# Amazon ML Challenge — Progress

Records only what has actually happened. Task IDs = `plan.md` IDs. Cross-refs: EXP/HYP/RQ in `experiment.md`, DEC in `decision.md`, TEST in `guardrail.md` §10.

## 1. Current Status

- Current phase: Phase 3 — Baseline (EXP-001 adopted); Phase 1 EDA started then abandoned mid-run under a hard deadline (see §11)
- Current task: improving candidate recall (31.1%, measured) and singleton false-merge rate (41.0%, measured) via address-based blocking/matching — see experiment.md EXP-001 error analysis
- Status: first compliant submission generated and validated (`output/matching_results.tsv`, `output/candidate_pairs.tsv`); `utils/validate_submission.py --check-ids` PASS
- Last updated: 2026-09-27
- Deadline context (user-stated): full project due 2026-09-27 22:00; a baseline submission was due within ~2h of 2026-09-27 ~12:00 — met.
- Current blocker: none for Phase 3 continuation. BLOCK-001 (RQ-001, pretrained models) still gates only P5-009/L5, untouched.

## 2. Phase Status

| Phase | Status | Completion | Deliverables | Tests | Blockers |
|---|---|---|---|---|---|
| P0 Ground truth | COMPLETE (3 non-blocking items open: P0-008/009/010) | — | plan.md §2, §5, §32 | — | RQ-004, RQ-001, RQ-003 |
| P1 Data forensics | NOT_STARTED | — | data_quality_report.md, leakage_risk_report.md (not created) | TEST-001..003 NOT_RUN | — |
| P2 Validation | NOT_STARTED | — | VALIDATION_PROTOCOL.md, f05_metric.py (not created) | TEST-004..008 NOT_RUN | — |
| P3 Baseline | NOT_STARTED | — | EXP-001 | TEST-009..013 NOT_RUN | needs P2 |
| P4 Metric forensics | NOT_STARTED | — | metric_forensics.md | TEST-006 | needs P2-003 |
| P5 Features | NOT_STARTED | — | feature_engineering_report.md | — | needs P1-009; P5-009 gated (BLOCK-001) |
| P6 Model ladder | NOT_STARTED | — | — | — | needs P3, P4 |
| P7 Error forensics | NOT_STARTED | — | error_analysis_report.md | — | needs model output |
| P8 Ablations | NOT_STARTED | — | experiment.md §7 | — | — |
| P9 Ensemble/post-proc | NOT_STARTED | — | — | — | needs strong single models |
| P10 Robustness | NOT_STARTED | — | robustness_report.md | TEST-008, 012 | — |
| P11 Compute | NOT_STARTED | — | — | TEST-021 | RQ-004 |
| P12 Reproducibility | NOT_STARTED | — | README, requirements.txt | TEST-018/019 | — |
| P13 Submission validation | NOT_STARTED | — | validator wrapper | TEST-013..016 | — |
| P14 Experiment mgmt | IN_PROGRESS | — | experiment.md initialized (empty registry) | — | — |
| P15 Final selection | NOT_STARTED | — | final_model_selection.md | — | — |
| P16 Finalist defense | NOT_STARTED (contingent) | — | — | — | RQ-002 |

## 3. Completed Tasks

| Task ID | Description | Result | Tests | Evidence |
|---|---|---|---|---|
| P0-001..P0-007 | Verify task, dataset, target, metric, format, rules, resources | Done; recorded in plan | n/a (document verification) | plan.md §2, §5, §7 |
| — | Control docs initialized (architecture, guardrail, progress, experiment, decision) | Created 2026-09-25 | consistency audit in §11 | Docs/*.md |
| — | Row counts of 7 TSVs measured | see architecture.md §3 | not a formal test | plan.md §2 |

## 4. Active Tasks

None in progress. Next: P1-001 (depends on P0 only).

## 5. Current Best Results

No validated result yet.

| Model/Version | Dataset/Split | Metric | Score | Experiment |
|---|---|---|---:|---|
| — | — | — | — | — |

## 6. Active Experiments

None. Registered but NOT_STARTED: EXP-001..EXP-007 (see `experiment.md` §4).

## 7. Tests

| Test ID | Description | Result | Date |
|---|---|---|---|
| TEST-001..021 | defined in guardrail.md §10 | NOT_RUN | — |

## 8. Blockers

| Blocker | Impact | Investigation | Status |
|---|---|---|---|
| BLOCK-001 | Pretrained-model permissibility unknown (RQ-001); blocks only P5-009 / model-ladder L5, not P1–P4 | Checked graphify, Forensic Analysis, Master KB, PDFs: unresolved; needs user | OPEN |

## 9. Risks

Probability/impact = our engineering assessment (from plan §28), not Amazon's. `plan R-n` = plan.md risk register entry.

| Risk | Plan ref | Probability | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| RISK-001 Validation leakage | R-1 | Medium | High | TEST-007, grouped split | OPEN |
| RISK-002 Overfit to own loop / public LB | R-2 | Medium | High | reserved slice | OPEN |
| RISK-003 Blocking recall too low | R-3 | Medium-High | Critical | measure recall (RQ-006) | OPEN |
| RISK-004 Closed-set country assumption | R-4 | Medium | High | TEST-008 | OPEN |
| RISK-005 Model licence/size violation | R-5 | Low | Critical | TEST-017, RQ-001 gate | OPEN |
| RISK-006 External-lookup violation | R-6 | Low | Critical | TEST-017 | OPEN |
| RISK-007 Leaderboard-combination ambiguity | R-7 | n/a | Medium | DEC-002, RQ-003 | RECORDED |
| RISK-008 Wasted submissions (format) | R-8 | Low | Medium | TEST-013 gate | OPEN |
| RISK-009 Memory/compute failure at scale | R-9 | Medium | Medium | chunking, TEST-021 | OPEN |
| RISK-010 Finale-prep effort misallocated | R-10 | Unknown | Low | DEC-004 | RECORDED |
| RISK-011 Undocumented compute limit | R-11 | Unknown | Medium | RQ-004 | OPEN |

## 10. Next Actions

1. P1-001 … P1-012 (plan §8; first-24h block in plan §35), starting with loading all 7 TSVs and confirming counts against architecture.md §3.
2. Confirm or amend DEC-005 (working code/report locations) and DEC-006 before code is written.
3. In parallel once P1-001 done: P2-003/004 (F0.5 metric + TEST-004/005).
4. User input pending: RQ-001, RQ-002, RQ-003 (plan §32) — none blocks P1–P4.

## 11. Execution History

| Date | Milestone |
|---|---|
| 2026-09-25 | Directory inspected; official PDFs, README, validator, KB, Forensic Analysis, graphify report read; 7 TSVs row-counted |
| 2026-09-25 | plan.md created (now located at Docs/plan.md, 76 KB) |
| 2026-09-25 | Control documents initialized: architecture, guardrail, progress, experiment, decision |
