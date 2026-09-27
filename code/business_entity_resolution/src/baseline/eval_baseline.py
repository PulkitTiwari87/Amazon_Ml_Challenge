"""Cheap post-hoc measurement over already-written baseline outputs (no rerun of the
merge). Computes exactly the numbers requested: candidate recall, singleton false-merge
rate, non-singleton miss rate, and candidate-set-size distribution. Every number here is
measured from the files on disk; nothing is estimated or assumed.

Usage: python -m src.baseline.eval_baseline --cand ../../artifacts/p3/candidate_pairs.tsv
                                             --match ../../artifacts/p3/matching_results.tsv
                                             --gt <train_ground_truth.tsv>
"""
import argparse
import csv
import sys

import numpy as np


def read_id_lists(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            s1, _, rest = line.rstrip("\n").partition("\t")
            out[s1] = rest.split(",") if rest else []
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cand", required=True)
    ap.add_argument("--match", required=True)
    ap.add_argument("--gt", required=True)
    a = ap.parse_args(argv)

    print("reading ground truth...", file=sys.stderr)
    gt = read_id_lists(a.gt)
    print("reading candidates...", file=sys.stderr)
    cand = read_id_lists(a.cand)
    print("reading matches...", file=sys.stderr)
    match = read_id_lists(a.match)

    n_entities = len(gt)
    true_match_total = 0
    true_match_in_cand = 0
    singletons = 0
    singleton_false_merge = 0
    nonsingleton = 0
    nonsingleton_miss = 0
    cand_sizes = []
    for s1, true_ids in gt.items():
        true_set = set(true_ids) if true_ids and true_ids != [""] else set()
        c = cand.get(s1, [])
        cand_sizes.append(len(c))
        c_set = set(c)
        m_set = set(match.get(s1, []))
        if true_set:
            nonsingleton += 1
            true_match_total += len(true_set)
            true_match_in_cand += len(true_set & c_set)
            if not m_set:
                nonsingleton_miss += 1
        else:
            singletons += 1
            if m_set:
                singleton_false_merge += 1

    cand_sizes = np.array(cand_sizes)
    print(f"entities={n_entities:,} singletons={singletons:,} ({singletons/n_entities:.3%}) "
          f"nonsingleton={nonsingleton:,} ({nonsingleton/n_entities:.3%})")
    print(f"candidate recall = {true_match_in_cand:,} / {true_match_total:,} = "
          f"{true_match_in_cand/true_match_total:.4%}  <-- ceiling on achievable F0.5 given this blocking")
    print(f"singleton false-merge rate (true singleton, predicted >=1 match) = "
          f"{singleton_false_merge:,} / {singletons:,} = {singleton_false_merge/singletons:.4%}")
    print(f"non-singleton miss rate (true match exists, predicted empty) = "
          f"{nonsingleton_miss:,} / {nonsingleton:,} = {nonsingleton_miss/nonsingleton:.4%}")
    print(f"candidates/S1: mean={cand_sizes.mean():.2f} median={np.median(cand_sizes):.0f} "
          f"p95={np.percentile(cand_sizes,95):.0f} max={cand_sizes.max()}")


if __name__ == "__main__":
    main()
