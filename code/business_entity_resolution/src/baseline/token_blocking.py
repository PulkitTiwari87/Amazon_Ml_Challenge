"""EXP-003+: rare-token (inverted-index) blocking + name/address Jaccard scoring.

Hypothesis (from EXP-001/002 error analysis): full-canonical-key equality is too strict a
blocking condition -- most of the 69% candidate-recall loss is true matches whose names
differ by a token our abbreviation map doesn't cover, a typo, or reordering beyond simple
sorting. Blocking on "at least one shared, sufficiently rare name token" should recover much
of that recall, at the cost of a larger (and noisier) candidate set that then needs a real
similarity score + tuned threshold instead of exact-equality matching (F0.5 is precision-
heavy, so the threshold matters more than for a recall metric).

Pipeline:
  1. tokenize normalized+canonicalised name (and, separately, address) per record
  2. drop stopword-like / high document-frequency tokens (P1-009-style generic terms;
     "trading", "pvt", "the", street-type words, etc.) from being usable blocking keys --
     otherwise one common token creates a huge, useless candidate bucket (AP-2, section 8/20
     of the optimization brief)
  3. candidates = S1 x other rows sharing >=1 surviving name token (name-token blocking)
  4. per candidate pair: name Jaccard (token sets) and address Jaccard (token sets) -- NOT
     just of the shared tokens, of the FULL sets, so it is a real similarity in [0,1]
  5. match decision = country_eq AND score >= threshold, where score is swept on train
     against the exact competition macro F0.5 (never a proxy), see `sweep_threshold`.

Every number this module prints is measured from the split it is run on; nothing here is
assumed or estimated.
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
from src.eda.text_utils import norm, canon_tokens, CANON
from src.eval.f05_metric import macro_f05

CHUNK = 300_000
MAX_TOKEN_DF = 250       # a token appearing on more than this many records on EITHER side is
                          # dropped as a blocking key (pathological/generic token, section 20).
                          # Measured history on a 200k-row (9%) S1 train sample:
                          #   400, other-side only  -> 11M pairs, OOM'd (~460MB free), killed
                          #   50, both sides        -> recall 12.4% / F0.5 0.145 (WORSE than
                          #                            the 31.1%/0.399 exact-key baseline --
                          #                            too strict, suppresses ordinary
                          #                            discriminating industry words)
                          # 250 is the next measured point, not a final answer.
MIN_TOKEN_LEN = 3
# Generic terms that must never block on their own: legal-form / street-type canonical forms
# (values of CANON, e.g. "limited", "road") plus a short hand-picked list of very common,
# low-information English/business words seen across the corpus.
STOPWORDS = set(CANON.values()) | {
    "and", "the", "of", "for", "a", "an", "no", "near", "opposite", "floor", "unit", "block",
    "phase", "sector", "building", "tower", "complex", "house", "plot", "city", "town",
    "village", "district", "state", "post", "office", "main", "new", "old",
}


def _tokset(text: pd.Series) -> pd.Series:
    n = norm(text)
    return pd.Series([frozenset(t for t in canon_tokens(x) if len(t) >= MIN_TOKEN_LEN and t not in STOPWORDS)
                      for x in n], index=text.index)


def load_reduced(name: str, split_files, log=True):
    path, prefix = split_files[name]
    parts = []
    t0 = time.perf_counter()
    for ch in pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_filter=False,
                          quoting=csv.QUOTE_NONE, chunksize=CHUNK, encoding="utf-8",
                          encoding_errors="replace", on_bad_lines="skip", usecols=C.SOURCE_COLS):
        name_tok = _tokset(ch["business_name"])
        addr_tok = _tokset(ch["business_address"])
        parts.append(pd.DataFrame({"id": ch["entity_id"].to_numpy(), "name_tok": name_tok.to_numpy(),
                                    "addr_tok": addr_tok.to_numpy(), "country": ch["country"].to_numpy()}))
    df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["id", "name_tok", "addr_tok", "country"])
    df["src"] = prefix
    if log:
        print(f"  loaded {name}: {len(df):,} rows in {time.perf_counter()-t0:.0f}s", file=sys.stderr, flush=True)
    return df


def _explode(df, col):
    """id -> one row per token in df[col] (a frozenset)."""
    lens = df[col].apply(len)
    rep = np.repeat(df["id"].to_numpy(), lens.to_numpy())
    toks = np.fromiter((t for s in df[col] for t in s), dtype=object, count=int(lens.sum()))
    return pd.DataFrame({"id": rep, "token": toks})


def build_token_candidates(s1, other, sample_s1=None, seed=20260925, log=True):
    """Returns (cand, s1_used) where cand has s1_id/other_id/src/country_s1/country_o/
    name_jac/addr_jac/shared_name_tokens."""
    t0 = time.perf_counter()
    if sample_s1:
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(s1), size=min(sample_s1, len(s1)), replace=False)
        s1 = s1.iloc[np.sort(idx)].reset_index(drop=True)

    s1_ex = _explode(s1, "name_tok")
    other_ex = _explode(other, "name_tok")
    df_other = other_ex["token"].value_counts()
    df_s1 = s1_ex["token"].value_counts()
    # cap BOTH sides: a token common on either side can still blow up pairs_for_token =
    # s1_count * other_count even if the other side alone looks capped (section 20/24).
    good = set(df_other[df_other <= MAX_TOKEN_DF].index) & set(df_s1[df_s1 <= MAX_TOKEN_DF].index)
    if log:
        print(f"  name-token vocab: {len(set(df_other.index)|set(df_s1.index)):,} tokens; {len(good):,} usable "
              f"(<= {MAX_TOKEN_DF} records on BOTH sides)", file=sys.stderr)
    s1_ex = s1_ex[s1_ex["token"].isin(good)]
    other_ex = other_ex[other_ex["token"].isin(good)]

    country_s1 = s1.set_index("id")["country"]
    country_o = other.set_index("id")["country"]
    s1_ex = s1_ex.merge(s1[["id", "country"]], on="id")
    other_ex = other_ex.merge(other[["id", "country"]], on="id")

    pairs = s1_ex.merge(other_ex, on=["token", "country"])  # country_eq enforced in the join
    # itself (true matches share a country by construction; this is a big speed/memory win --
    # measured to matter at this scale, see the killed 460MB-free run above)
    pairs = pairs.rename(columns={"id_x": "s1_id", "id_y": "other_id"})
    shared = pairs.groupby(["s1_id", "other_id"], as_index=False).size().rename(columns={"size": "shared_name_tokens"})
    if log:
        print(f"  {len(shared):,} distinct (s1,other) pairs share >=1 usable name token AND country "
              f"({time.perf_counter()-t0:.0f}s)", file=sys.stderr)

    n_name_s1 = s1.set_index("id")["name_tok"].apply(len)
    n_name_o = other.set_index("id")["name_tok"].apply(len)
    addr_s1 = s1.set_index("id")["addr_tok"]
    addr_o = other.set_index("id")["addr_tok"]

    shared["n_name_s1"] = shared["s1_id"].map(n_name_s1).to_numpy()
    shared["n_name_o"] = shared["other_id"].map(n_name_o).to_numpy()
    shared["name_jac"] = shared["shared_name_tokens"] / (shared["n_name_s1"] + shared["n_name_o"] - shared["shared_name_tokens"])
    shared["country_s1"] = shared["s1_id"].map(country_s1).to_numpy()
    shared["country_o"] = shared["other_id"].map(country_o).to_numpy()

    # address Jaccard computed only for these already name+country-blocked pairs (much smaller
    # than the full cross product), via a direct per-row set intersection.
    a1 = shared["s1_id"].map(addr_s1)
    a2 = shared["other_id"].map(addr_o)
    inter = np.fromiter((len(x & y) for x, y in zip(a1, a2)), dtype=np.int32, count=len(shared))
    na1 = a1.apply(len).to_numpy()
    na2 = a2.apply(len).to_numpy()
    union = na1 + na2 - inter
    shared["addr_jac"] = np.where(union > 0, inter / np.maximum(union, 1), 0.0)
    if log:
        print(f"  features computed ({time.perf_counter()-t0:.0f}s total)", file=sys.stderr)
    return shared, s1


def sweep_threshold(cand, gt_true_map, all_s1_ids, weight_name=0.6, weight_addr=0.4, thresholds=None):
    """score = weight_name*name_jac + weight_addr*addr_jac, evaluated only on country-agreeing
    pairs. Sweeps `thresholds` and reports macro F0.5 for each (measured, not assumed)."""
    thresholds = thresholds or [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    same_country = cand[cand["country_s1"] == cand["country_o"]].copy()
    same_country["score"] = weight_name * same_country["name_jac"] + weight_addr * same_country["addr_jac"]
    results = []
    for th in thresholds:
        m = same_country[same_country["score"] >= th]
        pred_lists = m.groupby("s1_id")["other_id"].agg(lambda s: set(s))
        pred_map = {sid: pred_lists.get(sid, set()) for sid in all_s1_ids}
        score = macro_f05(gt_true_map, pred_map)
        n_matched = sum(1 for v in pred_map.values() if v)
        results.append((th, score, n_matched))
        print(f"    threshold={th:.2f}  macro_F0.5={score:.4f}  matched={n_matched:,}/{len(all_s1_ids):,}",
              file=sys.stderr)
    return results


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["train", "test"], default="train")
    ap.add_argument("--data-root", default=str(C.DATA_ROOT))
    ap.add_argument("--sample-s1", type=int, default=None, help="fast-iteration mode: only "
                     "this many S1 rows (random, but ALL of S2/S3 loaded so recall is exact "
                     "for the sampled rows)")
    ap.add_argument("--sweep", action="store_true")
    a = ap.parse_args(argv)

    data_root = Path(a.data_root)
    files = {
        "s1": (data_root / a.split / f"{a.split}_source1.tsv", "S1"),
        "s2": (data_root / a.split / f"{a.split}_source2.tsv", "S2"),
        "s3": (data_root / a.split / f"{a.split}_source3.tsv", "S3"),
    }
    s1 = load_reduced("s1", files)
    s2 = load_reduced("s2", files)
    s3 = load_reduced("s3", files)
    other = pd.concat([s2, s3], ignore_index=True)

    cand, s1_used = build_token_candidates(s1, other, sample_s1=a.sample_s1)
    all_ids = s1_used["id"].tolist()

    # candidate recall @ this blocking (before any threshold): fraction of true matches that
    # appear anywhere in `cand` regardless of score.
    if a.split == "train":
        gt_path = data_root / "train" / "train_ground_truth.tsv"
        gt = pd.read_csv(gt_path, sep="\t", dtype=str, keep_default_na=False, na_filter=False,
                         quoting=csv.QUOTE_NONE, encoding="utf-8", encoding_errors="replace")
        gt = gt[gt["source1_entity_id"].isin(set(all_ids))]
        true_map = {r.source1_entity_id: (set(r.matched_entity_ids.split(",")) if r.matched_entity_ids else set())
                    for r in gt.itertuples()}
        cand_sets = cand.groupby("s1_id")["other_id"].agg(lambda s: set(s))
        tot_true = sum(len(v) for v in true_map.values())
        tot_in_cand = sum(len(v & cand_sets.get(k, set())) for k, v in true_map.items())
        print(f"CANDIDATE RECALL (token blocking, no threshold applied yet) = {tot_in_cand:,} / {tot_true:,} "
              f"= {tot_in_cand/tot_true:.4%}", file=sys.stderr)
        sizes = cand.groupby("s1_id").size()
        sizes = sizes.reindex(all_ids, fill_value=0)
        print(f"candidates/S1 (this blocking): mean={sizes.mean():.2f} median={sizes.median():.0f} "
              f"p95={np.percentile(sizes,95):.0f} max={sizes.max()}", file=sys.stderr)
        if a.sweep:
            print("  threshold sweep:", file=sys.stderr)
            sweep_threshold(cand, true_map, all_ids)


if __name__ == "__main__":
    main()
