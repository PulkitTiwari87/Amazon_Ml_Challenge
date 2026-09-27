# Amazon ML Challenge — Architecture

Scope: HOW the solution is structured. Source: `plan.md` (§ refs), official docs (`Docs/*.pdf`, `Dataset/student_resource/README.md`, `utils/validate_submission.py`). Nothing here is implemented yet. Status vocabulary: `PLANNED` / `EXPERIMENTAL` / `VALIDATED` / `ADOPTED` (see `decision.md` §4 for what is ADOPTED). Every component below is currently `PLANNED` unless stated.

## 1. Architecture Principles

| # | Principle | Evidence |
|---|---|---|
| AP-1 | Blocking recall is the ceiling; measure it, never assume it | [OFFICIAL] PS p.7 tips; plan §1 |
| AP-2 | Precision-first: default to "no match" under uncertainty | [OFFICIAL] F0.5, singleton = 1.0 / any false match = 0.0 (PS p.6) |
| AP-3 | `country` is an open-set string everywhere (blocking keys, features, thresholds) — France is test-only | [OFFICIAL] PS p.2; DEC-001 |
| AP-4 | Keep raw text; normalization is a derived, reversible layer | [INFERENCE] plan §12 (P5-001/002) |
| AP-5 | `matching_results` ⊆ `candidate_pairs`; candidates are exactly what the matcher scores | [OFFICIAL] PS pp.3–4 |
| AP-6 | No network/API/lookup at any stage; model MIT/Apache-2.0, ≤8B params | [OFFICIAL] PS pp.5–7; plan C5/C6 |
| AP-7 | Complexity only with measured justification (model ladder, ablations) | plan §13/§15 |
| AP-8 | Whole pipeline must be re-runnable from packaged code (data → blocking → matching → output) | [OFFICIAL] PS p.5; plan C8 |

## 2. System Overview

```
raw TSVs (S1,S2,S3; train/test)
 → Data Validation (schema, IDs, encoding)          [P1, TEST-001..003]
 → Preprocessing / Normalization (name, address)    [P5-001/002]
 → Candidate Generation (blocking, per S1 entity)   [P5-008]  → candidate_pairs.tsv
 → Pair Features (similarity)                       [P5-003..007]
 → Matcher (rule → LR → GBT → ...)                  [Phase 6 ladder]
 → Decision (threshold tuned on F0.5; abstain=singleton) [P4-003, P9-004]
 → Post-processing (optional, gated)                [Phase 9]
 → matching_results.tsv → Submission Validation (validate_submission.py) [Phase 13]
```
No image/second modality exists; multimodal levels are out of scope (plan §13 L6).

## 3. Data Architecture

Working data root: `E:\Amazon ML Challenge\Dataset\student_resource\dataset\` (read-only; never modified).

| File | Records (header excl.) | Origin |
|---|---:|---|
| train/train_source1.tsv | 2,206,821 | measured locally (`wc -l`), plan §2 |
| train/train_source2.tsv | 5,034,616 | same |
| train/train_source3.tsv | 5,285,603 | same |
| train/train_ground_truth.tsv | 2,206,821 | same (line count equals train_source1; 1:1 coverage NOT yet verified — P1-002) |
| test/test_source1.tsv | 1,732,544 | same |
| test/test_source2.tsv | 4,887,273 | same |
| test/test_source3.tsv | 5,082,316 | same |

- Identifiers: `S1-`/`S2-`/`S3-` prefix = source [OFFICIAL]. Observed samples are prefix + digits; formal uniqueness/format audit NOT_VERIFIED (P1-001/002).
- Target: `matched_entity_ids` per S1 entity (comma-separated S2/S3 IDs; empty = singleton). Test has no labels [OFFICIAL].
- Modalities: text only (`business_name`, `business_address`) + `country` label.
- Splits: official train/test only. Internal working holdout + reserved slice: PLANNED (P2-001/002/007), not built.
- Missing values: empty fields exist (e.g., an empty `business_address` seen in a `train_source3` head sample); rates NOT_VERIFIED (P1-003).
- Duplicates: within-source duplicates NOT_VERIFIED (P1-004).
- Lineage: every derived artifact must record source file + config + code version (see `guardrail.md` §9).

## 4. Data Contract

| Item | Contract | Evidence |
|---|---|---|
| Source file columns | `entity_id`, `business_name`, `business_address`, `country` | [OFFICIAL] PS pp.1–2 |
| Ground-truth columns | `source1_entity_id`, `matched_entity_ids` | [OFFICIAL] PS p.2 |
| Read mode | tab-delimited (`sep="\t"`), UTF-8 | [OFFICIAL] PS p.1; validator reads UTF-8 |
| Column dtypes | all textual; no further typing verified | Not verified from available evidence |
| `country` | open set of strings; train = US, India; test adds France | [OFFICIAL] PS p.2 |
| Output: matching | header `source1_entity_id\tmatched_entity_ids`; 1 row per test S1 entity; only S2-/S3- IDs; no dup IDs; no dup rows | [OFFICIAL] PS pp.3–5; validator |
| Output: candidates | header `source1_entity_id\tcandidate_entity_ids`; same rules | [OFFICIAL] |
| Row order in outputs | no ordering rule stated; validator does not check order | Not verified from available evidence (validator source read) |

Allowed transformations: text normalization (case, punctuation, legal-suffix/abbreviation mapping, token/n-gram/phonetic keys) as *derived* columns; chunked/streamed reads.
Forbidden: hard-coding/filtering/one-hot on `{US, India}`; altering or re-keying `entity_id`; dropping any test S1 entity; any external lookup/geocoding/augmentation; using pretrained components without RQ-001/licence check.
Missing-value behavior: empty name/address must not crash or silently drop a record; entity still gets an output row (empty list allowed). Detailed cleaning rules: decided per-anomaly after P1 (no silent cleaning).

## 5. Processing Pipeline

Stages (all `PLANNED`): ingest (chunked TSV) → validate → normalize (derived columns) → cache normalized text + blocking keys (plan P11-004) → candidate generation → pair features → score → decide → write outputs. Intermediate artifacts location: NOT_DECIDED (see DEC-005). Each cached artifact keyed by (input file, normalizer version, config hash).

## 6. Candidate Generation / Retrieval

Applies (scale ≈ 10M source records/side; all-pairs infeasible — plan §1).
- Method: union of complementary keys (normalized-name tokens/n-grams, address tokens, phonetic key) via inverted index — PLANNED (P5-008, P5-006); exact key set UNDECIDED (RQ-006).
- Country: must not be a mandatory hard filter that assumes a closed set (AP-3); whether a same-country restriction is safe is UNVERIFIED and must be tested (P10-001).
- Candidate limits: NOT_DECIDED; set from measured recall vs volume.
- Metrics recorded per run: blocking recall (fraction of true matches in candidates), reduction ratio, candidates per S1 entity, runtime, RAM (plan P3-005, P11).
- Output: `candidate_pairs.tsv` = final list fed to the matcher (not an early pass) [OFFICIAL PS p.3].

## 7. Feature Architecture

| Family | Plan ID | Status |
|---|---|---|
| Name normalization | P5-001 | PLANNED |
| Address normalization | P5-002 | PLANNED |
| Jaccard / token overlap (name, address) | P5-003 | PLANNED [OFFICIAL tip] |
| Levenshtein / edit similarity | P5-004 | PLANNED [OFFICIAL tip] |
| TF-IDF cosine | P5-005 | PLANNED [OFFICIAL tip] |
| Phonetic key | P5-006 | PLANNED |
| Open-set country-aware address parsing | P5-007 | PLANNED |
| Pretrained embedding similarity | P5-009 | PLANNED — GATED by RQ-001 (not to be built before answered) |

Promotion rule: PLANNED → EXPERIMENTAL (EXP registered) → VALIDATED (positive delta on holdout + reserved slice, leakage check passed) → ADOPTED (a DEC entry). No feature is ADOPTED.

## 8. Model Architecture

| Level | Model | Status |
|---|---|---|
| Baseline (L1) | rule/threshold on normalized-name equality/similarity | PLANNED (P3) |
| Candidate (L2) | logistic regression on pair features | PLANNED |
| Candidate (L3) | gradient-boosted trees on same features | PLANNED |
| Experimental (L4) | small text-encoder pair model | PLANNED, only if Phase 7 attributes error to representation |
| Experimental (L5) | pretrained embeddings | PLANNED, GATED by RQ-001 |
| Ensemble (L7) | blend/stack | PLANNED, gated by Phase 9 |
| Final model | — | NONE. Nothing is final or validated. |

## 9. Validation Architecture

- Working holdout: split at S1-entity level, grouped so matched S2/S3 records do not straddle the split; stratified by country and singleton status [INFERENCE, P2-001/002].
- Reserved slice: untouched during feature/threshold iteration [INFERENCE, P2-007].
- Metric: exact per-S1-entity macro F0.5, singleton-inclusive, standalone module `src/eval/f05_metric.py` with tests (P2-003/004) [OFFICIAL formula].
- CV vs single split: decided after variance is measured (P2-005).
- Leaderboard: public feedback only; ≤5 submissions/day; never used for tuning decisions without local confirmation [plan R-2].
- Unsupervised fit policy on test text: see RQ-005 / DEC-006.

## 10. Inference Architecture

Same code path for holdout and test: normalize → block → features → score → threshold → write. Requirements: chunked/batched processing (plan P11-003), deterministic given seed, no network. Batch sizes/hardware: NOT_DECIDED; hardware limits UNKNOWN (RQ-004).

## 11. Submission Architecture

`predictions → format (TSV, exact headers, UTF-8, one row/test S1) → local validator (utils/validate_submission.py, also `--check-ids` when memory allows) → dry-run checks (`guardrail.md` §10 TEST-013..016) → upload matching_results.tsv → record in progress.md`. Final zip layout per plan C8 (`output/`, `code/business_entity_resolution/{src,README.md,requirements.txt}`, `Documentation_template.md`). Gate: `decision.md` §5.

## 12. Component Dependencies

```
data validation → normalization → blocking → pair features → matcher → threshold → writer → validator
                        ↘ f05_metric (independent; consumed by every experiment and threshold tuning)
```
Interfaces to fix when coding (NOT_DECIDED): normalized-record schema; candidate table schema `(s1_id, cand_id, source, blocking_key(s))`; feature matrix schema; score → decision function signature. Working-code location and reports location: DEC-005 (PROPOSED).

## 13. Architecture Evolution

| Version | Date | Change | Reason | Decision ID |
|---|---|---|---|---|
| v0.1 | 2026-09-25 | Initial architecture from plan.md; all components PLANNED | Control-layer initialization | DEC-001, DEC-003 |
