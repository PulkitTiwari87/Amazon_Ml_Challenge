"""Render Docs/reports/data_quality_report.md and leakage_risk_report.md from the JSON artifacts.

All numbers come from the artifacts; hand-written decisions/notes are read verbatim from
Docs/reports/p1_decisions.md and p1_leakage_notes.md so the tables can be regenerated
without losing the analysis.  Run: python -m src.eda.render_report
"""
import json
from datetime import date
from pathlib import Path

import numpy as np

from . import config as C

A = C.ARTIFACT_DIR
R = C.REPORT_DIR


def J(name):
    p = A / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out) + "\n"


def n(x):
    return "—" if x is None else f"{x:,}"


def pc(x, d=2):
    return "—" if x is None else f"{100 * x:.{d}f}%"


def pct_from_hist(h, q):
    c = np.cumsum(h)
    return int(np.searchsorted(c, q / 100 * c[-1]))


def note(name):
    p = R / name
    return p.read_text(encoding="utf-8") if p.exists() else f"_({name} not yet written)_\n"


def data_quality():
    raw, prof, truth, pairs, drift = J("rawscan.json"), J("profiles.json"), J("truth.json"), J("pairs.json"), J("drift.json")
    o = [f"# Phase 1 — Data Quality Report\n\nGenerated {date.today()} by `src/eda/render_report.py` from `artifacts/p1/*.json` "
         f"(seed {C.SEED}). Every number below is measured from the real TSVs; nothing is copied from another document. "
         "Task IDs = plan.md §8.\n"]
    # ---- schema
    o.append("## 1. Schema / structure / malformed records (P1-001, P1-012; TEST-001)\n")
    rows = []
    for f, r in raw.items():
        if f.startswith("_"):
            continue
        d = r.get("default_read", {})
        rows.append([f, f"{r['bytes']/2**20:,.0f}", n(r["data_lines"]), n(C.EXPECTED_ROWS[f]),
                     "yes" if r["data_lines"] == C.EXPECTED_ROWS[f] else "NO", r["header_ok"],
                     r["wrong_column_lines"], r["invalid_utf8_lines"], r["blank_lines"], r["nul_lines"],
                     r["crlf_lines"], r["bom"], n(r["quote_lines"]), n(d.get("rows_default_parse"))])
    o.append(table(["file", "MB", "data lines (raw)", "plan.md §2 rows", "match", "header ok", "wrong #cols", "bad UTF-8",
                    "blank", "NUL", "CRLF", "BOM", "lines with `\"`", "rows via pandas default read"], rows))
    rows = []
    for f, r in raw.items():
        if f.startswith("_") or "default_read" not in r:
            continue
        rows.append([f, json.dumps(r["tab_count_hist"]), json.dumps(r["default_read"]["nan_cells_default_parse"])])
    o.append("\nTab-count histogram per line, and cells that `pd.read_csv(path, sep='\\t')` (README's own one-liner) turns into NaN:\n\n")
    o.append(table(["file", "tabs/line histogram", "NaN cells under default parse"], rows))
    # ---- uniqueness
    o.append("\n## 2. Row-count and uniqueness audit (P1-002; TEST-002)\n")
    rows = []
    for f, p in prof.items():
        if f.startswith("_"):
            continue
        i = p["ids"]
        rows.append([f, n(p["rows"]), n(i["valid"]), n(i["unique"]), p["bad_id_rows"], i["min"], i["max"],
                     f"{i['ascending_pair_frac']:.4f}", json.dumps(p["id_digits_hist"])])
    o.append(table(["file", "rows parsed", "valid IDs", "unique IDs", "invalid-ID rows", "min id", "max id",
                    "P(next id > prev)", "ID string length hist"], rows))
    if truth:
        g, s = truth["gt_vs_s1"], truth["s1_unique"]
        o.append("\nGround truth vs `train_source1`:\n\n" + table(["metric", "value"], [
            ["train_source1 rows / unique valid IDs", f"{n(s['rows'])} / {n(s['unique_valid'])}"],
            ["GT rows / unique S1 IDs", f"{n(g['gt_rows'])} / {n(g['gt_unique_ids'])}"],
            ["GT IDs missing from train_source1", g["gt_ids_not_in_s1"]],
            ["train_source1 IDs missing from GT", g["s1_ids_not_in_gt"]],
            ["identical row order (GT vs S1)", g["same_row_order"]]]))
        o.append("\nGT parse anomalies (counted, never silently repaired): `" + json.dumps(truth["anomalies"]) + "`\n")
    # ---- missingness
    o.append("\n## 3. Null / empty-field audit (P1-003; TEST-003)\n\nRate = rows in that country. `ws-only` = whitespace-only; `NA-token` = literal NA-like strings "
             "(`NA`, `null`, `none`, `-`, ...) that pandas default parsing would convert to NaN.\n")
    rows = []
    for f, p in prof.items():
        if f.startswith("_"):
            continue
        for c, tot in p["rows_by_country"].items():
            e, w = p["empty"], p["ws_only"]
            rows.append([f, c, n(tot)] + [f"{n(e[col].get(c, 0))} ({pc(e[col].get(c, 0)/tot)})" for col in ("business_name", "business_address", "country", "entity_id")]
                        + [n(w["business_name"].get(c, 0)), n(w["business_address"].get(c, 0)),
                           n(p["flags"]["name_hyg"]["na_token"].get(c, 0)), n(p["flags"]["addr_hyg"]["na_token"].get(c, 0))])
    o.append(table(["file", "country", "rows", "empty name", "empty address", "empty country", "empty id", "ws-only name",
                    "ws-only addr", "NA-token name", "NA-token addr"], rows))
    # ---- duplicates
    o.append("\n## 4. Duplicate / near-duplicate records (P1-004)\n\nKeys: **exact** = raw (name,address,country); **norm** = NFKC+casefold+punctuation-stripped+whitespace-collapsed "
             "(name,address,country); **tokset** = norm with tokens sorted (word-order-insensitive). `groups` = key values shared by ≥2 records. "
             "This is a *proxy* for near-duplicates (no fuzzy matching at 5M scale in Phase 1).\n")
    rows = []
    for f, p in prof.items():
        if f.startswith("_"):
            continue
        for k, d in p["duplicates"].items():
            rows.append([f, k, n(d["groups"]), n(d["records_in_groups"]), pc(d["records_in_groups"] / p["rows"], 3), d["max_group"], json.dumps(d["size_hist"])])
    o.append(table(["file", "key", "groups", "records in groups", "% rows", "max group", "group-size hist (10 = 10+)"], rows))
    if truth:
        rows = [[k, *[n(v.get(x)) for x in ("groups", "records", "all_same_entity", "span_multiple_entities", "all_orphan", "mixed_matched_and_orphan")]]
                for k, v in truth["dup_vs_truth"].items()]
        o.append("\nDuplicate groups in S2/S3 vs the ground truth (does a duplicate group stay inside one S1 entity?):\n\n" +
                 table(["source_key", "groups", "records", "all same S1 entity", "span >1 S1 entities", "all orphan", "mixed matched+orphan"], rows))
        rows = [[k, *[n(v.get(x)) for x in ("groups", "records")]] for k, v in truth["s1_dups"].items()]
        o.append("\nDuplicates inside `train_source1` (billed as 'deduplicated reference'):\n\n" + table(["key", "groups", "records"], rows))
    # ---- country
    o.append("\n## 5. Country distribution (P1-005)\n")
    rows = []
    for f, p in prof.items():
        if f.startswith("_"):
            continue
        for c, k in sorted(p["rows_by_country"].items()):
            rows.append([f, c, n(k), pc(k / p["rows"])])
    o.append(table(["file", "country (exact string)", "rows", "share"], rows))
    # ---- cardinality
    if truth:
        c = truth["cardinality"]
        o.append("\n## 6. Match cardinality (P1-006)\n\n" + table(["metric", "value"], [
            ["S1 entities", n(c["entities"])], ["singletons (no match)", f"{n(c['singletons'])} ({pc(c['singleton_frac'])})"],
            ["exactly 1 match", n(c["one_match"])], ["2+ matches", n(c["two_plus"])], ["max matches", c["max_matches"]],
            ["mean matches / entity (all)", f"{c['mean_matches']:.3f}"], ["mean matches / non-singleton", f"{c['mean_matches_nonsingleton']:.3f}"],
            ["percentiles (non-singleton) 50/90/99/99.9", json.dumps(c["percentiles_nonsingleton"])]]))
        o.append("\nHistograms (key = number of matches, capped at 25): total `" + json.dumps(c["total_hist"]) + "`; S2 `" + json.dumps(c["s2_hist"]) + "`; S3 `" + json.dumps(c["s3_hist"]) + "`\n")
        rows = [[k, n(v["entities"]), pc(v["singleton_frac"]), f"{v['mean_matches']:.3f}", n(v["s2_only"]), n(v["s3_only"]), n(v["both"])] for k, v in truth["by_country"].items()]
        o.append("\nBy S1 country:\n\n" + table(["country", "entities", "singleton %", "mean matches", "S2 only", "S3 only", "both"], rows))
        s = truth["source_split"]
        o.append("\n## 7. Match split by source, orphans, integrity (P1-007)\n\n" + table(["metric", "value"], [
            ["matched IDs with S2 prefix", n(s["match_ids_s2"])], ["matched IDs with S3 prefix", n(s["match_ids_s3"])],
            ["entities with S2 matches only", n(s["entities_s2_only"])], ["S3 only", n(s["entities_s3_only"])],
            ["both S2 and S3", n(s["entities_both"])], ["none", n(s["entities_none"])]]))
        rows = []
        for k, v in truth["match_integrity"].items():
            rows.append([k.upper(), n(v["match_tokens"]), n(v["unique_match_ids"]), n(v["ids_missing_from_source_file"]), n(v["ids_claimed_by_multiple_s1"]),
                         v["max_claims_per_id"], n(v["dup_tokens_within_list"]), n(v["source_file_rows"]), f"{n(v['orphan_records'])} ({pc(v['orphan_frac'])})",
                         n(v["country_disagree_tokens"])])
        o.append("\n" + table(["src", "match tokens", "unique match IDs", "IDs absent from source file", "IDs claimed by >1 S1", "max claims/ID", "dup tokens in a list",
                               "source rows", "orphan records (matched to no S1)", "matched pairs with different country"], rows))
        rows = [[k.upper(), c, n(v["rows_by_country"][c]), n(v["orphan_by_country"][c]), pc(v["orphan_by_country"][c] / max(v["rows_by_country"][c], 1))]
                for k, v in truth["match_integrity"].items() for c in v["rows_by_country"]]
        o.append("\nOrphans by country:\n\n" + table(["src", "country", "rows", "orphans", "orphan %"], rows))
    # ---- text stats
    o.append("\n## 8. Text statistics and character sets (P1-008)\n\nLength = characters. p50/p95/p99/max-bin from exact histograms (name cap 300, address cap 500; the last bin absorbs longer values).\n")
    rows = []
    for f, p in prof.items():
        if f.startswith("_"):
            continue
        for c in p["rows_by_country"]:
            row = [f, c]
            for key in ("name_len", "addr_len", "name_tok", "addr_tok"):
                h = p["length_hist"][key][c]
                row.append("/".join(str(pct_from_hist(h, q)) for q in (50, 95, 99)) + f" (max-bin {max(i for i, v in enumerate(h) if v)})")
            rows.append(row)
    o.append(table(["file", "country", "name len p50/95/99", "addr len p50/95/99", "name tokens", "addr tokens"], rows))
    keys = ["nonascii", "latin_ext", "devanagari", "other_indic", "cjk", "arabic", "cyrillic", "nonlatin", "mixed_script"]
    rows = []
    for f, p in prof.items():
        if f.startswith("_"):
            continue
        for c, tot in p["rows_by_country"].items():
            for fld in ("name_script", "addr_script"):
                rows.append([f, c, fld[:4]] + [pc(p["flags"][fld][k].get(c, 0) / tot) for k in keys])
    o.append("\nShare of records containing each script class:\n\n" + table(["file", "country", "field"] + keys, rows))
    hk = ["control_char", "replacement_char", "zero_width", "nbsp", "mojibake_hint", "leading_trailing_ws", "html_entity"]
    rows = []
    for f, p in prof.items():
        if f.startswith("_"):
            continue
        for c, tot in p["rows_by_country"].items():
            for fld in ("name_hyg", "addr_hyg"):
                rows.append([f, c, fld[:4]] + [n(p["flags"][fld][k].get(c, 0)) for k in hk])
    o.append("\nEncoding / hygiene anomaly counts (records):\n\n" + table(["file", "country", "field"] + hk, rows))
    o.append("\nNot NFC-normalised (records): " + "; ".join(f"{f}: name {n(p['not_nfc']['name'])}, addr {n(p['not_nfc']['addr'])}" for f, p in prof.items() if not f.startswith("_")) + "\n")
    # ---- noise census
    o.append("\n## 9. Noise-pattern census (P1-009)\n\n### 9a. Population-level regex census (share of records; heuristic patterns in `text_utils.py`)\n")
    nf = list(next(iter(prof.values()))["flags"]["name"].keys()) if prof else []
    af = list(next(iter(prof.values()))["flags"]["addr"].keys()) if prof else []
    for grp, fl in (("name", nf), ("addr", af)):
        rows = []
        for f, p in prof.items():
            if f.startswith("_"):
                continue
            for c, tot in p["rows_by_country"].items():
                rows.append([f, c] + [pc(p["flags"][grp][k].get(c, 0) / tot, 1) for k in fl])
        o.append(f"\n**{grp}**\n\n" + table(["file", "country"] + fl, rows))
    if pairs:
        o.append(f"\n### 9b. Pair-level census on matched pairs\n\nSeeded random sample: {n(pairs['sampled_entities'])} non-singleton S1 entities → {n(pairs['pairs'])} (S1 record, matched record) pairs "
                 f"({pairs['pairs_missing_records']} pairs had a missing record). Random baseline = same-country/same-source random pairs (chance level, **not** hard negatives).\n")
        keys = [k for k in pairs["overall"] if not k.endswith("_hist10") and k not in ("n", "name_sim_mean", "addr_sim_mean")]
        cols = {"overall": pairs["overall"], **{f"src {k}": v for k, v in pairs["by_match_source"].items()},
                **{f"cty {k}": v for k, v in pairs["by_country"].items()}, "RANDOM neg": pairs["random_negative_baseline"]}
        rows = [[k] + [pc(v.get(k), 1) for v in cols.values()] for k in keys]
        rows.append(["n pairs"] + [n(v["n"]) for v in cols.values()])
        rows.append(["mean name_sim (difflib)"] + [f"{v['name_sim_mean']:.3f}" for v in cols.values()])
        rows.append(["mean addr_sim (difflib)"] + [f"{v['addr_sim_mean']:.3f}" for v in cols.values()])
        o.append(table(["flag (share of pairs)"] + list(cols), rows))
        o.append("\nname_sim histogram (10 bins 0→1): matched `" + json.dumps(pairs["overall"]["name_sim_hist10"]) + "`; random `" + json.dumps(pairs["random_negative_baseline"]["name_sim_hist10"]) + "`\n")
        o.append("\naddr_sim histogram: matched `" + json.dumps(pairs["overall"]["addr_sim_hist10"]) + "`; random `" + json.dumps(pairs["random_negative_baseline"]["addr_sim_hist10"]) + "`\n")
        o.append("\nNon-Latin matched-record names: `" + json.dumps(pairs["nonlatin_match_name"]) + "`; Latin: `" + json.dumps(pairs["latin_match_name"]) + "`\n")
    # ---- drift
    if drift:
        o.append("\n## 10. Train vs test distribution (P1-010)\n\nPSI computed on train-quantile bins (convention: <0.1 small, 0.1–0.25 moderate, >0.25 large — a convention, not a rule of the challenge).\n")
        rows = []
        for s, d in drift.items():
            for c, v in d["country_share"].items():
                rows.append([s, c, n(v["train_rows"]), pc(v["train_share"]), n(v["test_rows"]), pc(v["test_share"])])
        o.append(table(["source", "country", "train rows", "train share", "test rows", "test share"], rows))
        rows = [[s, k, f"{v:.4f}"] for s, d in drift.items() for k, v in d["psi"].items()]
        o.append("\nPSI (length / token-count histograms):\n\n" + table(["source", "country|field", "PSI"], rows))
        rows = []
        for s, d in drift.items():
            for c, lst in d["flag_shift_pp"].items():
                for e in lst[:5]:
                    rows.append([s, c, e["flag"], pc(e["train"], 2), pc(e["test"], 2), f"{e['shift_pp']:+.2f}"])
        o.append("\nLargest flag-rate shifts per country (top 5, percentage points):\n\n" + table(["source", "country", "flag", "train", "test", "shift pp"], rows))
        if truth:
            tr = {s: prof[f"train_source{s}"]["rows"] for s in (1, 2, 3)}
            te = {s: prof[f"test_source{s}"]["rows"] for s in (1, 2, 3)}
            o.append("\nRecords per S1 entity: " + "; ".join(f"S{s}/S1 train {tr[s]/tr[1]:.3f} vs test {te[s]/te[1]:.3f}" for s in (2, 3)) + "\n")
    o.append("\n## 11. Anomaly register and decisions\n\n" + note("p1_decisions.md"))
    (R / "data_quality_report.md").write_text("\n".join(o), encoding="utf-8")


def leakage():
    lk = J("leakage.json")
    o = [f"# Phase 1 — Leakage Risk Report\n\nGenerated {date.today()} from `artifacts/p1/leakage.json` (P1-011). 'Leakage' here = anything that predicts match / singleton / "
         "orphan status without name or address similarity, or that lets train information into test. AUC 0.5 and Spearman 0 mean no exploitable signal.\n"]
    if lk:
        rows = [[k] + [f"{v[x]:.5f}" if isinstance(v[x], float) else v[x] for x in v] for k, v in lk["pair_relations"].items()]
        hdr = ["pair"] + list(next(iter(lk["pair_relations"].values())).keys())
        o.append("## 1. Do matched pairs have related IDs / file positions?\n\n" + table(hdr, rows))
        rows = []
        for k, v in lk["orphan_predictability"].items():
            rows.append([k, pc(v["orphan_frac"]), f"{v['auc_id_value']:.4f}", f"{v['auc_id_digit_length']:.4f}", f"{v['auc_file_position']:.4f}"])
        o.append("\n## 2. Can ID or file position predict an orphan (unmatched S2/S3 record)?\n\n" + table(["source", "orphan %", "AUC id value", "AUC id length", "AUC file position"], rows))
        for k, v in lk["orphan_predictability"].items():
            o.append(f"\n{k} orphan rate by id decile: `{[None if x is None else round(x, 4) for x in v['orphan_frac_by_id_decile']]}`; by file-position decile: `{[None if x is None else round(x, 4) for x in v['orphan_frac_by_position_decile']]}`\n")
        s = lk["singleton_predictability"]
        o.append("\n## 3. Can ID or row position predict a singleton S1 entity?\n\n" + table(["metric", "value"], [
            ["singleton fraction", pc(s["singleton_frac"])], ["AUC S1 id value", f"{s['auc_s1_id_value']:.4f}"],
            ["AUC S1 id length", f"{s['auc_s1_id_digit_length']:.4f}"], ["AUC GT row position", f"{s['auc_gt_row_position']:.4f}"]]))
        o.append(f"\nSingleton rate by id decile `{[None if x is None else round(x, 4) for x in s['singleton_frac_by_id_decile']]}`; by row-position decile `{[None if x is None else round(x, 4) for x in s['singleton_frac_by_position_decile']]}`\n")
        rows = [[k, *[n(v[x]) for x in ("train_rows", "test_rows", "shared_ids", "shared_exact_records", "shared_normalised_records", "test_records_with_normalised_twin_in_train")]] for k, v in lk["train_test_overlap"].items()]
        o.append("\n## 4. Train ↔ test overlap\n\n" + table(["source", "train rows", "test rows", "shared IDs", "shared exact (name,addr,country) values", "shared normalised values", "test records with normalised twin in train"], rows))
    o.append("\n## 5. Assessment and decisions\n\n" + note("p1_leakage_notes.md"))
    (R / "leakage_risk_report.md").write_text("\n".join(o), encoding="utf-8")


if __name__ == "__main__":
    data_quality()
    leakage()
    print("reports written to", R)
