"""Phase 3 baseline (P3-001/002/003), built under a hard 2-hour deadline: precision-first
blocking + matching that runs end to end on the real train or test set.

Design (deliberately simple, chosen for speed and precision under the F0.5(beta=0.5)
metric, which penalises false merges twice as hard as misses):

  name_key   = sorted, legal-suffix-canonicalised tokens of the normalised business_name
               (case/punctuation-insensitive, word-order-insensitive)
  match_key  = name_key + the literal (open-set) country string

  candidate_pairs: S1 x (S2 union S3) rows sharing the same name_key.
  matching_results: the subset of those candidate rows that also share country exactly
                     (country is compared as whatever string is present -> open-set safe,
                     never hard-coded to {US, India}, so France/any unseen country still
                     gets a country-equality check, never a closed-set filter).

  Any name_key shared by more than MAX_GROUP source records is dropped entirely from both
  files (treated as an unblockable generic name) instead of exploding candidate volume /
  runtime, and because a very generic shared name is exactly the situation where a name-only
  rule is least trustworthy (AP-2: default to no-match under uncertainty).

  Every test S1 entity gets exactly one output row; entities with no surviving candidates
  get an empty match list (singleton decision) -- this is intentional, not a bug, since
  correctly predicting an empty list on a true singleton scores 1.0 and a wrong match on
  a true singleton scores 0.0.

Usage:
    python -m src.baseline.run_baseline --split test --out ../../output
    python -m src.baseline.run_baseline --split train --out ../../artifacts/p3 --score
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "code" / "business_entity_resolution"))
from src.eda import config as C
from src.eda.text_utils import norm, canon_tokens
from src.eval.f05_metric import macro_f05

MAX_GROUP = 400  # a key shared by more source-side records than this is dropped (AP-2)
CHUNK = 300_000


def _key_series(text: pd.Series) -> pd.Series:
    n = norm(text)
    return pd.Series([" ".join(sorted(canon_tokens(x))) for x in n], index=text.index)


def load_reduced(name: str, split_files, log=True):
    """Stream one source file, keep only entity_id / name_key / addr_key / country (drop the
    raw name/address once both keys are computed, to hold peak memory down)."""
    path, prefix = split_files[name]
    parts = []
    t0 = time.perf_counter()
    for ch in pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_filter=False,
                          quoting=csv.QUOTE_NONE, chunksize=CHUNK, encoding="utf-8",
                          encoding_errors="replace", on_bad_lines="skip", usecols=C.SOURCE_COLS):
        name_key = _key_series(ch["business_name"])
        addr_key = _key_series(ch["business_address"])
        parts.append(pd.DataFrame({"id": ch["entity_id"].to_numpy(), "name_key": name_key.to_numpy(),
                                    "addr_key": addr_key.to_numpy(), "country": ch["country"].to_numpy()}))
    df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["id", "name_key", "addr_key", "country"])
    df["src"] = prefix
    if log:
        print(f"  loaded {name}: {len(df):,} rows in {time.perf_counter()-t0:.0f}s", file=sys.stderr, flush=True)
    return df


def _drop_generic(s1, other, key_col, min_len=1):
    """Cap block size on a key column: a key shared by >MAX_GROUP source-side records, or an
    empty/too-short key (e.g. missing address -> would block everything with a missing
    address together), never participates in that blocking view."""
    valid = other[key_col].str.split().str.len().fillna(0) >= min_len
    counts = other.loc[valid, key_col].value_counts()
    bad = set(counts[counts > MAX_GROUP].index) | set(other.loc[~valid, key_col].unique())
    s1_counts = s1[key_col].value_counts()
    bad |= set(s1_counts[s1_counts > MAX_GROUP].index)
    return bad


def build(split: str, data_root=None, address_mode="none"):
    """address_mode:
      none - EXP-001 behaviour: name_key blocking only; match = candidates with country equal.
      or   - candidates = union(name_key match, addr_key match); match = country equal AND
             (name_key equal OR addr_key equal)  [more recall, same or looser precision than 'and']
      and  - same candidates; match = country equal AND name_key equal AND addr_key equal
             [strict, precision-first: rejects same-name-different-address false merges]
    """
    data_root = Path(data_root or C.DATA_ROOT)
    files = {
        "s1": (data_root / split / f"{split}_source1.tsv", "S1"),
        "s2": (data_root / split / f"{split}_source2.tsv", "S2"),
        "s3": (data_root / split / f"{split}_source3.tsv", "S3"),
    }
    s1 = load_reduced("s1", files)
    s2 = load_reduced("s2", files)
    s3 = load_reduced("s3", files)
    other = pd.concat([s2, s3], ignore_index=True)

    bad_name = _drop_generic(s1, other, "name_key")
    print(f"  dropped {len(bad_name)} generic/empty name_keys (> {MAX_GROUP} records or empty)", file=sys.stderr)
    name_cand = s1.loc[~s1["name_key"].isin(bad_name), ["id", "name_key", "addr_key", "country"]].merge(
        other.loc[~other["name_key"].isin(bad_name), ["id", "name_key", "addr_key", "country", "src"]],
        on="name_key", suffixes=("_s1", "_o"))
    name_cand = name_cand.rename(columns={"id_s1": "s1_id", "id_o": "other_id"})
    # `name_key` was the join column, so pandas leaves it singular (unsuffixed) even though it
    # came from both sides -- duplicate it explicitly so every candidate frame has the same
    # four key columns regardless of which blocking view produced the row.
    name_cand["name_key_s1"] = name_cand["name_key"]
    name_cand["name_key_o"] = name_cand["name_key"]

    if address_mode == "none":
        cand = name_cand.copy()
        cand["via_name"], cand["via_addr"] = True, False
    else:
        bad_addr = _drop_generic(s1, other, "addr_key", min_len=2)  # require >=2 tokens: a
        # 1-token address (or empty) is too weak/common a key to block on safely
        print(f"  dropped {len(bad_addr)} generic/empty/short addr_keys (> {MAX_GROUP} records or <2 tokens)",
              file=sys.stderr)
        addr_cand = s1.loc[~s1["addr_key"].isin(bad_addr), ["id", "name_key", "addr_key", "country"]].merge(
            other.loc[~other["addr_key"].isin(bad_addr), ["id", "name_key", "addr_key", "country", "src"]],
            on="addr_key", suffixes=("_s1", "_o"))
        addr_cand = addr_cand.rename(columns={"id_s1": "s1_id", "id_o": "other_id"})
        addr_cand["addr_key_s1"] = addr_cand["addr_key"]
        addr_cand["addr_key_o"] = addr_cand["addr_key"]
        name_cand["via_name"], name_cand["via_addr"] = True, False
        addr_cand["via_name"], addr_cand["via_addr"] = False, True
        key_cols = ["s1_id", "other_id", "name_key_s1", "name_key_o", "addr_key_s1", "addr_key_o",
                    "country_s1", "country_o", "src", "via_name", "via_addr"]
        cand = pd.concat([name_cand.reindex(columns=key_cols), addr_cand.reindex(columns=key_cols)],
                         ignore_index=True)
        cand = cand.groupby(["s1_id", "other_id"], as_index=False).agg(
            {**{c: "first" for c in key_cols if c not in ("s1_id", "other_id", "via_name", "via_addr")},
             "via_name": "max", "via_addr": "max"})

    name_eq = cand["name_key_s1"] == cand["name_key_o"]
    addr_eq = cand["addr_key_s1"] == cand["addr_key_o"]
    country_eq = cand["country_s1"] == cand["country_o"]
    if address_mode == "and":
        match = cand[country_eq & name_eq & addr_eq]
    elif address_mode == "or":
        match = cand[country_eq & (name_eq | addr_eq)]
    else:
        match = cand[country_eq]
    return s1, cand, match


def to_lists(df, id_col="s1_id", other_col="other_id"):
    g = df.groupby(id_col)[other_col].agg(lambda s: sorted(set(s)))
    return g


def write_output(all_s1_ids, lists_by_id, path, header):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(header) + "\n")
        for sid in all_s1_ids:
            ids = lists_by_id.get(sid, [])
            f.write(f"{sid}\t{','.join(ids)}\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["train", "test"], default="test")
    ap.add_argument("--data-root", default=str(C.DATA_ROOT))
    ap.add_argument("--out", default=str(C.PROJECT_ROOT / "output"))
    ap.add_argument("--address-mode", choices=["none", "or", "and"], default="none")
    ap.add_argument("--score", action="store_true", help="train split only: compute holdout-free "
                     "sanity F0.5 against train_ground_truth (NOT a leakage-safe holdout, just a "
                     "quick check that the pipeline is directionally sane)")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()

    s1, cand, match = build(a.split, a.data_root, a.address_mode)
    cand_lists = to_lists(cand)
    match_lists = to_lists(match)
    all_ids = s1["id"].tolist()

    write_output(all_ids, cand_lists, out / "candidate_pairs.tsv",
                 ["source1_entity_id", "candidate_entity_ids"])
    write_output(all_ids, match_lists, out / "matching_results.tsv",
                 ["source1_entity_id", "matched_entity_ids"])
    n_matched = sum(1 for sid in all_ids if len(match_lists.get(sid, [])) > 0)
    print(f"{a.split}: {len(all_ids):,} S1 entities, {n_matched:,} with >=1 match "
          f"({n_matched/len(all_ids):.3%}), runtime {time.perf_counter()-t0:.0f}s", file=sys.stderr)

    if a.score and a.split == "train":
        gt_path = Path(a.data_root) / "train" / "train_ground_truth.tsv"
        gt = pd.read_csv(gt_path, sep="\t", dtype=str, keep_default_na=False, na_filter=False,
                         quoting=csv.QUOTE_NONE, encoding="utf-8", encoding_errors="replace")
        true_map = {r.source1_entity_id: (set(r.matched_entity_ids.split(",")) if r.matched_entity_ids else set())
                    for r in gt.itertuples()}
        pred_map = {sid: set(match_lists.get(sid, [])) for sid in all_ids}
        score = macro_f05(true_map, pred_map)
        print(f"SANITY macro F0.5 on full train (not a real holdout, no leakage control): {score:.4f}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
