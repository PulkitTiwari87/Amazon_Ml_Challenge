"""P1-002, P1-004 (vs truth), P1-006, P1-007: ground-truth structure of the training set.

Consumes the .npz row arrays written by profile.py (ids, country codes, record hashes in
file order). Nothing here re-parses the big source files.
"""
import csv
import time

import numpy as np
import pandas as pd

from .config import CHUNK_ROWS, GT_COLS
from .text_utils import parse_ids

CARD_CAP = 25


class IdIndex:
    """Exact lookup id -> file position using a sorted copy (no Python dicts at 5M scale)."""

    def __init__(self, ids: np.ndarray):
        self.order = np.argsort(ids, kind="stable")
        self.sorted = ids[self.order]

    def pos(self, q: np.ndarray) -> np.ndarray:
        i = np.searchsorted(self.sorted, q)
        i = np.minimum(i, len(self.sorted) - 1)
        hit = self.sorted[i] == q
        return np.where(hit, self.order[i], -1)


def load_npz(path):
    z = np.load(path, allow_pickle=True)
    return {k: z[k] for k in z.files}


def parse_ground_truth(gt_path, chunk_rows=CHUNK_ROWS):
    """Parse the GT file into flat arrays. Every anomaly is counted, none is silently repaired
    (a repaired token is still counted in `anom`)."""
    anom = dict(rows=0, bad_s1_id=0, singleton=0, empty_token=0, token_ws=0, bad_token=0,
                s1_prefix_in_list=0, dup_in_list=0, other_prefix=0)
    s1_ids, owner_l, src_l, mid_l, list_len = [], [], [], [], []
    base = 0
    rd = pd.read_csv(gt_path, sep="\t", dtype=str, keep_default_na=False, na_filter=False,
                     quoting=csv.QUOTE_NONE, chunksize=chunk_rows, encoding="utf-8",
                     encoding_errors="replace", on_bad_lines="skip", usecols=GT_COLS)
    for ch in rd:
        n = len(ch)
        anom["rows"] += n
        ids, ok = parse_ids(ch["source1_entity_id"], "S1")
        anom["bad_s1_id"] += int((~ok).sum())
        s1_ids.append(ids)
        m = ch["matched_entity_ids"].reset_index(drop=True)
        single = (m == "").to_numpy()
        anom["singleton"] += int(single.sum())
        rows = np.flatnonzero(~single)
        ex = m.iloc[rows].str.split(",").explode()
        own = ex.index.to_numpy()
        tok = ex.reset_index(drop=True)
        empty = (tok == "").to_numpy()
        anom["empty_token"] += int(empty.sum())
        anom["token_ws"] += int((tok != tok.str.strip()).sum())
        t = tok.str.strip()
        v2 = t.str.fullmatch(r"S2-\d{1,18}").to_numpy()
        v3 = t.str.fullmatch(r"S3-\d{1,18}").to_numpy()
        anom["s1_prefix_in_list"] += int(t.str.startswith("S1-").sum())
        anom["bad_token"] += int((~(v2 | v3)).sum() - empty.sum())
        good = v2 | v3
        num = pd.to_numeric(t.str.slice(3).where(good, "-1")).to_numpy(dtype=np.int64)
        src = np.where(v2, 2, np.where(v3, 3, 0)).astype(np.int8)
        owner_l.append((own[good] + base).astype(np.int64))
        src_l.append(src[good])
        mid_l.append(num[good])
        base += n
    return {
        "s1_ids": np.concatenate(s1_ids), "owner": np.concatenate(owner_l),
        "src": np.concatenate(src_l), "mid": np.concatenate(mid_l), "anom": anom,
    }


def _hist(a, cap):
    return {int(k): int(v) for k, v in zip(*np.unique(np.minimum(a, cap), return_counts=True))}


def analyze_truth(gt, s1, s2, s3):
    """gt: parse_ground_truth output; s1/s2/s3: load_npz of the train source files."""
    t0 = time.perf_counter()
    out = {"anomalies": gt["anom"]}
    n_gt = len(gt["s1_ids"])
    # ---- P1-002 coverage / uniqueness
    idx1 = IdIndex(s1["ids"])
    gpos = idx1.pos(gt["s1_ids"])
    good_s1 = s1["ids"][s1["ids"] >= 0]
    out["s1_unique"] = {"rows": int(len(s1["ids"])), "unique_valid": int(np.unique(good_s1).size)}
    out["gt_vs_s1"] = {
        "gt_rows": n_gt, "gt_unique_ids": int(np.unique(gt["s1_ids"]).size),
        "gt_ids_not_in_s1": int((gpos < 0).sum()),
        "s1_ids_not_in_gt": int(np.setdiff1d(good_s1, gt["s1_ids"]).size),
        "same_row_order": bool(len(s1["ids"]) == n_gt and np.array_equal(s1["ids"], gt["s1_ids"])),
    }
    # ---- P1-006 cardinality
    n2 = np.bincount(gt["owner"][gt["src"] == 2], minlength=n_gt)
    n3 = np.bincount(gt["owner"][gt["src"] == 3], minlength=n_gt)
    tot = n2 + n3
    out["cardinality"] = {
        "entities": n_gt, "singletons": int((tot == 0).sum()),
        "singleton_frac": float((tot == 0).mean()), "one_match": int((tot == 1).sum()),
        "two_plus": int((tot >= 2).sum()), "max_matches": int(tot.max()), "mean_matches": float(tot.mean()),
        "mean_matches_nonsingleton": float(tot[tot > 0].mean()) if (tot > 0).any() else 0.0,
        "total_hist": _hist(tot, CARD_CAP), "s2_hist": _hist(n2, CARD_CAP), "s3_hist": _hist(n3, CARD_CAP),
        "percentiles_nonsingleton": {str(p): float(np.percentile(tot[tot > 0], p)) for p in (50, 90, 99, 99.9)}
        if (tot > 0).any() else {},
    }
    # ---- P1-007 by source
    both = (n2 > 0) & (n3 > 0)
    out["source_split"] = {
        "match_ids_s2": int((gt["src"] == 2).sum()), "match_ids_s3": int((gt["src"] == 3).sum()),
        "entities_s2_only": int(((n2 > 0) & (n3 == 0)).sum()),
        "entities_s3_only": int(((n3 > 0) & (n2 == 0)).sum()), "entities_both": int(both.sum()),
        "entities_none": int(((n2 == 0) & (n3 == 0)).sum()),
    }
    # ---- per-country cardinality (country of the S1 record)
    names = list(s1["country_codes"])
    cc1 = np.where(gpos >= 0, s1["ccode"][np.maximum(gpos, 0)], -1)
    out["by_country"] = {}
    for c, name in enumerate(names):
        mk = cc1 == c
        out["by_country"][name] = {
            "entities": int(mk.sum()), "singleton_frac": float((tot[mk] == 0).mean()) if mk.any() else None,
            "mean_matches": float(tot[mk].mean()) if mk.any() else None,
            "s2_only": int(((n2 > 0) & (n3 == 0))[mk].sum()), "s3_only": int(((n3 > 0) & (n2 == 0))[mk].sum()),
            "both": int(both[mk].sum())}
    # ---- match-id integrity, many-to-one, orphans, country agreement
    out["match_integrity"] = {}
    owner_of = {}
    for src_no, arr in ((2, s2), (3, s3)):
        mk = gt["src"] == src_no
        mids, own = gt["mid"][mk], gt["owner"][mk]
        idx = IdIndex(arr["ids"])
        rpos = idx.pos(mids)
        u, cnt = np.unique(mids, return_counts=True)
        dup_in_list = int(len(mids) - len(np.unique(own.astype(np.int64) * (1 << 30) + mids % (1 << 30))))
        # per-record owner: an arbitrary claiming S1 entity (-1 = orphan)
        rec_owner = np.full(len(arr["ids"]), -1, dtype=np.int64)
        ok = rpos >= 0
        rec_owner[rpos[ok]] = own[ok]
        owner_of[src_no] = rec_owner
        rc = arr["ccode"]
        rnames = list(arr["country_codes"])
        e_country = np.array([names.index(rnames[c]) if rnames[c] in names else -2 for c in range(len(rnames))])
        agree = ok & (cc1[own] == e_country[rc[np.maximum(rpos, 0)]])
        out["match_integrity"][f"s{src_no}"] = {
            "match_tokens": int(mk.sum()), "ids_missing_from_source_file": int((~ok).sum()),
            "unique_match_ids": int(u.size), "ids_claimed_by_multiple_s1": int((cnt > 1).sum()),
            "max_claims_per_id": int(cnt.max()) if cnt.size else 0,
            "dup_tokens_within_list": dup_in_list,
            "source_file_rows": int(len(arr["ids"])), "orphan_records": int((rec_owner < 0).sum()),
            "orphan_frac": float((rec_owner < 0).mean()),
            "country_disagree_tokens": int((ok & ~agree).sum()),
            "orphan_by_country": {rnames[c]: int(((rec_owner < 0) & (rc == c)).sum()) for c in range(len(rnames))},
            "rows_by_country": {rnames[c]: int((rc == c).sum()) for c in range(len(rnames))},
        }
    # ---- P1-004 duplicates vs truth (are exact/normalised dups the same S1 entity's variants?)
    out["dup_vs_truth"] = {}
    for src_no, arr in ((2, s2), (3, s3)):
        for key in ("exact", "norm", "tokset"):
            out["dup_vs_truth"][f"s{src_no}_{key}"] = _dup_groups(arr[f"h_{key}"], owner_of[src_no])
    out["s1_dups"] = {key: _dup_groups(s1[f"h_{key}"], np.arange(len(s1["ids"]))) for key in ("exact", "norm", "tokset")}
    out["runtime_s"] = round(time.perf_counter() - t0, 1)
    aux = {"gpos": gpos, "n2": n2, "n3": n3, "tot": tot, "owner_of": owner_of}
    return out, aux


def _dup_groups(h, owner):
    """For hash groups of size>=2: does the group stay inside one S1 entity (owner) or not?"""
    u, inv, cnt = np.unique(h, return_inverse=True, return_counts=True)
    in_dup = cnt[inv] >= 2
    if not in_dup.any():
        return {"groups": 0}
    df = pd.DataFrame({"g": inv[in_dup], "o": owner[in_dup]})
    df["orph"] = df["o"] < 0
    ag = df.groupby("g").agg(n=("o", "size"), nown=("o", "nunique"), orph=("orph", "sum"))
    return {
        "groups": int(len(ag)), "records": int(ag["n"].sum()),
        "all_same_entity": int(((ag["nown"] == 1) & (ag["orph"] == 0)).sum()),
        "span_multiple_entities": int((ag["nown"] > 1).sum()),
        "all_orphan": int((ag["orph"] == ag["n"]).sum()),
        "mixed_matched_and_orphan": int(((ag["orph"] > 0) & (ag["orph"] < ag["n"])).sum()),
    }
