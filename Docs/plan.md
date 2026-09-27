# Amazon ML Challenge — Full Execution Plan

**Generated:** 2026-09-25
**Project root:** `E:\Amazon ML Challenge`
**Status:** No prior `plan.md` existed. This is the first version — nothing to reconcile.

---

## 0. Files Actually Inspected For This Plan

No file names were assumed. The directory tree was walked before writing anything below.

```
E:\Amazon ML Challenge\
├── Dataset\student_resource\
│   ├── README.md                                    [OFFICIAL — problem statement, markdown copy]
│   ├── Documentation_template.md                     [OFFICIAL — required methodology template]
│   ├── utils\validate_submission.py                  [OFFICIAL — local submission validator, read in full]
│   └── dataset\{train,test}\*.tsv                     [OFFICIAL — actual competition data, row-counted and header-sampled directly]
├── Docs\
│   ├── 6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf        [OFFICIAL — read in full, 8 pages]
│   ├── 6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf  [OFFICIAL — read in full, 2 pages]
│   ├── AMAZON_ML_CHALLENGE_MASTER.md                  [SECONDARY — self-authored KB, verified against the two PDFs above]
│   ├── Amazon ML Challenge Forensic Analysis.md       [SECONDARY / mostly UNVERIFIED for 2021–2025 specifics — read in full]
│   ├── amazon_ml_challenge_2026_complete_video_and_source_notes.json  [SECONDARY — derived notes; explicitly has NO video transcript]
│   └── graphify-out\ (GRAPH_REPORT.md, graph.json, manifest.json, cost.json)  [SECONDARY — knowledge-graph over the above; consulted before drawing conclusions below]
```

There is **no** separate `Knowledge Base\` directory and **no** `graphify\` directory (it is `Docs\graphify-out\`) — both were named hypothetically in the request. No `notebooks\`, `code\`, or `experiments\` directories exist yet; this project is pre-implementation. This is stated explicitly rather than silently substituted.

`graphify-out` was consulted first for every structural question below (community structure, god-nodes, hyperedges, flagged "surprising connections" and "knowledge gaps" in `GRAPH_REPORT.md`) per the required order graphify → Forensic Analysis → Master KB → original PDFs. Where graphify's own report already flags an unresolved conflict (e.g. the public/private leaderboard shortlisting language), that conflict is carried into this plan rather than silently resolved.

---

## 1. Executive Strategy

The 2026 task is **cross-source business entity resolution** at large scale (~2.2M Source‑1 / ~5M Source‑2 / ~5.3M Source‑3 training records; ~1.7M/4.9M/5.1M test records — counts measured directly from the local TSVs, see §2). Scoring is **macro‑averaged, per‑entity F0.5**, which weights precision 2× over recall and scores singletons explicitly (1.0 for a correctly predicted empty set, 0.0 for any false merge on a true singleton).

Three facts dominate every downstream decision:

1. **Blocking is the ceiling.** At this scale, all‑pairs comparison (~10¹³ pairs) is not viable. Whatever blocking/candidate-generation stage we build sets the maximum achievable recall — nothing downstream can recover a true match blocking never produced. `[OFFICIAL, Problem statement p.7 tips]`
2. **The metric punishes confidence, not caution.** Because β=0.5, an aggressive matcher that over-merges will score worse than a conservative one that misses some true links, and singletons are graded as strictly as matches. `[OFFICIAL, Problem statement p.6]`
3. **France is an adversarial input by design.** It exists in test only, specifically to catch any pipeline that implicitly assumes a closed `{US, India}` country set — country must be treated as an open string label everywhere, including blocking keys and any encoding. `[OFFICIAL, Problem statement p.2]`

The strategy that follows is: verify everything verifiable first (Phase 0–1), build a scoring-correct baseline before any model complexity (Phase 2–3), understand the metric mathematically before touching features (Phase 4), then climb a model ladder only as far as measured evidence justifies (Phase 6–9), while continuously testing robustness to unseen categories and hidden-test distribution shift (Phase 10), and never submitting anything the local validator hasn't already passed (Phase 13).

No claim in this document is that any single approach "wins." Historical winner narratives in the Forensic Analysis document are for *different task types* (classification, regression, image extraction, pricing) under *different metrics*, sourced from Reddit/Medium/GitHub write-ups that are explicitly self-flagged in that document as "not publicly verified" in many places. They are used here only for **meta-engineering discipline** (baseline-first, EDA-first, exact format compliance, local validation before leaderboard chasing) — never for architecture choices, since none of those teams solved an entity-resolution problem.

---

## 2. Verified Challenge Specification

Everything in this table was read directly from the two 2026 official PDFs, cross-checked against the actual dataset files on disk (row counts and header rows were inspected directly, not taken from any secondary document).

| Item | Value | Evidence |
|---|---|---|
| Task | Cross-source business entity resolution: for each Source‑1 entity, find all matching Source‑2/Source‑3 records (0, 1, or many) | `[OFFICIAL]` Problem statement p.1 |
| Source roles | S1 = deduplicated reference; S2, S3 = independent noisy sources to match against | `[OFFICIAL]` Problem statement p.1 |
| File format | `.tsv`, explicit `sep="\t"` required; comma-separated read silently collapses to one column | `[OFFICIAL]` Problem statement p.1 |
| Columns (all 3 source files) | `entity_id` (prefix `S1-`/`S2-`/`S3-`), `business_name`, `business_address`, `country` | `[OFFICIAL]` Problem statement pp.1–2 |
| Ground truth columns | `source1_entity_id`, `matched_entity_ids` (comma-separated, empty = no match) | `[OFFICIAL]` Problem statement p.2 |
| Training countries | `US`, `India` | `[OFFICIAL]` Problem statement p.2; confirmed directly — `train_source1.tsv` shows only `US`/`India` in a sample |
| Test countries | `US`, `India`, **`France`** (unseen in training) | `[OFFICIAL]` Problem statement p.2; confirmed directly — `test_source2.tsv` row 3 is a France record (`Marina Ecole France Sarl`) |
| Country handling rule | Treat as open-set string labels; do not hard-code/filter/one-hot to `{US, India}`; every test entity incl. France must appear in the submission | `[OFFICIAL]` Problem statement p.2 |
| Name noise | Abbreviations (Corp/Corporation, Pvt/Private, Ltd/Limited), legal suffix inconsistency, DBA/trade names, `&` vs "and", word-order transpositions, typos | `[OFFICIAL]` Problem statement p.2 |
| Address noise | Abbreviations (Rd/Road, St/Street), transliteration variants, missing components (no PIN/state), landmark references ("Near SBI ATM"), municipal numbering, reordering | `[OFFICIAL]` Problem statement p.2 |
| **Directly measured row counts** | train_source1 **2,206,821**; train_source2 **5,034,616**; train_source3 **5,285,603**; train_ground_truth **2,206,821**; test_source1 **1,732,544**; test_source2 **4,887,273**; test_source3 **5,082,316** (records, header excluded) | `[OFFICIAL — measured locally, not from any doc]`, `wc -l` + header check on the real files |
| Sanity check already passed | `train_source1.tsv` and `train_ground_truth.tsv` have identical line counts → every training S1 entity appears to have exactly one ground-truth row (to be formally verified in Phase 1, not assumed) | `[OFFICIAL — measured locally]` |
| Output files | `matching_results.tsv` (scored on leaderboard), `candidate_pairs.tsv` (not scored; used to audit blocking recall ceiling / reduction ratio) | `[OFFICIAL]` Problem statement pp.3–4 |
| Output rule set | One row per test S1 entity (empty = no match), no duplicate IDs in a list, no duplicate `source1_entity_id` rows, only existing S2/S3 test IDs, matches ⊆ candidates (soft check — warns, doesn't fail) | `[OFFICIAL]` Problem statement pp.3–4, confirmed against `utils/validate_submission.py` source |
| Local validator | `utils/validate_submission.py` — stdlib only, checks format but **never computes score**; `--check-ids` is off by default (memory-heavy at this scale) | `[OFFICIAL]` — code read in full |
| Metric | `F0.5 = (1.25 × P × R) / (0.25 × P + R)`, computed per Source‑1 entity, then **macro-averaged** across all S1 entities, singletons included (empty-correct = 1.0, any false match on a true singleton = 0.0) | `[OFFICIAL]` Problem statement p.6 |
| Model constraints | MIT or Apache‑2.0 license, ≤ 8B parameters | `[OFFICIAL]` Problem statement p.6 |
| External data | Strictly prohibited: commercial ER APIs, government registration lookups, geocoding APIs, any internet-sourced augmentation. Enforcement = code/pipeline review; violation = immediate disqualification | `[OFFICIAL]` Problem statement p.7 |
| Public/private leaderboard | Public = subset during challenge; private = remaining portion, revealed after | `[OFFICIAL]` Problem statement p.6 |
| Final ranking basis | Problem statement: "final decision... based on the private leaderboard." | `[OFFICIAL]` Problem statement p.6 |
| Shortlisting basis | Guidelines: "Evaluation and shortlisting will be based on performance across **both** leaderboards." | `[OFFICIAL]` Guidelines p.1 |
| **⚠ Conflict — not resolved, recorded** | The two official 2026 documents give different rules for how leaderboards combine (final rank = private only, vs. shortlisting = both). Not merged, not guessed. | `[OFFICIAL vs OFFICIAL — internal document conflict]` |
| Challenge window | 25 Sep 2026 00:00 IST → 27 Sep 2026 23:59 IST | `[OFFICIAL]` Guidelines p.1 |
| Submission limit | 5/day, disabled after 3 days | `[OFFICIAL]` Guidelines p.1 |
| Access rule | Desktop/laptop only, no simultaneous logins (risk of termination) | `[OFFICIAL]` Guidelines p.1 |
| Required artifacts (best solution) | 1–2 page ML-approach document + commented source code | `[OFFICIAL]` Guidelines p.1 |
| Top‑100 follow-up | Methodology, blocking strategy, model architecture/features, other relevant info | `[OFFICIAL]` Guidelines p.2, and Problem statement pp.5–6 (final zip requirement, no page limit there) |
| Final submission package | `<team>_submission.zip` with `output/{matching_results.tsv,candidate_pairs.tsv}`, `code/business_entity_resolution/{src/,README.md,requirements.txt}`, `Documentation_template.md` | `[OFFICIAL]` Problem statement p.5 |
| Grand Finale / interview stage for 2026 | **Not mentioned anywhere in either 2026 official document.** | `[UNVERIFIED for 2026]` — see §5 conflict list |

---

## 3. Evidence & Source Hierarchy (as applied)

1. Official 2026 problem statement PDF & guidelines PDF — binding.
2. Official Amazon/Unstop announcements — none beyond the two PDFs were provided; not fabricated.
3. Official evaluation/submission documentation — `utils/validate_submission.py` (code, not prose — authoritative for format rules it implements).
4. Knowledge Base (`AMAZON_ML_CHALLENGE_MASTER.md`) — used, cross-checked against #1–3, found consistent.
5. `Amazon ML Challenge Forensic Analysis.md` — used for meta-patterns only; its year-by-year specifics are `[PARTICIPANT]`/`[SECONDARY]`/`[UNVERIFIED]`, explicitly self-labelled in many rows as "not publicly verified from accessible primary sources."
6. `graphify-out` knowledge graph — used as a structural cross-check (community coverage, "surprising connections," flagged knowledge gaps) before finalizing §4–§6 below.
7. Winner/finalist write-ups cited inside the Forensic Analysis (2023 "ART in Artificial Intelligence," 2024 "NeuralNinjas," 2025 "SPAM_LLMs," "NeelDevenShah") — `[WINNER/FINALIST]`/`[PARTICIPANT]` for *different competition years and different task types* (classification, regression, image entity extraction, price regression). None solved entity resolution. Treated strictly as engineering-discipline evidence, never as architecture evidence.
8. Papers/research articles — none were supplied locally; none invented.
9. Secondary sources (Medium/Reddit/GitHub posts cited by the Forensic Analysis) — lowest priority, already several hops removed from official material.

Where #1–3 conflict with each other (the leaderboard-basis conflict in §2), that conflict is recorded, not resolved. Where #5/#7 conflict with #1–3 (e.g., any historical rule vs. 2026's actual rules), #1–3 wins outright — historical rules are never treated as current.

---

## 4. Known Facts vs. Inferences vs. Unknowns

### HIGH CONFIDENCE (official, directly verified)
- Task definition, schema, output format, validator behavior, F0.5 formula and singleton scoring, model license/size cap, external-lookup ban, challenge window, submission limits — all `[OFFICIAL]`, all read directly from primary sources, all cross-checked against the real data files where applicable.
- Actual dataset scale (row counts in §2) — measured directly, not sourced from any document.

### MEDIUM CONFIDENCE (inference from official text, low ambiguity)
- Blocking recall ceiling is the primary lever (`[INFERENCE]` from Problem statement p.7 tips + the mathematical scale of the data — directly measured, not asserted by the PDF).
- Country must be handled as a fully open set, including at the blocking-key level, not just the model layer (`[INFERENCE]` — the PDF states the modeling requirement; extending it to blocking keys is our engineering conclusion).
- Whether pretrained open-source models (e.g., a small pretrained sentence-embedding model) are permitted at all, so long as they satisfy the license/size cap and make no external calls at inference time (`[INFERENCE]` — the license/size rule as written presupposes teams *do* use a licensed pretrained model of some kind; the external-lookup ban is specifically about looking up business identity, not about model provenance). **Flagged as a question for the user in §32 rather than assumed silently**, because getting this wrong (using a model that turns out to be disallowed) risks disqualification.

### LOW CONFIDENCE / UNVERIFIED (carried from the Forensic Analysis, not to be treated as 2026 rules)
- That a Top‑10 Grand Finale / live interview stage with Amazon Scientists happens in 2026, or that any specific "question bank" reflects 2026 reality — neither 2026 official document mentions a finale, presentation, or interview at all. The Forensic Analysis projects this from 2021–2025 patterns. `[UNVERIFIED for 2026]`.
- All 2021–2025 per-year numeric details (dataset sizes, team names, exact hyperparameters, scores) in the Forensic Analysis — most rows in that document's own timeline table read "Not publicly verified from accessible primary sources," and the winner write-ups are sourced from Medium/Reddit/GitHub, several hops from Amazon. `[PARTICIPANT]`/`[SECONDARY]`/`[UNVERIFIED]`.
- Whether the private test set's country/source-pairing distribution mirrors the public subset — undocumented in both PDFs. `[UNKNOWN]`.
- Any hardware/runtime/inference-latency/package-size limit — not documented anywhere. `[UNKNOWN]` (treated as an engineering risk, not a rule, in §21).

---

## 5. Critical Constraints (hard gate — violating any of these invalidates a submission or the whole entry)

| # | Constraint | Source | Enforcement |
|---|---|---|---|
| C1 | Output must be exact-format TSV per schema in §2 | `[OFFICIAL]` | Automatic rejection ("submissions that fail validation will not be evaluated") |
| C2 | Every test S1 entity appears exactly once | `[OFFICIAL]` | Rejection |
| C3 | No duplicate IDs within a list; no duplicate `source1_entity_id` rows | `[OFFICIAL]` | Rejection |
| C4 | `matched_entity_ids` only reference S2/S3 IDs that exist in the **test** set; no S1 self-matches | `[OFFICIAL]` | Rejection |
| C5 | Model: MIT or Apache‑2.0 license, ≤8B parameters | `[OFFICIAL]` | Package audit; violation = disqualification risk |
| C6 | No external identity lookup / geocoding / commercial ER API / internet augmentation, at any pipeline stage | `[OFFICIAL]` | Code review; **immediate disqualification** |
| C7 | Desktop/laptop only, one login per participant | `[OFFICIAL]` | Platform enforcement; may terminate session |
| C8 | Final submission zip structure exactly as specified (`output/`, `code/business_entity_resolution/{src,README.md,requirements.txt}`, `Documentation_template.md`) | `[OFFICIAL]` | Package review |
| C9 | ≤5 leaderboard submissions/day, 3 days total | `[OFFICIAL]` | Platform enforcement |

---

## 6. Competition Forensic Insights (translated into engineering decisions)

Only insights that survive the evidence check are carried forward as decisions. Each entry follows: evidence → official/inferred → historical support → implementation effect → test → what would invalidate it.

| Insight | Evidence | Class | Implementation effect | Test | Invalidated by |
|---|---|---|---|---|---|
| Baseline-first, refine-don't-swap | Forensic Analysis §10 ("ART in AI" 2023 timeline) | `[PARTICIPANT]`, single anecdote, different task | Phase 3 baseline is mandatory before any modeling complexity (§10) | Time-boxed: baseline complete before any Phase 6 model beyond Level 1–2 | If baseline can't reach any meaningful F0.5 signal at all (data/format bug) |
| EDA-first / 80-20 rule | Forensic Analysis §10 (NeelDevenShah 2025) | `[PARTICIPANT]` | Phase 1 (Data Forensics) is a hard gate before Phase 5/6 | Phase 1 exit criteria in §19 | N/A — low-risk, high-value regardless of source reliability |
| Exact format compliance is a binary pass/fail gate historically | Forensic Analysis §10, §11 (2024 OCR teams scored 0 despite good models) | `[PARTICIPANT]`, but consistent with our own `[OFFICIAL]` reading of the validator and constraint C1–C4 | `utils/validate_submission.py` run before **every** submission, no exceptions (Phase 13) | Automated pre-submit hook | N/A — independently confirmed by official validator + rules |
| Local validation must precede leaderboard chasing to avoid private-LB shakeup | Forensic Analysis §10, §13 (2025 "SPAM_LLMs" rank 5 private vs public) | `[PARTICIPANT]` | Phase 2 validation protocol is mandatory before Phase 3 baseline is trusted | Compare local F0.5 vs public LB score trend over first submissions | If local holdout distribution turns out to diverge sharply from test (see Phase 10) |
| Compute-constrained quantization/LoRA is essential *if* using multi-billion-param neural models | Forensic Analysis §10, §11 (2024/2025 VLM fine-tunes) | `[PARTICIPANT]`, **different task/modality (vision-language, not string matching)** | Only relevant if Phase 6 model ladder reaches a large pretrained encoder; not assumed necessary for entity resolution, which is traditionally solved with classical/tree-based matchers | Phase 6 ladder decision — climb only if evidence justifies it | If classical blocking + tree-based matcher already saturates local F0.5 (likely, given the task) |
| Grand Finale / interview defense with Amazon Scientists | Forensic Analysis §8 | `[UNVERIFIED for 2026]` — not in either 2026 official doc | Phase 16 kept, but explicitly marked **contingent and low-priority** until top‑100 status is confirmed or Amazon publishes finale details | N/A until triggered | Confirmed either way once/if top‑100 announcement details arrive |
| Precision-heavy metrics historically reward conservative thresholding (F1 2024, SMAPE 2025 as loose analogues) | Forensic Analysis §3 | `[INFERENCE]`, cross-task analogy, not a proof | Reinforces (does not solely establish) the `[OFFICIAL]` F0.5 precision-weighting already in §2 | Phase 4 metric forensics with synthetic examples (not the analogy) | The `[OFFICIAL]` F0.5 formula itself is the actual authority — this row is redundant confirmation, not new evidence |

`graphify-out/GRAPH_REPORT.md` cross-check: its community structure (8 communities: Modeling Principles & Deliverables, Past Editions & Support, Documentation & Feature Design, Submission Files & Validation, ER Task & Dataset, Rules & Leaderboards, Forensic Analysis & Finale, F0.5 Metric & Thresholding) maps onto every phase below with no orphaned topic area. Its own "Knowledge Gaps" section flags the same leaderboard-conflict node cluster identified independently in §2 — treated as corroboration, not new evidence.

---

## 7. Phase 0 — Ground Truth & Constraints

**Goal:** No material assumption about the challenge remains unverified before engineering starts.

| ID | Task | Action | Evidence | Status |
|---|---|---|---|---|
| P0-001 | Verify problem statement & task definition | Done — §2 | `[OFFICIAL]` | ✅ Complete |
| P0-002 | Verify dataset schema & files | Done — §2, plus direct header read of all 7 TSVs | `[OFFICIAL]` | ✅ Complete |
| P0-003 | Verify target definition | `matched_entity_ids` per S1 entity — done | `[OFFICIAL]` | ✅ Complete |
| P0-004 | Verify metric formula & aggregation | Done — §2 | `[OFFICIAL]` | ✅ Complete |
| P0-005 | Verify submission format & validator behavior | Done — read `utils/validate_submission.py` source in full | `[OFFICIAL]` | ✅ Complete |
| P0-006 | Verify rules/constraints (C1–C9) | Done — §5 | `[OFFICIAL]` | ✅ Complete |
| P0-007 | Verify allowed/disallowed resources | Done — external lookup ban, license/size cap (§5 C5–C6) | `[OFFICIAL]` | ✅ Complete |
| P0-008 | Verify compute constraints | **No hardware/runtime/package-size limit found in any document.** | `[UNKNOWN]` | ⚠ Open — treated as risk R-11 in §21, not blocking |
| P0-009 | Verify external-data restriction scope | Done — §5 C6. Ambiguity remains on pretrained-model provenance (§4) | `[OFFICIAL] + [INFERENCE gap]` | ⚠ Open — user question Q1 in §32 |
| P0-010 | Verify evaluation process (public/private) | Done — conflict recorded in §2 | `[OFFICIAL — internal conflict]` | ⚠ Open — recorded, not blocking (strategy in §1 satisfies both readings) |

**Deliverables:** this section + §2 (verified spec table) + §5 (constraint checklist) + §32 (unresolved-question list).

**Exit criteria (met):** No material challenge assumption remains unverified except the two explicitly flagged, non-blocking items (P0-008 compute ceiling, P0-009 pretrained-model provenance), both routed to §32 for user confirmation rather than guessed.

---

## 8. Phase 1 — Data Forensics

**Goal:** Full empirical understanding of the real training/test data before any modeling. Nothing here has been executed yet beyond the row-count/header sampling already recorded in §2 — this phase is the actual EDA work.

| ID | Task | Input | Deliverable |
|---|---|---|---|
| P1-001 | Full schema/dtype validation across all 7 TSVs (tab-delimited parse, column count, encoding) | raw TSVs | `data_quality_report.md` §schema |
| P1-002 | Row-count and uniqueness audit: confirm `train_source1` entity_ids are unique (it's billed as "deduplicated reference"); confirm `train_ground_truth` covers exactly the `train_source1` ID set 1:1 (already suggestive from matching line counts in §2, not yet formally verified) | train_source1, train_ground_truth | data_quality_report.md §uniqueness |
| P1-003 | Null/empty-field audit per column, per source, per country | all sources | data_quality_report.md §missingness |
| P1-004 | Duplicate & near-duplicate record detection within S2 and within S3 (same business appearing twice under different IDs) | S2, S3 | data_quality_report.md §duplicates |
| P1-005 | Country distribution per file (confirm France absent from train, present in test only; get exact per-country row counts) | all sources | data_quality_report.md §country |
| P1-006 | Match cardinality distribution from `train_ground_truth`: % singleton (empty), 1-match, 2+match; max matches per S1 entity | train_ground_truth | data_quality_report.md §cardinality |
| P1-007 | Match-count by source: what fraction of matched IDs are S2- vs S3- prefixed | train_ground_truth | data_quality_report.md §source split |
| P1-008 | Text statistics: `business_name`/`business_address` length distributions, character-set/encoding audit (Unicode/transliteration present — already seen directly in S2/S3 samples, e.g. Devanagari business names) | all sources | data_quality_report.md §text stats |
| P1-009 | Noise-pattern census: sample and quantify frequency of each noise type listed in §2 (abbreviations, DBA, punctuation, transpositions, typos; address abbreviations, transliteration, missing PIN/state, landmarks, reordering) | all sources | data_quality_report.md §noise census |
| P1-010 | Train/test distributional comparison per country, per field-length, per noise-pattern frequency (detect if test genuinely differs beyond the known France addition) | train vs test | data_quality_report.md §train/test drift |
| P1-011 | Leakage-candidate audit: any field/pattern in S1 that trivially predicts a match without genuine name/address similarity (e.g., ID numbering correlated with match order) | all sources | leakage_risk_report.md |
| P1-012 | Malformed-record audit: rows that fail the tab-split, rows with wrong column count, mixed encodings | all sources | data_quality_report.md §malformed |

**For every discovered anomaly:** quantify (exact count/%), identify affected entity_ids, determine systematic vs. sporadic, and record a clean/transform/exclude/retain decision with rationale — no silent cleaning.

**Deliverables:** `data_quality_report.md`, `leakage_risk_report.md`, plus reusable profiling scripts under `code/business_entity_resolution/src/eda/`.

**Exit criteria:** schema verified; quality profiled; leakage risks documented; train/test differences measured; anomalies categorized with explicit decisions. (Per §19 decision gate.)

---

## 9. Phase 2 — Validation Strategy (mandatory, before tuning)

**Goal:** A validation protocol that reflects the actual competition metric and won't quietly diverge from hidden-test behavior.

| ID | Task | Decision driver |
|---|---|---|
| P2-001 | Split `train_source1` (and its ground truth) into train/holdout at the **S1-entity level**, grouped so no S1 entity's matched S2/S3 records leak across the split via shared blocking keys | `[INFERENCE]` — prudent for matching data; not an official requirement, stated as such |
| P2-002 | Stratify the holdout by country and by singleton/matched status, so F0.5 on the holdout isn't dominated by one slice | Directly follows from §2's country and singleton rules |
| P2-003 | Implement the **exact** official F0.5 aggregation (per-entity, macro-averaged, singleton-inclusive) as a standalone, independently tested function — this is the single most important piece of code in the whole project | `[OFFICIAL]` formula, §2 |
| P2-004 | Hand-verify the F0.5 implementation against the worked example in the Problem statement (P=2/3, R=1.0 → F0.5=0.714) plus 4–5 additional hand-computed synthetic cases (perfect match, total miss, correct singleton, false-merge singleton, partial overlap) | `[OFFICIAL]` worked example, p.6 |
| P2-005 | Decide k-fold vs. single held-out split based on variance observed once P2-003/004 exist (data-driven, not assumed upfront) | Evidence-dependent |
| P2-006 | Build edge-case test fixtures: missing values, empty business_name/address strings, malformed text, rare/unseen country beyond France (synthetic), duplicate candidate IDs, extreme-length names/addresses, unusual Unicode | Derived from §2 noise patterns + open-set country rule |
| P2-007 | Reserve a final validation slice untouched during all feature/threshold iteration (distinct from the working holdout) to catch overfitting to our own iteration loop | `[INFERENCE]`, explicitly labeled as prudent practice, not an official requirement |

**Deliverable:** `VALIDATION_PROTOCOL.md` + `code/business_entity_resolution/src/eval/f05_metric.py` (with its own unit tests).

**Exit criteria:** split strategy justified and grouped correctly; official metric implemented and hand-verified; leakage tests pass; edge cases enumerated and testable.

---

## 10. Phase 3 — Baseline

**Goal:** Simplest credible end-to-end pipeline, run before any optimization.

| ID | Task |
|---|---|
| P3-001 | Trivial blocking baseline: exact-normalized-name match (lowercase, strip punctuation/legal suffixes) plus same-country filter, as the candidate generator |
| P3-002 | Trivial matching baseline: candidate accepted as a match if normalized name is identical (or above a fixed high string-similarity threshold); everything else → singleton |
| P3-003 | Generate `candidate_pairs.tsv` and `matching_results.tsv` on the holdout, score with P2-003's F0.5 implementation |
| P3-004 | Run `utils/validate_submission.py` against the baseline output on a small local test slice to confirm the pipeline is format-correct end-to-end, before ever touching the real test set |
| P3-005 | Record: config, seed, preprocessing steps, holdout F0.5, blocking recall ceiling, reduction ratio, wall-clock runtime, peak memory |

**Deliverable:** `baseline_v0` run recorded in the experiment log (Phase 14), establishing the reference point for every later change.

**Exit criteria:** end-to-end pipeline runs on the full data without OOM/crash, produces validator-passing output, and yields a nonzero, sane holdout F0.5. Do not optimize before this exists.

---

## 11. Phase 4 — Metric Forensics

**Goal:** Understand F0.5's mathematical behavior before choosing objectives/thresholds.

| ID | Task |
|---|---|
| P4-001 | Construct synthetic per-entity scenarios sweeping precision/recall combinations; plot the F0.5 surface to make the 2× precision weighting concrete (not just stated) |
| P4-002 | Quantify singleton sensitivity: with X% true singletons in `train_ground_truth` (measured in Phase 1, P1-006), compute how much overall macro F0.5 moves per percentage-point change in singleton false-merge rate vs. per percentage-point change in matched-entity recall |
| P4-003 | Determine threshold sensitivity: sweep the match/no-match decision threshold on the P2 holdout and plot F0.5 vs. threshold to find the actual optimum, rather than assuming 0.5 |
| P4-004 | Confirm (via P4-001/003) that optimizing threshold directly on F0.5 differs measurably from optimizing a proxy (e.g., raw accuracy or plain F1) — do not optimize a proxy metric without this evidence |

**Deliverable:** `metric_forensics.md` with plots/tables, feeding directly into P5 feature priorities and P6 model objective choice (loss/threshold selection must target F0.5, not a generic classification loss).

**Exit criteria:** metric behavior is characterized with evidence, not assumed from the formula alone.

---

## 12. Phase 5 — Feature & Representation Engineering

Only features supported by the actual data (per Phase 1) and justified by Phase 4's metric behavior are built. Candidate families, gated by the noise patterns confirmed in §2/P1-009:

| ID | Feature family | Hypothesis | Leakage check | Cost |
|---|---|---|---|---|
| P5-001 | Name normalization (case, punctuation, legal-suffix dictionary: Corp/Corporation, Pvt/Private, Ltd/Limited, & vs "and") | Reduces surface noise before any similarity computation | None — deterministic transform | Low |
| P5-002 | Address normalization (Rd/Road, St/Street dictionary; component splitting where possible) | Same rationale for addresses | None | Low |
| P5-003 | Token-overlap / Jaccard similarity (name, address) | Explicitly suggested by the official Tips (`[OFFICIAL]`, Problem statement p.7) | None | Low |
| P5-004 | Levenshtein / edit-distance similarity (name, address) | Explicitly suggested (`[OFFICIAL]`) — catches typos | None | Medium (pairwise cost at scale) |
| P5-005 | TF‑IDF cosine similarity (name, address) | Explicitly suggested (`[OFFICIAL]`) | None | Medium |
| P5-006 | Phonetic encoding (e.g., Soundex/Metaphone) as an additional blocking key | Historical ER practice; catches transliteration-driven spelling variance | None | Low |
| P5-007 | Country-aware address parsing, without requiring a closed country set (must degrade gracefully for France) | `[OFFICIAL]` open-set requirement, §2 | Must explicitly test on synthetic unseen-country input (P2-006) | Medium |
| P5-008 | Blocking-key inverted index (name n-grams / address tokens / phonetic code) as the actual candidate generator | Required at this scale — see §1 point 1 | Recall measured, not assumed | High (engineering) |
| P5-009 (optional, gated) | Pretrained sentence-embedding similarity | Only pursued if P0-009 (pretrained-model provenance question, §32 Q1) is resolved favorably, and only if it beats P5-003–006 on the P2 holdout | Must confirm no network calls at inference | High |

Every feature family is scored against the P2 holdout with P2-003's exact metric, and its computational cost (P11) is recorded before acceptance. None is added "for completeness."

**Deliverable:** `feature_engineering_report.md`, one row per family, with the required hypothesis/implementation/leakage-check/validation-experiment/metric-impact/cost/failure-case fields.

---

## 13. Phase 6 — Model Ladder

Climbed only as far as evidence justifies — entity resolution is traditionally solved by classical/tree-based matchers over engineered pairwise features, not by defaulting to deep learning. This is our own engineering judgment, not sourced from the Forensic Analysis's unrelated-task winner write-ups.

| Level | Approach | Trigger to climb |
|---|---|---|
| L1 | Rule/threshold baseline over P5-001–006 features (already built in Phase 3) | Always the floor reference |
| L2 | Classical ML pair-classifier (logistic regression) over engineered similarity features | Climb if L1's holdout F0.5 leaves clear, characterized headroom (Phase 7 error buckets identify *what kind* of headroom) |
| L3 | Gradient-boosted trees (e.g., XGBoost/LightGBM-class model) over the same feature set, with a decision threshold tuned via P4-003 | Climb if L2 underfits the pairwise similarity signal (measured, not assumed) |
| L4 | Deep learning (e.g., a small text-encoder pair model) | Climb only if L3 plateaus below a level Phase 7 error analysis attributes to representation limits, not threshold/feature limits |
| L5 | Pretrained embeddings (P5-009) | Gated by the §32 Q1 provenance question; only attempted after L3/L4 establish a clear, quantified gap pretrained embeddings could plausibly close |
| L6 | Multimodal | Not applicable — the task has no image/second modality; explicitly out of scope |
| L7 | Ensemble/stacking of L2–L5 candidates | Only after Phase 9 gating (post individual models are strong and validated) |

For each model actually built: architecture, input representation, parameter count (must respect C5's 8B cap if any pretrained component is used), training config, holdout F0.5 (mean and variance across seeds), runtime, memory, and a documented set of failure cases from Phase 7.

**Deliverable:** `model_ladder_log.md`, one entry per level actually attempted (levels are not attempted out of order or skipped without a documented reason).

---

## 14. Phase 7 — Error Forensics

**Goal:** Systematic, not anecdotal, error analysis — the highest-priority phase per the Forensic Analysis's own repeated failure-mode warnings (§11 of that document), independently justified here by the fact that F0.5's precision weighting means *which* errors you make matters more than *how many*.

| ID | Bucket | What to quantify |
|---|---|---|
| P7-001 | False merges on true singletons | Count, which country/source pairing, what similarity score they had (near-threshold vs. confidently wrong) |
| P7-002 | Missed true matches (false negatives) | Were they lost at blocking (recall ceiling problem) or at matching (threshold problem) — this distinction changes which phase to fix |
| P7-003 | Partial-match entities (some correct, some wrong IDs in the predicted set) | Precision vs. recall balance per entity |
| P7-004 | Country-specific failure rates (US / India / France) | France is the adversarial case — must be reported separately, not averaged away |
| P7-005 | Name-noise-type failure rates (map back to the noise census from P1-009) | Which specific noise types (DBA names, transliteration, transposition) correlate with errors |
| P7-006 | Address-noise-type failure rates | Same, for address noise types |
| P7-007 | Long-tail / rare pattern failures | Records with unusually short/long names or addresses, or unusual token patterns |
| P7-008 | Duplicate/near-duplicate interaction effects | Whether S2/S3 near-duplicates cause spurious multi-matches |

Each bucket: root cause → hypothesis → intervention → experiment (Phase 8) → result, not random tuning.

**Deliverable:** `error_analysis_report.md`, refreshed after every Phase 6 model level and after significant Phase 5 feature changes.

---

## 15. Phase 8 — Ablation Studies

Every Phase 5/6 component must be independently testable against the Phase 3 baseline.

| Experiment | Change | Hypothesis | Validation | Delta | Runtime | Memory | Decision |
|---|---|---|---|---|---|---|---|
| A0 | Baseline (P3) | — | P2 holdout | — | recorded | recorded | Reference |
| A1 | + name normalization only | Reduces surface noise → recall/precision up | P2 holdout | TBD | TBD | TBD | TBD |
| A2 | + address normalization only | Same, for address | P2 holdout | TBD | TBD | TBD | TBD |
| A3 | + Jaccard/Levenshtein/TF-IDF features (L2 classifier) | Official-tip features improve discrimination over exact-match rule | P2 holdout | TBD | TBD | TBD | TBD |
| A4 | + phonetic blocking key | Improves recall ceiling on transliteration-heavy India/France records | P2 holdout, blocking recall specifically | TBD | TBD | TBD | TBD |
| A5 | L2 → L3 (GBT) | Non-linear combination of features improves over linear | P2 holdout | TBD | TBD | TBD | TBD |
| A6 | Threshold retuned via P4-003 vs. default 0.5 | Metric-aligned threshold beats default | P2 holdout | TBD | TBD | TBD | TBD |

Rows are filled in only as experiments actually run — this table starts empty of results by design; no result is pre-written.

**Deliverable:** `ablation_log.md`, append-only, feeding Phase 14's experiment tracker.

---

## 16. Phase 9 — Ensemble & Post-Processing

Only attempted after Phase 6/8 establish strong individual models with characterized error profiles.

| ID | Technique | Gate |
|---|---|---|
| P9-001 | Weighted blend of L2/L3 (and L4/L5 if built) pairwise scores | Only if models make measurably different error buckets (Phase 7) — blending similar-error models wastes complexity |
| P9-002 | Threshold recalibration post-blend | Re-run P4-003 sweep on the blended score, not reuse of a single-model threshold |
| P9-003 | Domain constraints as post-processing (e.g., cap matches per S1 entity if Phase 1 showed match-count is bounded in training) | Only if P1-006 supports a real bound, not an assumed one |
| P9-004 | Confidence-aware abstention (favor singleton prediction under low confidence) | Directly motivated by F0.5's precision weighting (§1, §4) |

Every technique here must show a measured F0.5 improvement on the **reserved** validation slice (P2-007), not just the working holdout, to guard against overfitting our own iteration loop (a specific form of leaderboard overfitting risk, R-2 in §21).

---

## 17. Phase 10 — Robustness & Hidden-Test Simulation

Assume the private test set can differ from what we can directly observe, since P0-010/§2 already shows Amazon's own two documents give inconsistent guidance about how the two leaderboards even combine — a concrete, documented reason not to over-trust the public leaderboard alone.

| ID | Stress test | Method |
|---|---|---|
| P10-001 | Unseen-country simulation beyond France (hold out a synthetic "fourth country" from training, or literally hold true France examples out of a training-time proxy) | Confirms no implicit closed-set assumption leaked in anywhere (blocking keys, encodings, thresholds) |
| P10-002 | Missing-field perturbation (blank address, blank name) | Confirms graceful degradation, not a crash or silent wrong-match |
| P10-003 | Extreme-length name/address perturbation | Confirms features don't break on outlier lengths |
| P10-004 | Duplicate-record perturbation | Confirms blocking/matching don't produce duplicate output IDs (violates C3) |
| P10-005 | Distribution-shift check: retrain on an artificially country-imbalanced subset of training, evaluate on the real, differently-balanced holdout | Measures sensitivity to the specific kind of shift the private set could plausibly contain |
| P10-006 | Malformed/adversarial-format input (extra whitespace, stray tabs inside a field, mixed encodings) | Confirms the pipeline fails safely, not silently |

Preference rule: a solution that holds up across P10-001–006 with a smaller local F0.5 margin is preferred over one that maximizes only the P2 working-holdout score.

**Deliverable:** `robustness_report.md`.

---

## 18. Phase 11 — Compute & Engineering Optimization

No hardware/runtime limit is documented (P0-008, `[UNKNOWN]`), but at ~10M+ records per source pair this is a real engineering constraint regardless of rules.

| ID | Task |
|---|---|
| P11-001 | Track wall-clock and peak RAM for blocking, feature computation, and matching-model inference separately, at every Phase 6/8 experiment |
| P11-002 | Identify the actual bottleneck stage (near-certainly blocking/candidate generation at this row count) before optimizing anything else |
| P11-003 | Batch/chunk processing for feature computation across the ~5M-record S2/S3 files to avoid OOM (the `validate_submission.py` docstring itself warns the full test set costs "a few GB" just to hold IDs in memory — a directly relevant, `[OFFICIAL]`-sourced signal of scale) |
| P11-004 | Cache/reuse normalized text and blocking-key computations across experiments instead of recomputing per run |
| P11-005 | If any pretrained model is used (L5, gated), profile its batched inference cost against C5's implicit expectation of local, non-API inference |

**Never** trade robustness for a small speed gain unless a documented constraint requires it (none currently documented).

---

## 19. Phase 12 — Reproducibility

| ID | Requirement |
|---|---|
| P12-001 | Pin Python version + all dependency versions in `requirements.txt` (required by C8 / the final package structure) |
| P12-002 | Fixed random seeds for every stochastic step (splits, any ML model training), recorded per experiment |
| P12-003 | Versioned config files per experiment (feature set, blocking params, threshold, model hyperparameters) |
| P12-004 | Dataset version pinning (the provided files are static per the challenge, but record checksums to detect accidental local corruption) |
| P12-005 | `code/business_entity_resolution/README.md` with exact, tested run commands from raw data → `output/matching_results.tsv` + `output/candidate_pairs.tsv` — must be verified by literally re-running it end-to-end before final packaging (directly required by the official package description, `[OFFICIAL]` Problem statement p.5) |
| P12-006 | Experiment ID / checkpoint naming convention (see Phase 14) |

---

## 20. Phase 13 — Submission Validation

`utils/validate_submission.py` is run **before every single leaderboard upload**, no exceptions — this is the one piece of official tooling directly available and directly authoritative for format rules (C1–C4).

| ID | Check | Source |
|---|---|---|
| P13-001 | Row count matches required S1 test entity count | validator + C2 |
| P13-002 | No duplicate `source1_entity_id` rows | validator + C3 |
| P13-003 | No duplicate IDs within a list | validator + C3 |
| P13-004 | Correct header, tab-delimited (not comma) | validator |
| P13-005 | Only S2-/S3- prefixed IDs, no self-matches | validator + C4 |
| P13-006 | `--check-ids` run at least once per major submission (even though off by default) to catch nonexistent IDs, memory permitting — this only lowers score if skipped, so run it whenever compute allows, not only when convenient | validator docstring |
| P13-007 | Matches ⊆ candidates (validator warning, not a hard fail) — treat as a hard internal gate anyway, since it signals a pipeline bug | validator + Problem statement p.4 |
| P13-008 | No NaN/empty malformed rows, correct encoding (UTF-8) | validator (UnicodeDecodeError handling in the script) |

A malformed submission must fail **locally** before ever reaching the portal, given the daily 5-submission cap (C9) makes a wasted submission costly.

---

## 21. Phase 14 — Experiment Management

Every experiment recorded with: ID, timestamp, hypothesis, dataset version, split version, feature set, model, hyperparameters, seed, holdout F0.5 (+ reserved-slice F0.5 once relevant), runtime, memory, artifact paths, and conclusion. Never overwrite a prior successful experiment's record.

Template row for `experiment_log.md`:

```
| exp_id | date | hypothesis | features | model | seed | holdout_F0.5 | reserved_F0.5 | runtime | mem | artifact | conclusion |
```

A running "local leaderboard" of all experiments is maintained so the best-so-far configuration is always identifiable without relying on memory.

---

## 22. Phase 15 — Final Model Selection

Selection is **not** simply "highest single holdout F0.5." Evaluated jointly:

| Criterion | Why it matters here specifically |
|---|---|
| Mean holdout F0.5 (P2 split) | Primary signal |
| Reserved-slice F0.5 (P2-007) | Guards against overfitting our own iteration loop |
| Variance across seeds | A high-variance model is a bad bet against an undocumented private-set distribution (§17) |
| Error profile (Phase 7) | A model with fewer *false-merge* errors is preferred at equal F0.5, since F0.5's precision weighting means those errors are structurally worse for score stability |
| Robustness (Phase 10 results) | Directly motivated by the unresolved leaderboard-combination conflict (§2) |
| Compute cost (Phase 11) | Must be practically re-runnable to reproduce the package (C8) |
| Complexity vs. C5 (license/size cap) | Any model must be independently confirmed MIT/Apache‑2.0, ≤8B params before it can be finalized |
| Reproducibility (Phase 12) | Must literally re-run from the packaged code before submission |

**Deliverable:** `final_model_selection.md` with the comparison table and a written rationale — no unexplained pick.

---

## 23. Phase 16 — Finalist / Amazon Technical Defense (contingent, low-priority until triggered)

Per §4/§6, no 2026 official document confirms a finale/interview stage exists. This phase is retained (the Forensic Analysis's historical pattern is a reasonable hedge) but is explicitly **not prioritized** over Phases 0–15, and is only actively prepared once top‑100 status is confirmed or Amazon publishes finale details.

Prepared question categories (adapted from Forensic Analysis §8, all `[UNVERIFIED for 2026]`, to be answered only with evidence from our own experiments, never invented):

- **Problem understanding:** Why is cross-source entity resolution structurally hard at this scale? What is the actual recall ceiling our blocking stage achieves, and why?
- **Data:** What anomalies did Phase 1 find? How was leakage checked and ruled out (P1-011)? Why was France handled the way it was?
- **Modeling:** Why was the model ladder stopped where it was (Phase 6 decision log)? What did the ablations (Phase 8) actually show?
- **Validation:** Why this split strategy (P2-001)? How was leakage prevented specifically?
- **Error analysis:** What are the largest documented failure modes (Phase 7)? What interventions measurably helped?
- **Engineering:** What is the actual candidate-generation and inference runtime/memory profile (Phase 11)?
- **Generalization:** What do the Phase 10 robustness results show, specifically for the France/unseen-country case?
- **Reproducibility:** Can the packaged `code/business_entity_resolution/` regenerate both output files from scratch (P12-005, actually tested)?

Every answer must cite a specific artifact from Phases 1–15 (a report file, a table row, a number) — no answer may be improvised at defense time.

---

## 24. Test Case Matrix

### Data tests
Empty dataset · single-row dataset · duplicate rows · fully-missing feature column · unseen country (synthetic, beyond France) · malformed country string · extremely long name/address · empty-string name/address · Unicode/transliterated text (already directly observed in S2, e.g. Devanagari names) · malformed TSV row (wrong column count) · file read as CSV by mistake (the documented #1 trap, C1-adjacent)

### Pipeline tests
Preprocessing determinism (same input → same normalized output) · train/inference feature parity (no train-only feature computed differently at inference) · serialization/deserialization of any trained model/index · deterministic inference given a fixed seed · batch size = 1 vs. full-batch equivalence · restart-from-checkpoint correctness

### Model tests
Expected output shape/type for a given candidate set · behavior on an empty candidate list (must correctly emit a singleton) · behavior on an all-identical-candidate edge case · reproducibility with a fixed seed

### Metric tests
The 5 hand-computed synthetic cases from P2-004, including the official worked example (P=2/3, R=1.0 → F0.5=0.714), verified byte-for-byte against our implementation.

### Submission tests
All of P13-001–008, run automatically before every submission, no manual override.

---

## 25. Experiment Prioritization

Every proposed experiment (Phase 5/6/8/9) is scored 1–5 on Impact, Confidence, Cost, Risk before being run. Priority = high Impact × high Confidence × manageable Cost × low catastrophic Risk.

| Experiment class | Impact | Confidence | Cost | Risk | Priority |
|---|---|---|---|---|---|
| Blocking key coverage (P5-008) | 5 | 5 | 3 | 2 | **Highest — recall ceiling gates everything** |
| Official-tip similarity features (P5-003–005) | 4 | 5 | 2 | 1 | **High** |
| Threshold tuning to F0.5 (P4-003, A6) | 4 | 5 | 1 | 1 | **High** |
| Country-aware but open-set address parsing (P5-007) | 3 | 3 | 3 | 2 | Medium |
| Classical → GBT model climb (A5) | 3 | 3 | 2 | 1 | Medium |
| Phonetic blocking key (P5-006/A4) | 3 | 3 | 2 | 2 | Medium |
| Pretrained embeddings (P5-009/L5) | 2 | 2 (gated by unresolved provenance question) | 4 | 4 (compliance risk if provenance assumption is wrong) | **Low until Q1 resolved** |
| Ensemble/blend (Phase 9) | 2 | 2 (until individual models are strong) | 3 | 2 | Low until gated by Phase 6/8 evidence |

No blind large-scale experiment sweep is planned; each row above must individually clear its own gate before running.

---

## 26. Decision Gates

| Phase | Exit only when |
|---|---|
| Phase 0 | No material assumption unverified; both open items routed to §32, not guessed (met — see §7) |
| Phase 1 | Schema verified; data quality profiled; leakage risks documented; train/test differences measured; anomalies categorized with explicit decisions |
| Phase 2 | Split strategy justified and grouped; official metric implemented and hand-verified against the worked example; leakage tests pass; edge cases enumerated |
| Phase 3 | End-to-end pipeline runs on full data without crash/OOM; validator-passing output; nonzero sane holdout F0.5 |
| Phase 4 | Metric behavior characterized with synthetic evidence, not assumed from the formula alone |
| Phase 5 | Each accepted feature family has a measured, positive holdout delta and a recorded cost |
| Phase 6 | Each model level attempted only after the prior level's headroom is characterized by Phase 7, not assumed |
| Phase 7 | Error buckets quantified with root-cause hypotheses, not just aggregate score deltas |
| Phase 8 | Every claimed improvement has an ablation row with a measured delta |
| Phase 9 | Ensembling only attempted on models with demonstrably different error profiles |
| Phase 10 | Robustness results exist for all 6 stress tests before final model selection |
| Phase 11 | Bottleneck stage identified with numbers, not guessed |
| Phase 12 | Packaged code literally re-run end-to-end and confirmed to reproduce both output files |
| Phase 13 | Validator passes with zero errors before every submission, no exceptions |
| Phase 15 | Selection table (§22) complete with written rationale before any file is finalized |

---

## 27. Stop Conditions

Stop pursuing a given approach when:
- No statistically meaningful F0.5 improvement over the current best (accounting for seed variance measured in Phase 15).
- Compute cost makes the approach impractical to re-run for the reproducibility requirement (C8/P12-005).
- A validation improvement is traced to a leakage source (Phase 1/P1-011 or a newly discovered one) rather than genuine signal.
- Performance is unstable across seeds beyond what Phase 15's variance criterion tolerates.
- Robustness (Phase 10) degrades materially versus the current best, even if the working-holdout score is higher.
- The approach would violate C5/C6 (license/size cap or external-lookup ban) — stop immediately, no exception, regardless of performance.
- The packaged code cannot be independently re-run to reproduce the claimed result (P12-005 fails).

---

## 28. Risk Register

Probability/impact ratings below are our own engineering assessment, not any official Amazon judgment.

| Risk | Evidence | Probability | Impact | Detection | Mitigation | Status |
|---|---|---|---|---|---|---|
| R-1 Data leakage in validation split | General ER risk; not yet tested locally | Medium | High | P1-011, P2-001 leakage checks | Entity-grouped split, dedicated leakage audit | Open — Phase 1/2 pending |
| R-2 Overfitting to our own iteration loop / public leaderboard | `[PARTICIPANT]` historical precedent (Forensic Analysis §13) + `[OFFICIAL]` documented public/private split | Medium | High | Reserved validation slice (P2-007) diverging from working holdout | Never tune on reserved slice; track divergence | Open — mitigated by design |
| R-3 Blocking recall ceiling too low | Mathematical necessity at ~5M-record scale | Medium-High | Critical (caps max achievable score regardless of matcher quality) | `candidate_pairs.tsv` recall audit (P1-006 + P5-008 validation) | Multiple complementary blocking keys (P5-008), measured not assumed | Open — Phase 5 pending |
| R-4 Country-closed-set assumption leaking into blocking/encoding | `[OFFICIAL]` explicit warning, §2 | Medium | High (breaks on ~1/3 of test countries) | P10-001 unseen-country simulation | Explicit open-set design from the start, tested | Open — Phase 10 pending |
| R-5 Model license/size non-compliance | `[OFFICIAL]` C5 | Low (if avoided by design) | Critical (disqualification) | Manual audit of any pretrained component before finalization | Prefer classical/tree-based models unless a compliant pretrained option is confirmed (§32 Q1) | Open — gated |
| R-6 External-lookup violation (even inadvertent, e.g. a library that calls a geocoding API) | `[OFFICIAL]` C6 | Low | Critical (immediate disqualification) | Dependency audit; network-call audit of all libraries used | No network calls anywhere in the pipeline; explicit dependency review before packaging | Open — Phase 12 pending |
| R-7 Public/private leaderboard combination ambiguity (§2 conflict) | `[OFFICIAL vs OFFICIAL]` | N/A (documented fact) | Medium (affects which score to optimize for) | N/A | Optimize for robust private-leaderboard-generalizing performance, which satisfies both readings | Recorded, non-blocking |
| R-8 Wasted submissions against the 5/day cap due to format errors | `[OFFICIAL]` C9 + validator rules | Low if Phase 13 followed | Medium (costs a submission slot) | Automated pre-submit validator run | Zero-exception validator gate (Phase 13) | Mitigated by design |
| R-9 Compute/memory failure at full data scale | Directly evidenced by the validator's own memory warning for `--check-ids` at ~1.7M-4.9M IDs | Medium | Medium (delays, not disqualification) | Chunked processing (P11-003), memory profiling | Batch/stream processing throughout | Open — Phase 11 pending |
| R-10 Finale/interview stage assumption (Phase 16) consumes effort not actually needed for 2026 | `[UNVERIFIED for 2026]` | Unknown | Low (only wastes prep time if wrong) | Confirm via official channels once top‑100 is relevant | Kept explicitly low-priority/contingent | Recorded |
| R-11 Undocumented hardware/runtime limit surprises us at submission time | `[UNKNOWN]`, P0-008 | Unknown | Medium | N/A locally | Keep pipeline resource-conscious regardless (Phase 11) as a hedge | Open, non-blocking |

---

## 29. Research Loop

Applied to every uncertain technical decision in this project:

`Question → Evidence (which phase/report) → Hypothesis → Experiment (Phase 8 ablation or Phase 10 stress test) → Result (logged in Phase 14) → Decision (recorded in the relevant phase's log)`

Never `Question → Guess → Implementation`. Concretely: no feature, model, or post-processing technique enters the final pipeline without a corresponding row in `ablation_log.md` or `robustness_report.md`.

---

## 30. Final Pre-Submission Checklist

- [ ] `utils/validate_submission.py` passes with zero errors on the actual `output/matching_results.tsv` and `output/candidate_pairs.tsv`
- [ ] Every test `S1` entity present exactly once (C2)
- [ ] No duplicate IDs within any list, no duplicate `source1_entity_id` rows (C3)
- [ ] All matched/candidate IDs are S2-/S3- prefixed and exist in the test set (C4) — confirmed with `--check-ids` at least once (P13-006)
- [ ] `matching_results.tsv` IDs ⊆ `candidate_pairs.tsv` IDs per entity (soft validator check, treated as hard internally, P13-007)
- [ ] Model license confirmed MIT/Apache‑2.0, parameter count confirmed ≤8B (C5)
- [ ] No external lookup/API/network call anywhere in the pipeline, dependency-audited (C6)
- [ ] Final zip structure matches the official layout exactly: `output/`, `code/business_entity_resolution/{src,README.md,requirements.txt}`, `Documentation_template.md` (C8)
- [ ] `code/business_entity_resolution/README.md` commands independently re-run end-to-end and confirmed to reproduce both output files (P12-005)
- [ ] `requirements.txt` pinned and matches the actual environment used
- [ ] `Documentation_template.md` filled in with methodology, blocking strategy, model/features, results (required topics per §2)
- [ ] Version history of submissions maintained (Guidelines requirement)
- [ ] Submission count for the day checked against the 5/day cap (C9)

---

## 31. Finalist Preparation Checklist (contingent — see Phase 16)

- [ ] Confirm (via the official Google Form channel named in the guidelines, or any later Amazon communication) whether a finale/interview stage actually applies in 2026 before investing significant prep time
- [ ] If confirmed: every prepared answer in Phase 16 cites a specific artifact (report file, table, number) from Phases 1–15
- [ ] Blocking recall ceiling and reduction ratio numbers ready to state exactly
- [ ] Error analysis buckets (Phase 7) ready to summarize with root causes and interventions
- [ ] Robustness results (Phase 10), especially the France/unseen-country case, ready to summarize
- [ ] Reproducibility demonstrably proven, not just claimed (P12-005 actually re-run)

---

## 32. Evidence Gaps / Questions For Me

Only questions genuinely unresolved after consulting graphify → Forensic Analysis → Master KB → original PDFs, per the required order, are listed here.

**Q1 — Pretrained model provenance.** The external-lookup ban (C6) explicitly targets looking up business *identities* (commercial ER APIs, government registries, geocoding APIs, internet augmentation). The license/size rule (C5) implies teams are expected to use *some* model, and MIT/Apache‑2.0 + ≤8B is a licensing/size constraint, not a "must be trained from scratch" constraint. Neither document explicitly states whether using a generic pretrained open-source model (e.g., a small pretrained sentence-embedding model, used purely as a fixed local feature extractor with no network calls) is permitted, versus whether "external data" is meant to cover any data the model was pretrained on. **This materially affects whether Phase 6 Level 5 (pretrained embeddings) is even in scope**, and getting it wrong risks disqualification (C6 is an immediate-DQ clause). Neither `graphify-out`, the Forensic Analysis, nor the Master KB resolves this (the Master KB flags the same ambiguity independently in its §17 "Evidence Gaps," as `[OFFICIAL, model license/size], [gap: pretrained model legality]`). **Please confirm, or tell me whether to treat this as "assume disallowed" (safest) or "assume allowed for local, non-API, license-compliant models" for planning purposes** — the plan currently defaults to treating it as gated/low-priority (§13 L5, §25) rather than assumed either way.

**Q2 — Finale/interview stage for 2026.** Neither the problem statement nor the guidelines PDF mentions a Top‑10 finale, live presentation, or Amazon Scientist interview for 2026 — this only appears in the Forensic Analysis as a projection from 2021–2025 patterns. Do you have a source (e.g., the "Prep before you start" blog link referenced in the guidelines, or the referenced problem-statement explainer video) confirming whether this stage exists in 2026, so Phase 16 prep can be prioritized appropriately rather than left contingent?

**Q3 — Leaderboard-combination conflict.** The problem statement says final ranking is based purely on the private leaderboard; the guidelines say shortlisting considers both leaderboards. This is recorded as an internal document conflict in §2 rather than resolved. If you have clarification (e.g., from the Google Form Q&A channel mentioned in the guidelines), it would let Phase 15's selection criteria be tuned more precisely — though the current strategy (optimize for robust, private-leaderboard-generalizing performance) already satisfies both readings, so this is lower-urgency than Q1/Q2.

No other question is asked here — everything else resolvable from the local files has been resolved above rather than deferred.

---

## 33. Source Index

| Source | Type / evidence class | Used for |
|---|---|---|
| `Dataset\student_resource\README.md` | `[OFFICIAL]` markdown mirror of problem statement | Cross-check against PDF, §2 |
| `Dataset\student_resource\Documentation_template.md` | `[OFFICIAL]` required methodology template | §2, §30 |
| `Dataset\student_resource\utils\validate_submission.py` | `[OFFICIAL]` code, read in full | §2 validator rules, §5 C1–C4, §20 Phase 13 |
| `Dataset\student_resource\dataset\train\*.tsv`, `dataset\test\*.tsv` | `[OFFICIAL]` actual competition data — row counts and header rows read directly | §2 measured stats, basis for all of §8–§18 |
| `Docs\6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf` | `[OFFICIAL]`, 8 pages, read in full | Primary source for §2, §5, most of §6–§23 |
| `Docs\6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf` | `[OFFICIAL]`, 2 pages, read in full | §2 dates/limits/access rules, §5 C7/C9 |
| `Docs\AMAZON_ML_CHALLENGE_MASTER.md` | `[SECONDARY]`, self-authored KB, verified consistent with the two PDFs above | Cross-check, §4 confidence classification |
| `Docs\Amazon ML Challenge Forensic Analysis.md` | `[SECONDARY]`/`[PARTICIPANT]`/`[UNVERIFIED]` for most specifics, read in full including its own works-cited list | §6 (translated to decisions), §23 Phase 16, explicitly excluded from architecture decisions |
| `Docs\amazon_ml_challenge_2026_complete_video_and_source_notes.json` | `[SECONDARY]`, derived notes; explicitly states no video transcript is available | Confirms no additional facts beyond the two PDFs exist from the video |
| `Docs\graphify-out\GRAPH_REPORT.md` (+ `graph.json`, `manifest.json`) | `[SECONDARY]`, knowledge graph over the above | Structural cross-check in §6, corroborated the leaderboard-conflict flag in §2 independently |

---

## 34. Dependency Graph

```
Phase 0 (Ground Truth)
        │
        ▼
Phase 1 (Data Forensics) ──────────────┐
        │                              │
        ▼                              │
Phase 2 (Validation Strategy) ◄────────┘   (leakage findings from Phase 1 feed split design)
        │
        ▼
Phase 3 (Baseline)
        │
        ▼
Phase 4 (Metric Forensics) ─────────────┐  (can start in parallel with Phase 3 once
        │                                │   Phase 2's metric implementation exists)
        ▼                                │
Phase 5 (Feature Engineering) ◄──────────┘
        │
        ▼
Phase 6 (Model Ladder) ──────► Phase 8 (Ablation Studies)   [tightly coupled, iterate together]
        │                              │
        ▼                              │
Phase 7 (Error Forensics) ◄────────────┘   (feeds back into Phase 5/6 — not a one-way gate)
        │
        ▼
Phase 9 (Ensemble & Post-Processing)
        │
        ▼
Phase 10 (Robustness & Hidden-Test Simulation)
        │
        ▼
Phase 15 (Final Model Selection) ◄── Phase 11 (Compute) ◄── runs continuously alongside Phase 6–10
                                  ◄── Phase 12 (Reproducibility) ◄── finalized once model is chosen
        │
        ▼
Phase 13 (Submission Validation) ── runs before every leaderboard upload, not just at the end
        │
        ▼
Final Package + Phase 16 (contingent, parallel track, does not block submission)
```

**Parallelizable:** Phase 4 (Metric Forensics) can start as soon as Phase 2's F0.5 implementation exists, alongside Phase 3's baseline build. Phase 11 (Compute) and Phase 14 (Experiment Management) run continuously throughout, not as discrete sequential phases. Phase 16 prep (contingent) never blocks the main line.

**Must-not-start-early:** Phase 5 (Feature Engineering) must not begin before Phase 1's noise census (P1-009) exists — building similarity features before knowing what noise actually looks like in this specific data risks building the wrong features. Phase 6 (Model Ladder) must not climb past L1 before Phase 3's baseline and Phase 4's metric forensics both exist — no model complexity before the scoring is trustworthy.

---

## 35. First 24 Hours Execution Plan

*(Timing below is a **planning assumption** — the actual challenge window, 25–27 Sep 2026 IST, is confirmed in §2; internal day-1 pacing within that window is our own choice, not an official schedule.)*

| Block | Objective | Task IDs | Output | Decision |
|---|---|---|---|---|
| Hours 0–2 | Confirm environment, load all 7 TSVs with correct `sep="\t"`, verify row counts match §2 | P0-002 | Loaded dataframes/chunked readers | Proceed only if counts match §2 exactly |
| Hours 2–6 | Full Phase 1 data forensics pass (schema, nulls, duplicates, country distribution, match cardinality, noise census) | P1-001…P1-012 | `data_quality_report.md` v1 | Identify any blocking issue (e.g. unexpected nulls) before proceeding |
| Hours 6–8 | Implement and hand-verify the F0.5 metric function against the official worked example + synthetic cases | P2-003, P2-004 | `f05_metric.py` + passing unit tests | Do not proceed to modeling until this is verified |
| Hours 8–10 | Build the entity-grouped train/holdout split | P2-001, P2-002 | `VALIDATION_PROTOCOL.md` v1 | Confirm no ID leakage across split |
| Hours 10–16 | Build and run the Phase 3 baseline end-to-end (blocking → matching → both output files) | P3-001…P3-005 | `baseline_v0` results, validator-passing output | This is the single most important artifact of day 1 |
| Hours 16–18 | Run `utils/validate_submission.py` against baseline output on a local slice | P13 (early smoke test) | Pass/fail report | Fix format bugs immediately — cheap now, expensive later |
| Hours 18–22 | Phase 4 metric forensics (synthetic precision/recall sweep, singleton sensitivity, threshold sweep) | P4-001…P4-004 | `metric_forensics.md` v1 | Establishes the target for every later threshold decision |
| Hours 22–24 | Record baseline in `experiment_log.md`; write day-1 summary; flag any Phase 1 anomaly requiring a scope decision | P14 | `experiment_log.md` entry 1 | Go/no-go on Phase 5 feature engineering starting day 2 |

**Explicit non-goal for the first 24 hours:** no deep learning, no pretrained models, no ensembling. The entire window is understanding + a correct, if crude, end-to-end baseline — directly matching the Phase 0–3 gating already established above, independent of (but consistent with) the Forensic Analysis's baseline-first anecdote in §6.

---

## 36. First 7 Days Execution Plan

*(Day numbering is a **planning assumption** for internal pacing, not an official schedule — the actual competition runs 25–27 Sep 2026 per §2. If prep happens before the window opens, "Day 1" below is whatever day this plan is executed.)*

| Day | Objective | Key tasks | Deliverable | Decision gate |
|---|---|---|---|---|
| 1 | Ground truth + baseline | Phase 0 (done), Phase 1, Phase 2 (P2-001–004), Phase 3, start Phase 4 | `data_quality_report.md`, `VALIDATION_PROTOCOL.md`, `baseline_v0` | §26 Phase 1–3 gates must pass before Day 2 |
| 2 | Metric forensics complete + blocking build-out | Finish Phase 4; build P5-008 blocking (inverted index / phonetic keys) with measured recall ceiling | `metric_forensics.md`, blocking recall report | Blocking recall must be quantified before any matching-model work (R-3 mitigation) |
| 3 | Core similarity features + L2 classifier | P5-001–006, P5-007; Phase 6 L2 | `feature_engineering_report.md` v1, `model_ladder_log.md` entry L2 | Only proceed to L3 if Phase 7 shows headroom L2 can't reach |
| 4 | Error forensics + L3 (GBT) | Phase 7 full pass on L2; Phase 6 L3; threshold retuning (P4-003/A6) | `error_analysis_report.md` v1, L3 entry | Confirm L3 gain is real (Phase 8 ablation, not just a single run) |
| 5 | Ablations + robustness | Phase 8 full ablation table filled; Phase 10 P10-001–006 stress tests | `ablation_log.md`, `robustness_report.md` v1 | Any stress-test failure routes back to Phase 5/6, not ignored |
| 6 | Ensembling (if justified) + compute optimization | Phase 9 (gated on Phase 7 error-profile diversity); Phase 11 bottleneck fixes | `model_ladder_log.md` final entries, optimized pipeline | Ensembling only if error profiles genuinely differ — otherwise skip straight to Day 7 |
| 7 | Final selection + packaging + validator gate | Phase 15 selection table; Phase 12 reproducibility re-run; Phase 13 full validator pass; Phase 30 checklist | `final_model_selection.md`, packaged `code/business_entity_resolution/`, validator PASS | Nothing submitted until every item in §30 is checked |

Days 1–2 are non-negotiable and sequential (matches the dependency graph, §34). Days 3–6 may compress or extend based on the evidence gathered — this is intentionally not a rigid calendar, per the requirement not to invent a deadline the source documents don't specify.

---

## 37. What "Winning" Means (framing, not a guarantee)

This plan does **not** claim any strategy guarantees winning, a specific rank, or finalist status. The engineering objective is:

> Maximize competitive F0.5 performance, subject to the official rules (§5), robustness to hidden/private-test distribution shift (§17), reproducibility (§19), and technical defensibility (§23) — using only evidence-backed decisions (§28).

Historical evidence (Forensic Analysis, `[PARTICIPANT]`/`[SECONDARY]`) suggests these characteristics are *associated with* strong performance across past editions: baseline-first discipline, EDA before modeling, metric-aligned optimization, exact format compliance, and rigorous local validation. These are labeled **historical/empirical patterns**, not a winning formula — none of the historical winners solved this task or this metric.

---

## 38. Final Synthesis

### What We Believe Will Matter Most

**Evidence-backed** (`[OFFICIAL]`, directly from the two PDFs and the real data):
- Blocking recall ceiling (§1, §13, R-3) — the single highest-leverage lever, mathematically forced by the ~10M-record scale we measured directly.
- Precision-weighted, singleton-inclusive scoring (§2, §11) — governs every threshold/objective decision.
- Open-set country handling, specifically the France trap (§2, §17) — a designed adversarial test, not incidental noise.
- Strict format compliance as a binary gate (§5, §20) — independently confirmed by both the PDF rules and the validator's own code.

**Strong inference** (derived carefully from official text, not asserted by it):
- Country-open-set handling must extend to blocking keys, not just the final model (§8, P5-007/P10-001).
- Classical/tree-based matching over engineered similarity features is the right starting architecture for this specific task, regardless of what worked for unrelated past tasks (§13).

**Experiment-dependent** (genuinely unknown until Phases 1–10 run):
- Which specific noise types dominate error (P1-009, P7-005/006).
- Whether GBT (L3) meaningfully beats a linear classifier (L2) on this feature set.
- Whether pretrained embeddings would help at all, contingent on Q1 being resolved.
- The actual blocking-key combination that clears the recall ceiling without exploding candidate volume.

**Unknown** (flagged, not guessed):
- Pretrained-model provenance permissibility (§32 Q1).
- Whether a 2026 finale stage exists (§32 Q2).
- How the two leaderboards actually combine for shortlisting (§32 Q3, §2).
- Any undocumented compute/runtime ceiling (R-11).

### Our Competitive Strategy
Verify before building (Phase 0–1) → make the metric trustworthy before optimizing it (Phase 2, 4) → establish a correct-but-crude baseline before any complexity (Phase 3) → spend the majority of engineering effort on blocking recall and metric-aligned thresholding, since those are the two levers the evidence says matter most (§1) → climb the model ladder only as far as measured error analysis justifies (Phase 6–8) → stress-test against the specific adversarial case the challenge designed in (France/open-set, Phase 10) → never submit anything the local validator hasn't already passed (Phase 13) → select the final model on robustness and reproducibility, not just the highest single score (Phase 15).

### What Could Make This Plan Wrong?
- If the true private test distribution diverges from the public subset far more than the train/test country split alone suggests (§17, R-7) — our robustness testing (Phase 10) is a hedge, not a guarantee, since the actual private distribution is `[UNKNOWN]`.
- If Q1 (pretrained-model provenance) is resolved as "disallowed" after some pretrained-embedding work is already invested — mitigated by gating L5 behind Q1 resolution (§13, §25) rather than building it first.
- If blocking-key design underestimates the true diversity of name/address noise in the full 10M+ record corpus beyond what Phase 1's sampling captures — mitigated by measuring actual candidate recall on the full holdout (P5-008), not assuming it from a sample.
- If a Grand Finale materializes and Phase 16 prep was deprioritized too far — mitigated by keeping Phase 16 explicitly contingent rather than dropped, and by every phase already generating the artifacts (reports, logs) that a defense would need.

### Questions Requiring User Confirmation
See §32 (Q1 pretrained-model provenance, Q2 finale-stage existence for 2026, Q3 leaderboard-combination clarification). No other question is raised — everything else resolvable from the local files has been resolved above.
