"""P1-010: train vs test distribution comparison from the per-file profiles (no re-parse)."""
import numpy as np

MIN_ROWS = 1000  # a country must have this many rows in BOTH splits to be compared


def psi(p_counts, q_counts, eps=1e-6):
    """Population stability index of q (test) relative to p (train). <0.1 small, >0.25 large
    by the usual convention (a convention, not a rule from the challenge)."""
    p = np.asarray(p_counts, float)
    q = np.asarray(q_counts, float)
    p, q = p / max(p.sum(), 1), q / max(q.sum(), 1)
    p, q = np.maximum(p, eps), np.maximum(q, eps)
    return float(((q - p) * np.log(q / p)).sum())


def _rebin(counts, edges):
    c = np.asarray(counts)
    return [int(c[a:b].sum()) for a, b in zip(edges[:-1], edges[1:])]


def _quantile_edges(counts, k=10):
    c = np.cumsum(counts) / max(sum(counts), 1)
    return sorted({0, *[int(np.searchsorted(c, q / k)) + 1 for q in range(1, k)], len(counts)})


def compare(train_prof, test_prof):
    """train_prof/test_prof: profile_source outputs for the same source number."""
    out = {"rows": {"train": train_prof["rows"], "test": test_prof["rows"]},
           "country_share": {}, "psi": {}, "flag_shift_pp": {}, "empty_rate_shift_pp": {}}
    tr_c, te_c = train_prof["rows_by_country"], test_prof["rows_by_country"]
    for c in sorted(set(tr_c) | set(te_c)):
        out["country_share"][c] = {
            "train_rows": tr_c.get(c, 0), "test_rows": te_c.get(c, 0),
            "train_share": tr_c.get(c, 0) / max(train_prof["rows"], 1),
            "test_share": te_c.get(c, 0) / max(test_prof["rows"], 1)}
    for c in [c for c in tr_c if tr_c[c] >= MIN_ROWS and te_c.get(c, 0) >= MIN_ROWS]:
        for key in ("name_len", "addr_len", "name_tok", "addr_tok"):
            h_tr = train_prof["length_hist"][key][c]
            h_te = test_prof["length_hist"][key][c]
            e = _quantile_edges(h_tr)
            out["psi"][f"{c}|{key}"] = psi(_rebin(h_tr, e), _rebin(h_te, e))
        shifts = []
        for grp, flags in train_prof["flags"].items():
            for f, byc in flags.items():
                r_tr = byc.get(c, 0) / tr_c[c]
                r_te = test_prof["flags"].get(grp, {}).get(f, {}).get(c, 0) / te_c[c]
                shifts.append({"flag": f"{grp}.{f}", "train": r_tr, "test": r_te, "shift_pp": 100 * (r_te - r_tr)})
        shifts.sort(key=lambda d: -abs(d["shift_pp"]))
        out["flag_shift_pp"][c] = shifts
        out["empty_rate_shift_pp"][c] = {
            col: 100 * (test_prof["empty"][col].get(c, 0) / te_c[c] - train_prof["empty"][col].get(c, 0) / tr_c[c])
            for col in train_prof["empty"]}
    return out
