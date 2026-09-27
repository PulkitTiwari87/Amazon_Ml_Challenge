"""P1-011: leakage-candidate audit. Looks for anything that predicts match / singleton /
orphan status WITHOUT name or address similarity: ID values, ID length, file row order,
train<->test overlap. An AUC near 0.5 and a spearman near 0 mean "no exploitable signal".
"""
import time

import numpy as np
from scipy import stats

from .truth import IdIndex


def auc(score: np.ndarray, positive: np.ndarray) -> float:
    """Mann-Whitney AUC of `score` for `positive` (ties handled by mid-ranks)."""
    n1 = int(positive.sum())
    n0 = len(score) - n1
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = stats.rankdata(score)
    return float((r[positive].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def _deciles(values, flag):
    """flag rate within each decile of `values` (rank based)."""
    q = np.minimum((stats.rankdata(values) - 1) * 10 // len(values), 9).astype(int)
    return [float(flag[q == d].mean()) if (q == d).any() else None for d in range(10)]


def _digits(x):
    return np.floor(np.log10(np.maximum(x, 1))).astype(int) + 1


def leakage_audit(gt, aux, s1, s2, s3, tests, seed=20260925):
    """tests: {1: npz, 2: npz, 3: npz} for the test files (may be empty -> overlap skipped)."""
    t0 = time.perf_counter()
    rng = np.random.default_rng(seed)
    out = {"pair_relations": {}, "orphan_predictability": {}, "singleton_predictability": {}}
    srcs = {2: s2, 3: s3}
    for k, arr in srcs.items():
        mk = gt["src"] == k
        own, mid = gt["owner"][mk], gt["mid"][mk]
        rpos = IdIndex(arr["ids"]).pos(mid)
        ok = rpos >= 0
        own, mid, rpos = own[ok], mid[ok], rpos[ok]
        s1_pos = aux["gpos"][own]
        s1_id = gt["s1_ids"][own]
        n = len(own)
        take = rng.choice(n, size=min(n, 1_000_000), replace=False)
        perm = rng.permutation(len(take))
        f = lambda a: a[take]
        rel1 = f(s1_pos) / len(s1["ids"])
        rel2 = f(rpos) / len(arr["ids"])
        d = {
            "pairs_used": int(len(take)),
            "spearman_id": float(stats.spearmanr(f(s1_id), f(mid)).statistic),
            "spearman_file_position": float(stats.spearmanr(rel1, rel2).statistic),
            "median_abs_rel_position_gap": float(np.median(np.abs(rel1 - rel2))),
            "median_abs_rel_position_gap_shuffled": float(np.median(np.abs(rel1 - rel2[perm]))),
            "frac_abs_id_diff_lt_1e6": float((np.abs(f(s1_id) - f(mid)) < 1e6).mean()),
            "frac_abs_id_diff_lt_1e6_shuffled": float((np.abs(f(s1_id) - f(mid)[perm]) < 1e6).mean()),
            "frac_same_digit_length": float((_digits(f(s1_id)) == _digits(f(mid))).mean()),
            "frac_same_digit_length_shuffled": float((_digits(f(s1_id)) == _digits(f(mid)[perm])).mean()),
        }
        out["pair_relations"][f"S1-S{k}"] = d
        orphan = aux["owner_of"][k] < 0
        pos_rel = np.arange(len(arr["ids"])) / len(arr["ids"])
        out["orphan_predictability"][f"S{k}"] = {
            "orphan_frac": float(orphan.mean()),
            "auc_id_value": auc(arr["ids"].astype(float), orphan),
            "auc_id_digit_length": auc(_digits(arr["ids"]).astype(float), orphan),
            "auc_file_position": auc(pos_rel, orphan),
            "orphan_frac_by_id_decile": _deciles(arr["ids"], orphan),
            "orphan_frac_by_position_decile": _deciles(pos_rel, orphan),
        }
    single = aux["tot"] == 0
    pos_rel = np.arange(len(single)) / len(single)
    out["singleton_predictability"] = {
        "singleton_frac": float(single.mean()),
        "auc_s1_id_value": auc(gt["s1_ids"].astype(float), single),
        "auc_s1_id_digit_length": auc(_digits(gt["s1_ids"]).astype(float), single),
        "auc_gt_row_position": auc(pos_rel, single),
        "singleton_frac_by_id_decile": _deciles(gt["s1_ids"], single),
        "singleton_frac_by_position_decile": _deciles(pos_rel, single),
    }
    out["train_test_overlap"] = {}
    for k, tr in ((1, s1), (2, s2), (3, s3)):
        te = tests.get(k)
        if te is None:
            continue
        g_tr, g_te = tr["ids"][tr["ids"] >= 0], te["ids"][te["ids"] >= 0]
        out["train_test_overlap"][f"S{k}"] = {
            "train_rows": int(len(tr["ids"])), "test_rows": int(len(te["ids"])),
            "shared_ids": int(np.intersect1d(g_tr, g_te).size),
            "shared_exact_records": int(np.intersect1d(np.unique(tr["h_exact"]), np.unique(te["h_exact"])).size),
            "shared_normalised_records": int(np.intersect1d(np.unique(tr["h_norm"]), np.unique(te["h_norm"])).size),
            "test_records_with_normalised_twin_in_train": int(np.isin(te["h_norm"], tr["h_norm"]).sum()),
        }
    out["runtime_s"] = round(time.perf_counter() - t0, 1)
    return out
