"""Phase 1 tests. Run from code/business_entity_resolution:  python -m unittest discover -s tests -v
TEST-001 (parse/columns/utf8), TEST-002 (IDs unique, GT 1:1), TEST-003 (audit counts, none dropped)
plus edge, reproducibility and integration tests for the EDA tooling itself."""
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.eda import config as C
from src.eda import drift, rawscan, run_p1, text_utils as T
from src.eda.leakage import auc, leakage_audit
from src.eda.pairs import noise_census
from src.eda.profile import profile_source
from src.eda.truth import IdIndex, analyze_truth, load_npz, parse_ground_truth
from tests.helpers import H, build

COLS = C.SOURCE_COLS


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = build(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def p(self, name):
        return C.path_of(name, self.root)


class TestRawScan(Base):
    def test_clean_fixture(self):  # TEST-001
        r = rawscan.scan_tsv(self.p("train_source1"), COLS, "S1")
        self.assertTrue(r["header_ok"])
        self.assertEqual(r["data_lines"], 6)
        self.assertEqual(r["wrong_column_lines"], 0)
        self.assertEqual(r["invalid_utf8_lines"], 0)
        self.assertEqual(r["quote_lines"], 1)      # the quoted name is counted, not hidden
        self.assertEqual(r["id_prefix_bad"], 0)

    def test_malformed_variants(self):  # TEST-003 / P1-012
        d = Path(self.tmp.name) / "bad.tsv"
        body = (b"\xef\xbb\xbfentity_id\tbusiness_name\tbusiness_address\tcountry\r\n"
                b"S1-1\tA\tB\tUS\r\n"
                b"S1-2\tA\tB\tC\tD\tUS\n"          # too many columns
                b"S1-3\tA\tB\n"                    # too few
                b"\n"                              # blank
                b"S1-4\tbad\xff\xfebytes\tB\tUS\n"  # invalid utf-8
                b"S2-5\tWrongPrefix\tB\tUS\n"
                b"S1-6\tlast\tno newline\tUS")
        d.write_bytes(body)
        r = rawscan.scan_tsv(d, COLS, "S1")
        self.assertTrue(r["bom"])
        self.assertEqual(r["crlf_lines"], 2)
        self.assertEqual(r["wrong_column_lines"], 2)
        self.assertEqual(r["blank_lines"], 1)
        self.assertEqual(r["invalid_utf8_lines"], 1)
        self.assertEqual(r["id_prefix_bad"], 1)
        self.assertFalse(r["final_newline"])
        self.assertEqual(r["data_lines"], 7)

    def test_wrong_header(self):
        d = Path(self.tmp.name) / "h.tsv"
        d.write_text("id\tname\n", encoding="utf-8")
        self.assertFalse(rawscan.scan_tsv(d, COLS, "S1")["header_ok"])

    def test_empty_file(self):
        d = Path(self.tmp.name) / "e.tsv"
        d.write_bytes(b"")
        r = rawscan.scan_tsv(d, COLS, "S1")
        self.assertEqual(r["data_lines"], 0)

    def test_default_read_hides_na_and_quotes(self):
        # 'NA' business name is silently turned to NaN by the README's one-liner
        r = rawscan.pandas_default_read_check(self.p("train_source2"), COLS)
        self.assertGreaterEqual(r["nan_cells_default_parse"]["business_name"], 1)


class TestText(unittest.TestCase):
    def test_norm_punct_and_amp(self):
        s = pd.Series(["Pvt. Ltd.", "Pvt Ltd", "Beta & Sons", "Orelee's"])
        n = T.norm(s).tolist()
        self.assertEqual(n[0], n[1])
        self.assertEqual(n[2], "beta and sons")
        self.assertEqual(n[3], "orelees")

    def test_norm_keeps_devanagari_marks(self):
        s = pd.Series(["राम मार्केटिंग"])
        self.assertEqual(T.norm(s).iloc[0], "राम मार्केटिंग")  # matras are not punctuation

    def test_parse_ids(self):
        ids, ok = T.parse_ids(pd.Series(["S2-12", "S3-12", "S2-", "S2-1x", "", "S2-1234567890123456789"]), "S2")
        self.assertEqual(ok.tolist(), [True, False, False, False, False, False])
        self.assertEqual(ids.tolist(), [12, -1, -1, -1, -1, -1])

    def test_script_flags(self):
        f = T.script_flags(pd.Series(["Abc", "राम", "École", "राम Abc", ""]))
        self.assertEqual(f["nonlatin"].tolist(), [False, True, False, True, False])
        self.assertEqual(f["mixed_script"].tolist(), [False, False, False, True, False])
        self.assertEqual(f["latin_ext"].tolist(), [False, False, True, False, False])

    def test_pair_flags(self):
        a = ("Acme Corporation", "1 Main Street, Austin")
        b = ("ACME CORP.", "1 MAIN ST, AUSTIN")
        n = lambda x: T.norm(pd.Series([x])).iloc[0]
        f = T.pair_flags(a[0], b[0], a[1], b[1], n(a[0]), n(b[0]), n(a[1]), n(b[1]))
        self.assertFalse(f["name_exact"])
        self.assertTrue(f["name_canon_equal"])
        self.assertTrue(f["addr_canon_equal"])
        g = T.pair_flags("Beta Sons", "Sons Beta", "x", "x")
        self.assertTrue(g["name_token_set_equal_reordered"])
        h = T.pair_flags("Ram Marketing", "राम मार्केटिंग", "KH 5 Delhi", "KH 5 Delhi")
        self.assertTrue(h["name_match_is_nonlatin"])
        self.assertTrue(h["name_token_overlap_zero"])
        self.assertFalse(h["both_token_overlap_zero"])

    def test_empty_strings(self):
        f = T.pair_flags("", "", "", "")
        self.assertEqual(f["name_sim"], 0.0)


class TestProfile(Base):
    def prof(self, name, sno, **kw):
        out = Path(self.tmp.name) / f"{name}.npz"
        return profile_source(self.p(name), sno, out, log=False, **kw), out

    def test_counts_and_countries(self):  # TEST-001/003/005-country
        m, _ = self.prof("train_source2", 2)
        self.assertEqual(m["rows"], 8)                     # quote-bearing row NOT lost (QUOTE_NONE)
        self.assertEqual(m["rows_by_country"], {"US": 7, "India": 1})
        self.assertEqual(m["bad_id_rows"], 0)
        self.assertEqual(m["ids"]["unique"], 8)
        self.assertEqual(m["flags"]["name_hyg"]["na_token"]["India"], 1)   # 'NA' name detected
        self.assertEqual(m["flags"]["name_script"]["nonlatin"]["US"], 0)

    def test_empty_address_counted(self):
        m, _ = self.prof("train_source3", 3)
        self.assertEqual(m["empty"]["business_address"]["India"], 1)
        self.assertEqual(m["flags"]["name_script"]["devanagari"]["India"], 1)

    def test_duplicates(self):  # P1-004
        m, _ = self.prof("train_source2", 2)
        self.assertEqual(m["duplicates"]["exact"]["groups"], 1)        # S2-11 == S2-17
        self.assertEqual(m["duplicates"]["exact"]["records_in_groups"], 2)
        self.assertGreaterEqual(m["duplicates"]["norm"]["groups"], 1)

    def test_france_open_set(self):  # C-France: unseen country flows through
        m, _ = self.prof("test_source2", 2)
        self.assertEqual(m["rows_by_country"].get("France"), 1)
        self.assertEqual(m["flags"]["addr"]["fr_street_abbr"]["France"], 1)

    def test_header_only_file(self):
        d = Path(self.tmp.name) / "empty" / "train_source2.tsv"
        d.parent.mkdir(exist_ok=True)
        d.write_text(H, encoding="utf-8")
        m = profile_source(d, 2, None, log=False)
        self.assertEqual(m["rows"], 0)

    def test_chunk_boundary_invariance(self):
        a, _ = self.prof("train_source2", 2, chunk_rows=3)
        b, _ = self.prof("train_source2", 2, chunk_rows=1000)
        for k in ("rows", "rows_by_country", "flags", "duplicates", "empty", "length_hist", "ids"):
            self.assertEqual(json.dumps(a[k], sort_keys=True), json.dumps(b[k], sort_keys=True), k)

    def test_reproducible(self):
        a, pa = self.prof("train_source1", 1)
        b, pb = self.prof("train_source1", 1)
        strip = lambda m: {k: v for k, v in m.items() if k not in ("runtime_s", "peak_rss_mb")}
        self.assertEqual(json.dumps(strip(a), sort_keys=True), json.dumps(strip(b), sort_keys=True))
        self.assertTrue(np.array_equal(load_npz(pa)["h_exact"], load_npz(pb)["h_exact"]))


class TestTruth(Base):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.s = {}
        for k in (1, 2, 3):
            out = Path(cls.tmp.name) / f"s{k}.npz"
            profile_source(C.path_of(f"train_source{k}", cls.root), k, out, log=False)
            cls.s[k] = load_npz(out)
        cls.gt = parse_ground_truth(C.path_of("train_ground_truth", cls.root))
        cls.res, cls.aux = analyze_truth(cls.gt, cls.s[1], cls.s[2], cls.s[3])

    def test_cardinality_exact(self):  # P1-006
        c = self.res["cardinality"]
        self.assertEqual((c["entities"], c["singletons"], c["one_match"], c["two_plus"], c["max_matches"]), (6, 2, 2, 2, 3))
        self.assertEqual(c["total_hist"], {0: 2, 1: 2, 2: 1, 3: 1})

    def test_source_split(self):  # P1-007
        s = self.res["source_split"]
        self.assertEqual((s["match_ids_s2"], s["match_ids_s3"]), (5, 2))
        self.assertEqual((s["entities_s2_only"], s["entities_s3_only"], s["entities_both"], s["entities_none"]), (2, 1, 1, 2))

    def test_gt_covers_s1_one_to_one(self):  # TEST-002
        g = self.res["gt_vs_s1"]
        self.assertEqual((g["gt_ids_not_in_s1"], g["s1_ids_not_in_gt"], g["same_row_order"]), (0, 0, True))
        self.assertEqual(self.res["s1_unique"]["rows"], self.res["s1_unique"]["unique_valid"])

    def test_orphans_and_integrity(self):
        mi = self.res["match_integrity"]
        self.assertEqual(mi["s2"]["orphan_records"], 3)      # S2-16, 17, 18
        self.assertEqual(mi["s3"]["orphan_records"], 1)
        self.assertEqual(mi["s2"]["ids_missing_from_source_file"], 0)
        self.assertEqual(mi["s2"]["country_disagree_tokens"], 0)

    def test_dup_vs_truth(self):
        d = self.res["dup_vs_truth"]["s2_exact"]      # S2-11 (matched to S1-1) vs S2-17 (orphan)
        self.assertEqual((d["groups"], d["mixed_matched_and_orphan"], d["all_same_entity"]), (1, 1, 0))

    def test_gt_anomalies_counted_not_repaired(self):  # TEST-003
        p = Path(self.tmp.name) / "gt_bad.tsv"
        p.write_text("source1_entity_id\tmatched_entity_ids\n"
                     "S1-1\tS2-11,S2-11\nS1-2\tS2-12,\nS1-3\t S3-21\nS1-4\tS1-9,S4-7,junk\nX-5\t\n", encoding="utf-8")
        g = parse_ground_truth(p)["anom"]
        self.assertEqual(g["rows"], 5)
        self.assertEqual(g["empty_token"], 1)
        self.assertEqual(g["token_ws"], 1)
        self.assertEqual(g["s1_prefix_in_list"], 1)
        self.assertEqual(g["bad_token"], 3)   # S1-9, S4-7, junk
        self.assertEqual(g["bad_s1_id"], 1)
        self.assertEqual(g["singleton"], 1)

    def test_idindex(self):
        ix = IdIndex(np.array([30, 10, 20]))
        self.assertEqual(ix.pos(np.array([10, 20, 30, 99, 5])).tolist(), [1, 2, 0, -1, -1])

    def test_noise_census_runs_and_sane(self):  # P1-009
        paths = {k: C.path_of(f"train_source{k}", self.root) for k in (1, 2, 3)}
        r = noise_census(self.gt, self.aux, paths, n_entities=100, n_negatives=5, log=False)
        self.assertEqual(r["pairs"], 7)
        self.assertEqual(r["pairs_missing_records"], 0)
        self.assertGreater(r["overall"]["name_canon_equal"], 0)
        self.assertEqual(r["nonlatin_match_name"]["n"], 1)

    def test_leakage_audit_runs(self):  # P1-011
        tests = {k: load_npz(Path(self.tmp.name) / f"t{k}.npz") for k in ()}
        for k in (1, 2, 3):
            out = Path(self.tmp.name) / f"t{k}.npz"
            profile_source(C.path_of(f"test_source{k}", self.root), k, out, log=False)
            tests[k] = load_npz(out)
        r = leakage_audit(self.gt, self.aux, self.s[1], self.s[2], self.s[3], tests)
        self.assertEqual(r["train_test_overlap"]["S2"]["shared_ids"], 0)
        self.assertIn("S1-S2", r["pair_relations"])

    def test_auc(self):
        s = np.array([1., 2., 3., 4.])
        self.assertEqual(auc(s, np.array([False, False, True, True])), 1.0)
        self.assertEqual(auc(s, np.array([True, True, False, False])), 0.0)
        self.assertEqual(auc(np.ones(4), np.array([True, False, True, False])), 0.5)
        self.assertTrue(np.isnan(auc(s, np.zeros(4, bool))))


class TestDrift(unittest.TestCase):
    def test_psi_identity_and_shift(self):
        self.assertAlmostEqual(drift.psi([5, 5, 5], [5, 5, 5]), 0.0)
        self.assertGreater(drift.psi([9, 1], [1, 9]), 1.0)


class TestIntegration(Base):
    def test_full_pipeline_on_fixture(self):
        out = Path(self.tmp.name) / "art"
        run_p1.main(["--stage", "all", "--data-root", str(self.root), "--out", str(out), "--workers", "1"])
        for f in ("rawscan.json", "profiles.json", "truth.json", "pairs.json", "leakage.json", "drift.json"):
            self.assertTrue((out / f).exists(), f)
        d = json.loads((out / "drift.json").read_text())
        self.assertEqual(d["S2"]["country_share"]["France"]["train_rows"], 0)   # France test-only
        self.assertEqual(d["S2"]["country_share"]["France"]["test_rows"], 1)
        raw = json.loads((out / "rawscan.json").read_text())
        self.assertEqual(raw["train_source2"]["data_lines"], 8)


if __name__ == "__main__":
    unittest.main()
