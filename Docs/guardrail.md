# Amazon ML Challenge — Guardrails & Test Strategy

Applies to every agent action. Sources: official docs, `plan.md`. Labels: [OFFICIAL] [INFERENCE] [HYPOTHESIS] [UNVERIFIED].

## 1. Evidence Guardrails

- Never hallucinate requirements, dataset properties, metrics, winner strategies, or scores. Unknown → write `Not verified from available evidence.`
- Label every claim; never present [INFERENCE]/[HYPOTHESIS] as [OFFICIAL].
- Forensic Analysis year-by-year specifics (2021–2025) are [PARTICIPANT]/[SECONDARY]/[UNVERIFIED]; they never override 2026 official rules and never justify architecture choices (different tasks/metrics).
- Numbers about the data must come from a run/measurement with the command or script recorded.

## 2. Ambiguity Guardrail

Graphify (`Docs/graphify-out`) → Forensic Analysis → Master KB (`AMAZON_ML_CHALLENGE_MASTER.md`) → original source (PDFs/README/validator) → **ask the user**. Never guess after this chain. Record the question as an `RQ-###` in `experiment.md`. Currently open: RQ-001 … RQ-005.

## 3. Challenge Compliance (all [OFFICIAL] unless noted)

| ID | Rule | Check |
|---|---|---|
| C1–C4 | exact TSV format; every test S1 once; no dup IDs/rows; only existing test S2/S3 IDs, no S1 self-match | TEST-011/013/014 |
| C5 | model MIT or Apache-2.0, ≤8B params | licence + param count recorded per model before use |
| C6 | no external DB/API/service/geocoding/internet augmentation; violation = immediate DQ | TEST-017 (no-network audit) |
| C7 | desktop/laptop, single login per participant | operational |
| C8 | final zip layout per PS p.5 | packaging check in `decision.md` §5 |
| C9 | ≤5 submissions/day, 3 days (window 25–27 Sep 2026 IST) | log every submission in `progress.md` |
| — | pretrained-model permissibility | UNRESOLVED (RQ-001): do not use any pretrained component until answered |
| — | hardware/runtime/package-size limits | Not verified from available evidence (RQ-004) |

## 4. Data Guardrails

Never: read TSV without tab separator; leak holdout/test information into training or thresholds; use test-set labels (none exist); fit learned parameters on holdout/reserved data; alter `entity_id`; silently drop rows/records (every drop logged with count + reason); silently change schema; hard-code `{US, India}`; let an S1 entity's matched records straddle train/holdout; contaminate the reserved slice. Unsupervised statistics on test text (IDF/vocab): follow DEC-006 (PROPOSED) until RQ-005 answered.

## 5. Metric Guardrails

Primary metric: macro F0.5 (per S1 entity, singleton-inclusive), via the single verified implementation `src/eval/f05_metric.py`. Every result records: primary metric, split ID, baseline (EXP-001), score, delta, blocking recall and reduction ratio, singleton/matched and per-country (US/India/France when applicable) breakdown. No isolated numbers. Do not optimize a proxy (accuracy/F1) without showing its relation to F0.5 (P4-004).

## 6. Validation Guardrails

Prevent: leakage (grouped split, TEST-007); leaderboard overfitting (reserved slice untouched, no tuning on public score); test-set tuning; inconsistent splits (split ID + seed + hash recorded; comparisons only on identical splits); invalid comparisons (same metric code version, same candidate universe). Public/private conflict (RQ-003) → optimize robust generalization, not public rank.

## 7. Code Guardrails

Before modifying code: inspect callers, interfaces, tests, and relevant `graphify-out` nodes (`GRAPH_REPORT.md`; the graph covers docs/validator only, not future code — rebuild required if code is added). Do not modify: `plan.md`, source docs, datasets, `utils/validate_submission.py`, graphify outputs. New code lives outside evidence folders (DEC-005). Comment functions (guidelines require commented source, [OFFICIAL] Guidelines p.1).

## 8. Experiment Guardrails

Hypothesis → Change → Evaluation → Result → Conclusion → Decision, all in `experiment.md`. One change per experiment unless bundled by design. Failed/negative experiments retained. No experiment result is used as a decision without a `DEC-###`. Stop conditions per plan §27 (no meaningful gain, leakage-driven gain, seed-unstable, rule violation, irreproducible).

## 9. Reproducibility

Record per run: random seed, Python + package versions, dataset file checksums, config file, code version (VCS status not verified: the project is not a git repo), model version, split ID, runtime, peak RAM. Never overwrite a prior result; new run = new EXP ID.

## 10. TEST STRATEGY

All tests are `NOT_RUN` at initialization. Results are logged in `progress.md` §7.

### Data tests
| ID | Test | Plan ref |
|---|---|---|
| TEST-001 | all 7 TSVs parse with tab; column count = 4 (GT: 2); UTF-8 decodable | P1-001/012 |
| TEST-002 | `train_source1` IDs unique; GT source1 IDs == train_source1 IDs (1:1); ID prefixes valid | P1-002 |
| TEST-003 | null/empty/duplicate/malformed audit counts recorded, none silently dropped | P1-003/004/012 |

### Metric tests
| ID | Test | Plan ref |
|---|---|---|
| TEST-004 | F0.5 reproduces the official worked example: P=2/3, R=1 → 0.714 | P2-004 [OFFICIAL] |
| TEST-005 | F0.5 edge cases: perfect, total miss, correct singleton (=1.0), false-merge singleton (=0.0), partial overlap, macro-average across entities | P2-004 |
| TEST-006 | monotonicity: adding a false positive never raises per-entity F0.5; threshold sweep direction as expected | P4 |

### Validation / leakage tests
| ID | Test |
|---|---|
| TEST-007 | no S1 entity or its matched S2/S3 record appears on both sides of split; reserved slice disjoint from holdout |
| TEST-008 | open-set country: synthetic unseen country flows through blocking, features, decision without error or drop (P10-001) |

### Pipeline tests
| ID | Test |
|---|---|
| TEST-009 | normalization deterministic; identical code path train/holdout/test (feature parity) |
| TEST-010 | zero candidates → empty row emitted; multiple candidates handled; exact / near / ambiguous match fixtures |
| TEST-011 | matches ⊆ candidates per entity; candidates and matches contain only S2-/S3- IDs, no duplicates, no S1 self-match |
| TEST-012 | edge inputs: empty name/address, missing fields, Unicode (e.g., Devanagari seen in data), very long / very short strings, duplicate records do not crash or duplicate output IDs (P10-002..004) |

### Submission tests
| ID | Test |
|---|---|
| TEST-013 | `python utils/validate_submission.py --matching … --candidate … --test-dir dataset/test` → PASS before every upload (from `student_resource/`) |
| TEST-014 | same with `--check-ids` at least once per candidate final (memory permitting) |
| TEST-015 | one row per test S1 ID (1,732,544 expected — recount before use); exact headers; UTF-8; no literal `nan`/`None`/`inf` tokens inside ID lists (numeric NaN/Inf/range checks apply to model scores before formatting) |
| TEST-016 | output ordering: no official ordering rule — order recorded, not asserted |

### ML / reproducibility tests
| ID | Test |
|---|---|
| TEST-017 | no-network / no-external-lookup audit of code and dependencies (C6); licence + parameter count of any model (C5) |
| TEST-018 | same seed + config → identical outputs (deterministic where required); baseline reproducible from scratch |
| TEST-019 | package re-run: README commands regenerate both output files from raw data (P12-005) |

### Regression / performance
| ID | Test |
|---|---|
| TEST-020 | any change re-runs TEST-004..006, 011, 013 and does not lower the adopted baseline on the same split without a recorded DEC |
| TEST-021 | record runtime, peak RAM, candidate count/entity, throughput per stage (P11-001); no hardware limit is documented (RQ-004), so treat memory as a practical constraint |
