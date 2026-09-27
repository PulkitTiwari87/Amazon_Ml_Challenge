# Amazon ML Challenge — Decisions & Submission

## 1. Decision Rules

A major decision needs: problem, evidence, alternatives, experiment/validation, result, rationale, trade-offs, risks, reversal condition. Statuses: PROPOSED / ACCEPTED / REJECTED / SUPERSEDED. "ACCEPTED (constraint)" = follows from an official rule, no experiment needed. Performance decisions require an EXP record on the reserved slice. IDs never reused.

## 2. Decision Log

### DEC-001 — Treat `country` as an open-set string everywhere
**Date:** 2026-09-25 **Phase:** P0 **Status:** ACCEPTED (constraint)
**Problem** France is test-only. **Evidence** [OFFICIAL] PS p.2. **Constraints** no hard-coding/filtering/one-hot on {US, India}. **Options** closed set (rejected: violates rule) / open set.
**Result** n/a. **Decision** open-set throughout, including blocking keys (extension to blocking is [INFERENCE], test via TEST-008/P10-001). **Trade-offs** may forgo country filters that shrink candidates. **Risks** RISK-004. **Reversal** only if official docs change. **Tasks** P5-007, P10-001. **Experiments** EXP-005, HYP-007.

### DEC-002 — Optimize robust generalization; record leaderboard conflict
**Date:** 2026-09-25 **Phase:** P0 **Status:** ACCEPTED (interim)
**Problem** RQ-003: final rank = private (PS p.6) vs shortlisting = both (Guidelines p.1). **Options** optimize public / private-only / robust holdout+stress tests. **Decision** selection by reserved-slice + robustness, not public score; satisfies both readings. **Trade-offs** slower than leaderboard chasing. **Risks** RISK-002/007. **Reversal** RQ-003 answered. **Tasks** P0-010, P15.

### DEC-003 — Gate pretrained models behind RQ-001
**Date:** 2026-09-25 **Phase:** P0/P5 **Status:** ACCEPTED (interim)
**Problem** permissibility of pretrained components not stated. **Evidence** PS p.6 (licence/size), p.7 (lookup ban); ambiguity flagged in Master KB §17. **Options** assume allowed / assume disallowed / gate. **Decision** no pretrained component built or used until RQ-001 answered; baseline and L1–L4 use no pretrained weights. **Risks** RISK-005. **Reversal** RQ-001 answered "allowed" (with licence/size verified). **Tasks** P5-009. **Blocker** BLOCK-001.

### DEC-004 — Finalist-defense prep is contingent
**Date:** 2026-09-25 **Phase:** P16 **Status:** ACCEPTED (interim)
**Problem** RQ-002. **Evidence** no finale mentioned in 2026 official docs. **Decision** P16 not started until top-100/finale details are published, but all phases keep artifacts a defense would need. **Reversal** RQ-002 confirmed. **Risks** RISK-010.

### DEC-005 — Working locations for code, artifacts, reports
**Date:** 2026-09-25 **Phase:** P1 **Status:** PROPOSED
**Problem** plan specifies only the *submission* layout (`code/business_entity_resolution/{src,README.md,requirements.txt}`, `output/`); no working location exists. **Proposal** code at `E:\Amazon ML Challenge\code\business_entity_resolution\` (mirrors package), outputs at `E:\Amazon ML Challenge\output\`, reports at `E:\Amazon ML Challenge\Docs\reports\`. Plan's `experiment_log.md`/`ablation_log.md`/`model_ladder_log.md` are represented by `experiment.md` §4/§7/§8. **Alternatives** work inside `Dataset\` (rejected: evidence folder, must stay unmodified). **Reversal** any time before the first file is written. Needs user confirmation or silent acceptance.

### DEC-006 — Interim fit policy for test text
**Date:** 2026-09-25 **Phase:** P2 **Status:** PROPOSED
**Problem** RQ-005. **Proposal** learned parameters, IDF/vocab and thresholds fitted on train data only; test records are used only as the retrieval universe and never for label-dependent steps (none exist). Any deviation needs a new DEC. **Risks** RISK-001. **Reversal** RQ-005 answered.

## 3. Major Technical Decisions

| Group | Decisions |
|---|---|
| Data | DEC-001, DEC-005 |
| Validation | DEC-002, DEC-006 |
| Features | DEC-003 |
| Candidate generation | none yet (RQ-006 → EXP-005) |
| Models | DEC-003 |
| Metrics | none yet (official F0.5 fixed; threshold via EXP-007) |
| Post-processing | none yet |
| Compute | none yet (RQ-004) |
| Architecture | none beyond principles in architecture.md §1 |

### Recorded document conflicts (not resolved)

| ID | Conflict | Sources | Handling |
|---|---|---|---|
| CONF-001 | Leaderboard combination (private only vs both) | PS p.6 vs Guidelines p.1 | RQ-003, DEC-002 |
| CONF-002 | Doc length: "1–2 page document" vs "no page limit" | Guidelines p.1 vs PS p.7 | plan follows the more detailed template; confirm if space matters |
| CONF-003 | Master KB header states Docs drive was unmounted and cites a `sources/` folder that does not exist here | Master KB vs actual tree | KB claims re-checked against PDFs: consistent; header considered stale |
| CONF-004 | plan.md internal cross-references are stale: says "Phase 1 exit criteria §19" / "risk R-11 in §21" / "R-2 in §21", but decision gates are §26 and the risk register is §28; also names `experiment_log.md`, `ablation_log.md`, `model_ladder_log.md` | plan.md | plan.md not modified (per instructions); IDs (P*, R-*) are unambiguous, so use IDs, not § numbers; log mapping in DEC-005 |
| CONF-005 | Forensic Analysis asserts prior-year specifics and a finale; Master KB says 2021–2025 "not verified" | Forensic Analysis vs Master KB | Forensic content treated [PARTICIPANT]/[UNVERIFIED]; not used for 2026 rules |
| CONF-006 | User request names `Docs\graphify` and `Knowledge Base`; actual paths are `Docs\graphify-out` and `AMAZON_ML_CHALLENGE_MASTER.md` | task text vs tree | actual paths used |

## 4. Current Adopted Solution

Nothing is ADOPTED or VALIDATED.

| Component | State |
|---|---|
| Metric implementation | PLANNED |
| Validation split | PLANNED |
| Blocking | PLANNED (key set UNDECIDED) |
| Normalization / features | PLANNED |
| Matcher | PLANNED (baseline L1 first) |
| Threshold | UNKNOWN |
| Final model | NONE |

## 5. FINAL SUBMISSION GATE

Do not mark ready unless every mandatory box is checked with evidence (ID/log reference). Currently: 0 of all checked.

### Data
- [ ] Correct dataset (test files, counts match architecture.md §3)
- [ ] Correct preprocessing (same code path as validated runs)
- [ ] No leakage (TEST-007)
- [ ] One row per test S1 entity (TEST-015)
- [ ] Identifiers valid, S2-/S3- only (TEST-011)

### Model
- [ ] Correct checkpoint / artifact hash recorded
- [ ] Correct configuration file
- [ ] Correct preprocessing version
- [ ] Threshold from F0.5 tuning on train-side data, confirmed on reserved slice
- [ ] Licence MIT/Apache-2.0 and ≤8B params recorded (TEST-017)

### Predictions
- [ ] No literal nan/None/inf tokens; no empty-ID artifacts
- [ ] No duplicate IDs (TEST-012)
- [ ] matches ⊆ candidates (TEST-011)
- [ ] Prediction count = test S1 count

### Submission
- [ ] Headers exact; TSV; UTF-8 (TEST-015)
- [ ] File name `matching_results.tsv`
- [ ] Validator PASS (TEST-013), `--check-ids` run (TEST-014)
- [ ] Daily submission count ≤5 checked; submission logged in progress.md

### Reproducibility
- [ ] Environment + pinned `requirements.txt`
- [ ] Dataset checksums
- [ ] Model + seed + config recorded
- [ ] Package re-run reproduces both outputs (TEST-018/019)

### Compliance
- [ ] No external lookup/network (TEST-017)
- [ ] Pretrained-model status resolved (RQ-001) or no pretrained component used
- [ ] Package layout per C8; `Documentation_template.md` filled
- [ ] Compute restrictions checked (RQ-004 answered or noted unverified)

### Final Approval
Ready = every box above checked. Status: NOT READY.
