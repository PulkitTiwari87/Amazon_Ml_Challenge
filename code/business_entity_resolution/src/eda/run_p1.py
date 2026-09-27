"""Phase 1 orchestrator. Stages are restartable: each writes to the artifact dir and is skipped
if its output exists (use --force to redo). Run from code/business_entity_resolution:

    python -m src.eda.run_p1 --stage all
    python -m src.eda.run_p1 --stage raw|profile|truth|pairs|leakage|drift
    python -m src.eda.run_p1 --data-root <dir> --out <dir> --nrows 50000   # smoke / scale sample
"""
import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import psutil

from . import config as C


def _dump(obj, path):
    Path(path).write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _raw_one(args):
    from .rawscan import pandas_default_read_check, scan_tsv
    name, data_root, do_default = args
    sno = C.FILES[name][2]
    cols = C.SOURCE_COLS if sno else C.GT_COLS
    r = scan_tsv(C.path_of(name, data_root), cols, f"S{sno}" if sno else "S1")
    if do_default:
        r["default_read"] = pandas_default_read_check(C.path_of(name, data_root), cols)
    return name, r


def _profile_one(args):
    from .profile import profile_source
    name, data_root, out, nrows = args
    m = profile_source(C.path_of(name, data_root), C.FILES[name][2], Path(out) / f"rows_{name}.npz", nrows=nrows)
    return name, m


def _load_truth(out, data_root):
    from .truth import analyze_truth, load_npz, parse_ground_truth
    s = {k: load_npz(Path(out) / f"rows_train_source{k}.npz") for k in (1, 2, 3)}
    gt = parse_ground_truth(C.path_of("train_ground_truth", data_root))
    res, aux = analyze_truth(gt, s[1], s[2], s[3])
    return gt, res, aux, s


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    ap.add_argument("--data-root", default=str(C.DATA_ROOT))
    ap.add_argument("--out", default=str(C.ARTIFACT_DIR))
    ap.add_argument("--nrows", type=int, default=None, help="profile only the first N rows per file")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--n-entities", type=int, default=50_000)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stages = ["raw", "profile", "truth", "pairs", "leakage", "drift"] if a.stage == "all" else [a.stage]
    src_names = [n for n in C.FILES if C.FILES[n][2]]
    t_all = time.perf_counter()

    def need(f):
        return a.force or not (out / f).exists()

    if "raw" in stages and need("rawscan.json"):
        t = time.perf_counter()
        with ProcessPoolExecutor(a.workers) as ex:
            res = dict(ex.map(_raw_one, [(n, a.data_root, a.nrows is None) for n in C.FILES]))
        res["_runtime_s"] = round(time.perf_counter() - t, 1)
        _dump(res, out / "rawscan.json")
        print(f"raw done {res['_runtime_s']}s", file=sys.stderr)
    if "profile" in stages and need("profiles.json"):
        t = time.perf_counter()
        with ProcessPoolExecutor(a.workers) as ex:
            res = dict(ex.map(_profile_one, [(n, a.data_root, out, a.nrows) for n in src_names]))
        res["_runtime_s"] = round(time.perf_counter() - t, 1)
        _dump(res, out / "profiles.json")
        print(f"profile done {res['_runtime_s']}s", file=sys.stderr)
    if "truth" in stages and need("truth.json"):
        t = time.perf_counter()
        _, res, _, _ = _load_truth(out, a.data_root)
        res["total_runtime_s"] = round(time.perf_counter() - t, 1)
        res["peak_rss_mb"] = round(psutil.Process().memory_info().rss / 2**20)
        _dump(res, out / "truth.json")
        print("truth done", file=sys.stderr)
    if "pairs" in stages and need("pairs.json"):
        from .pairs import noise_census
        gt, _, aux, _ = _load_truth(out, a.data_root)
        res = noise_census(gt, aux, {k: C.path_of(f"train_source{k}", a.data_root) for k in (1, 2, 3)},
                           n_entities=a.n_entities, seed=C.SEED)
        _dump(res, out / "pairs.json")
        print("pairs done", file=sys.stderr)
    if "leakage" in stages and need("leakage.json"):
        from .leakage import leakage_audit
        from .truth import load_npz
        gt, _, aux, s = _load_truth(out, a.data_root)
        tests = {k: load_npz(out / f"rows_test_source{k}.npz") for k in (1, 2, 3)
                 if (out / f"rows_test_source{k}.npz").exists()}
        _dump(leakage_audit(gt, aux, s[1], s[2], s[3], tests, C.SEED), out / "leakage.json")
        print("leakage done", file=sys.stderr)
    if "drift" in stages and need("drift.json"):
        from .drift import compare
        prof = _load(out / "profiles.json")
        _dump({f"S{k}": compare(prof[f"train_source{k}"], prof[f"test_source{k}"]) for k in (1, 2, 3)},
              out / "drift.json")
        print("drift done", file=sys.stderr)
    print(f"total {time.perf_counter()-t_all:.0f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
