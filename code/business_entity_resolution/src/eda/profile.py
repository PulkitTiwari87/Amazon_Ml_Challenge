"""P1-002..P1-005, P1-008: single streaming pass over one source TSV (S1/S2/S3, train or test).

Output = JSON-serialisable metrics dict + an .npz of per-row arrays (in file order) that the
ground-truth / leakage analysis re-uses so the big files are parsed only once.
"""
import csv
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import psutil

from .config import CHUNK_ROWS, SOURCE_COLS
from .text_utils import (addr_flags, hygiene_flags, norm, parse_ids, script_flags, name_flags)

NAME_CAP, ADDR_CAP, TOK_CAP = 300, 500, 60
_SEP = "\x1f"


def read_chunks(path, cols, chunk_rows=CHUNK_ROWS, nrows=None):
    """Tab parse, no quote handling, no NA coercion: every cell stays the literal string."""
    return pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_filter=False,
                       quoting=csv.QUOTE_NONE, chunksize=chunk_rows, nrows=nrows,
                       encoding="utf-8", encoding_errors="replace", on_bad_lines="skip",
                       usecols=cols)


def _hash(s: pd.Series) -> np.ndarray:
    return pd.util.hash_pandas_object(s, index=False).to_numpy(dtype=np.uint64)


def _tokset(s: pd.Series) -> pd.Series:
    return pd.Series([" ".join(sorted(x.split())) for x in s], index=s.index)


def _hist_by_country(acc, key, lengths, country, cap):
    clipped = np.minimum(lengths.to_numpy(), cap)
    for c in country.unique():
        h = np.bincount(clipped[(country == c).to_numpy()], minlength=cap + 1)
        acc[key][c] = acc[key].get(c, np.zeros(cap + 1, dtype=np.int64)) + h


def profile_source(path, source_no, npz_path=None, chunk_rows=CHUNK_ROWS, nrows=None, log=True):
    t0 = time.perf_counter()
    proc = psutil.Process()
    peak = 0
    prefix = f"S{source_no}"
    m = {"path": str(path), "source": source_no, "rows": 0, "bad_id_rows": 0,
         "rows_by_country": defaultdict(int),
         "empty": defaultdict(lambda: defaultdict(int)),       # col -> country -> n
         "ws_only": defaultdict(lambda: defaultdict(int)),
         "flags": defaultdict(lambda: defaultdict(lambda: defaultdict(int))),  # group -> flag -> country
         "not_nfc": defaultdict(int), "id_digits_hist": defaultdict(int)}
    len_h = {"name_len": {}, "addr_len": {}, "name_tok": {}, "addr_tok": {}}
    ids_l, cc_l, he_l, hn_l, ht_l = [], [], [], [], []
    codes = {}
    for chunk in read_chunks(path, SOURCE_COLS, chunk_rows, nrows):
        n = len(chunk)
        m["rows"] += n
        ids, valid = parse_ids(chunk["entity_id"], prefix)
        m["bad_id_rows"] += int((~valid).sum())
        for d, c in zip(*np.unique(chunk["entity_id"].str.len().to_numpy(), return_counts=True)):
            m["id_digits_hist"][int(d)] += int(c)
        country = chunk["country"]
        for c, k in country.value_counts().items():
            m["rows_by_country"][c] += int(k)
        name, addr = chunk["business_name"], chunk["business_address"]
        for col, s in (("business_name", name), ("business_address", addr), ("country", country),
                       ("entity_id", chunk["entity_id"])):
            for c, k in (s == "").groupby(country).sum().items():
                m["empty"][col][c] += int(k)
            for c, k in (s.str.strip() == "").groupby(country).sum().items():
                m["ws_only"][col][c] += int(k)
        for grp, s, fl in (("name", name, name_flags(name)), ("addr", addr, addr_flags(addr)),
                           ("name_script", name, script_flags(name)),
                           ("addr_script", addr, script_flags(addr)),
                           ("name_hyg", name, hygiene_flags(name)),
                           ("addr_hyg", addr, hygiene_flags(addr))):
            for c, row in fl.groupby(country).sum().iterrows():
                for f, k in row.items():
                    m["flags"][grp][f][c] += int(k)
        m["not_nfc"]["name"] += int((name.str.normalize("NFC") != name).sum())
        m["not_nfc"]["addr"] += int((addr.str.normalize("NFC") != addr).sum())
        _hist_by_country(len_h, "name_len", name.str.len(), country, NAME_CAP)
        _hist_by_country(len_h, "addr_len", addr.str.len(), country, ADDR_CAP)
        _hist_by_country(len_h, "name_tok", name.str.split().str.len().fillna(0).astype(int), country, TOK_CAP)
        _hist_by_country(len_h, "addr_tok", addr.str.split().str.len().fillna(0).astype(int), country, TOK_CAP)
        nn, an = norm(name), norm(addr)
        ids_l.append(ids)
        cc_l.append(np.array([codes.setdefault(c, len(codes)) for c in country], dtype=np.int32))
        he_l.append(_hash(name + _SEP + addr + _SEP + country))
        hn_l.append(_hash(nn + _SEP + an + _SEP + country))
        ht_l.append(_hash(_tokset(nn) + _SEP + _tokset(an) + _SEP + country))
        peak = max(peak, proc.memory_info().rss)
        if log:
            print(f"  [{prefix}] {Path(path).name}: {m['rows']:,} rows  {time.perf_counter()-t0:.0f}s",
                  file=sys.stderr, flush=True)
    ids = np.concatenate(ids_l) if ids_l else np.zeros(0, np.int64)
    cc = np.concatenate(cc_l) if cc_l else np.zeros(0, np.int32)
    hashes = {"exact": np.concatenate(he_l), "norm": np.concatenate(hn_l), "tokset": np.concatenate(ht_l)} \
        if ids_l else {k: np.zeros(0, np.uint64) for k in ("exact", "norm", "tokset")}
    good = ids[ids >= 0]
    m["ids"] = {"valid": int(good.size), "unique": int(np.unique(good).size),
                "min": int(good.min()) if good.size else None, "max": int(good.max()) if good.size else None,
                "ascending_pair_frac": float((np.diff(ids) > 0).mean()) if ids.size > 1 else None}
    m["duplicates"] = {k: _dup_stats(h) for k, h in hashes.items()}
    m["length_hist"] = {k: {c: v.tolist() for c, v in d.items()} for k, d in len_h.items()}
    m["runtime_s"] = round(time.perf_counter() - t0, 1)
    m["peak_rss_mb"] = round(peak / 2**20)
    m["country_codes"] = [c for c, _ in sorted(codes.items(), key=lambda kv: kv[1])]
    m = _plain(m)
    if npz_path is not None:
        np.savez(npz_path, ids=ids, ccode=cc, country_codes=np.array(m["country_codes"], dtype=object),
                 **{f"h_{k}": v for k, v in hashes.items()})
    return m


def _dup_stats(h: np.ndarray):
    if h.size == 0:
        return {"groups": 0, "records_in_groups": 0, "max_group": 0, "size_hist": {}}
    _, cnt = np.unique(h, return_counts=True)
    dup = cnt[cnt >= 2]
    sizes, freq = np.unique(np.minimum(dup, 10), return_counts=True)
    return {"groups": int(dup.size), "records_in_groups": int(dup.sum()), "max_group": int(cnt.max()),
            "size_hist": {int(s): int(f) for s, f in zip(sizes, freq)}}


def _plain(x):
    if isinstance(x, dict):
        return {str(k): _plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_plain(v) for v in x]
    return x
