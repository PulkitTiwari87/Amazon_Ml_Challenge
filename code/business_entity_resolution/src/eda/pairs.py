"""P1-009: noise-pattern census.

Two views: (a) population-level regex counts live in profile.py; (b) this module: pair-level
census on a seeded random sample of matched (S1 record, matched record) pairs from the
training ground truth, plus a random-pair baseline so the numbers can be read as "how far
apart are true matches compared with chance".
"""
import sys
import time

import numpy as np
import pandas as pd

from .profile import read_chunks
from .text_utils import norm, pair_flags, parse_ids
from .config import SOURCE_COLS

BOOL_FLAGS = None  # filled lazily from the first pair


def fetch_records(path, source_no, wanted_sorted, chunk_rows=500_000):
    """Stream a source file and keep only rows whose numeric id is in `wanted_sorted`."""
    parts = []
    for ch in read_chunks(path, SOURCE_COLS, chunk_rows):
        ids, ok = parse_ids(ch["entity_id"], f"S{source_no}")
        keep = np.isin(ids, wanted_sorted) & ok
        if keep.any():
            d = ch[keep].copy()
            d["id"] = ids[keep]
            parts.append(d)
    if not parts:
        return pd.DataFrame(columns=SOURCE_COLS + ["id"])
    return pd.concat(parts, ignore_index=True)


def _flags_frame(a, b):
    """a, b: DataFrames with equal length holding S1 record and candidate record columns."""
    an, bn = norm(a["business_name"]), norm(b["business_name"])
    aa, ba = norm(a["business_address"]), norm(b["business_address"])
    rows = [pair_flags(x1, x2, y1, y2, n1, n2, m1, m2) for x1, x2, y1, y2, n1, n2, m1, m2 in zip(
        a["business_name"], b["business_name"], a["business_address"], b["business_address"],
        an, bn, aa, ba)]
    return pd.DataFrame(rows)


def _rates(df):
    out = {"n": int(len(df))}
    for c in df.columns:
        if df[c].dtype == bool:
            out[c] = float(df[c].mean())
    for c in ("name_sim", "addr_sim"):
        out[c + "_hist10"] = np.histogram(df[c], bins=np.linspace(0, 1, 11))[0].tolist()
        out[c + "_mean"] = float(df[c].mean())
    return out


def noise_census(gt, aux, paths, n_entities=50_000, n_negatives=40_000, seed=20260925, log=True):
    """paths: {1: train_source1 path, 2: ..., 3: ...}"""
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    cand = np.flatnonzero(aux["tot"] > 0)
    pick = np.sort(rng.choice(cand, size=min(n_entities, len(cand)), replace=False))
    msk = np.isin(gt["owner"], pick)
    owner, src, mid = gt["owner"][msk], gt["src"][msk], gt["mid"][msk]
    recs = {1: fetch_records(paths[1], 1, np.sort(gt["s1_ids"][pick]))}
    for k in (2, 3):
        recs[k] = fetch_records(paths[k], k, np.unique(mid[src == k]))
        if log:
            print(f"  pairs: fetched S{k} records ({len(recs[k]):,})", file=sys.stderr, flush=True)
    pairs = pd.DataFrame({"s1_id": gt["s1_ids"][owner], "src": src, "mid": mid})
    a = pairs.merge(recs[1].add_prefix("a_"), left_on="s1_id", right_on="a_id", how="left")
    frames = []
    for k in (2, 3):
        sub = a[a["src"] == k].merge(recs[k].add_prefix("b_"), left_on="mid", right_on="b_id", how="left")
        frames.append(sub)
    full = pd.concat(frames, ignore_index=True)
    missing = int(full["b_id"].isna().sum() + full["a_id"].isna().sum())
    full = full.dropna(subset=["b_id", "a_id"]).reset_index(drop=True)
    A = full[[c for c in full.columns if c.startswith("a_")]].rename(columns=lambda c: c[2:])
    B = full[[c for c in full.columns if c.startswith("b_")]].rename(columns=lambda c: c[2:])
    fl = _flags_frame(A, B)
    fl["match_src"] = full["src"].to_numpy()
    fl["country"] = A["country"].to_numpy()
    fl["country_agrees"] = (A["country"].to_numpy() == B["country"].to_numpy())
    out = {"sampled_entities": int(len(pick)), "pairs": int(len(fl)), "pairs_missing_records": missing,
           "overall": _rates(fl), "by_match_source": {}, "by_country": {}, "by_country_source": {}}
    for k, g in fl.groupby("match_src"):
        out["by_match_source"][f"S{k}"] = _rates(g)
    for c, g in fl.groupby("country"):
        out["by_country"][c] = _rates(g)
        for k, h in g.groupby("match_src"):
            out["by_country_source"][f"{c}|S{k}"] = _rates(h)
    nl = fl[fl["name_match_is_nonlatin"]]
    lt = fl[~fl["name_match_is_nonlatin"]]
    out["nonlatin_match_name"] = {"n": int(len(nl)), "both_token_overlap_zero": float(nl["both_token_overlap_zero"].mean()) if len(nl) else None,
                                  "addr_token_overlap_zero": float(nl["addr_token_overlap_zero"].mean()) if len(nl) else None}
    out["latin_match_name"] = {"n": int(len(lt)), "both_token_overlap_zero": float(lt["both_token_overlap_zero"].mean()) if len(lt) else None}
    # ---- random same-country, same-source negatives (chance baseline; NOT hard negatives)
    neg_idx = rng.choice(len(A), size=min(n_negatives, len(A)), replace=False)
    An, Bn = A.iloc[neg_idx].reset_index(drop=True), B.iloc[neg_idx].reset_index(drop=True)
    perm = np.arange(len(Bn))
    keys = (An["country"] + "|" + full["src"].iloc[neg_idx].astype(str).reset_index(drop=True)).to_numpy()
    for key in np.unique(keys):
        ix = np.flatnonzero(keys == key)
        perm[ix] = rng.permutation(ix)
    neg = _flags_frame(An, Bn.iloc[perm].reset_index(drop=True))
    out["random_negative_baseline"] = _rates(neg)
    out["runtime_s"] = round(time.perf_counter() - t0, 1)
    return out
