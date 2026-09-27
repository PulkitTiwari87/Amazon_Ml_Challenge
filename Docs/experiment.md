# Amazon ML Challenge — Experiments & Research

No experiment has been run. All results fields are empty by design. Task refs = plan.md IDs. Hypotheses are [HYPOTHESIS], not findings.

## 1. Research Questions

| RQ ID | Question | Status | Evidence / Experiment |
|---|---|---|---|
| RQ-001 | Are pretrained open-source models (local, no network, MIT/Apache-2.0, ≤8B) permitted? External-lookup ban vs licence rule is ambiguous | OPEN | Unresolved in graphify, Forensic Analysis, Master KB §17, PDFs. Needs user/official clarification. Gates P5-009/L5 (BLOCK-001) |
| RQ-002 | Does a 2026 finale/interview stage exist? | OPEN | Absent from both 2026 official docs; Forensic Analysis projects from prior years [UNVERIFIED]. Low priority (DEC-004) |
| RQ-003 | How do public/private leaderboards combine? PS p.6: final rank = private; Guidelines p.1: shortlisting = both | OPEN | Official-vs-official conflict. Handled by DEC-002 |
| RQ-004 | Hardware/runtime/package-size limits? | OPEN | Not verified from available evidence |
| RQ-005 | May unsupervised statistics (IDF, vocab) be fitted on test-source text? Blocking must index test records regardless | OPEN | Docs silent; interim policy DEC-006 |
| RQ-006 | Which blocking-key combination reaches high recall at acceptable candidate volume? | OPEN | EXP-005 (A4), P5-008 |
| RQ-007 | Fraction of singletons and match-cardinality distribution in train? | OPEN | P1-006 |
| RQ-008 | Which name/address noise types dominate errors? | OPEN | P1-009, P7-005/006 |
| RQ-009 | Does GBT beat logistic regression on the pair features? | OPEN | EXP-006 (A5) |
| RQ-010 | Does the grouped train holdout represent the test distribution (beyond France)? | OPEN | P1-010, P10-005 |

## 2. Open Questions

Materially affecting execution: RQ-001 (gates one branch), RQ-003 (selection criteria), RQ-005 (fit policy). RQ-002/004 are non-blocking. Resolve via ambiguity chain in guardrail.md §2, then ask user.

## 3. Hypotheses

| HYP ID | Hypothesis | Related RQ | Status |
|---|---|---|---|
| HYP-001 | Name normalization (case, punctuation, legal-suffix map) raises holdout F0.5 over exact-string baseline | RQ-008 | UNTESTED |
| HYP-002 | Address normalization raises holdout F0.5 | RQ-008 | UNTESTED |
| HYP-003 | Jaccard/Levenshtein/TF-IDF pair features (LR) beat the rule baseline | RQ-008 | UNTESTED |
| HYP-004 | Adding a phonetic blocking key raises blocking recall (esp. transliteration-heavy records) without exploding candidate volume | RQ-006 | UNTESTED |
| HYP-005 | GBT on the same features beats LR | RQ-009 | UNTESTED |
| HYP-006 | Threshold tuned directly on F0.5 beats default 0.5 and beats thresholds tuned on a proxy metric | — | UNTESTED |
| HYP-007 | Pipeline built without country-specific hard filters preserves holdout F0.5 on a held-out synthetic unseen country | RQ-010 | UNTESTED |

## 4. Experiment Registry

Mapped from plan §15 ablation rows (A0–A6). Status: NOT_STARTED / RUNNING / DONE / FAILED / ABANDONED.

| EXP ID | Hypothesis | Change | Dataset | Metric | Status |
|---|---|---|---|---|---|
| EXP-001 | reference (plan A0) | Baseline P3: normalized-name blocking + high-similarity rule; rest singleton | working holdout (P2, not built) | F0.5, blocking recall, reduction ratio | NOT_STARTED |
| EXP-002 | HYP-001 (A1) | + name normalization | same | same | NOT_STARTED |
| EXP-003 | HYP-002 (A2) | + address normalization | same | same | NOT_STARTED |
| EXP-004 | HYP-003 (A3) | + similarity features, LR | same | same | NOT_STARTED |
| EXP-005 | HYP-004 (A4) | + phonetic blocking key | same | blocking recall, F0.5 | NOT_STARTED |
| EXP-006 | HYP-005 (A5) | LR → GBT | same | same | NOT_STARTED |
| EXP-007 | HYP-006 (A6) | F0.5-tuned threshold vs 0.5 | same | F0.5 | NOT_STARTED |

New experiments: append next unused EXP ID; never reuse.

## 5. Experiment Records

Template — copy per experiment, ID-ordered:

```
### EXP-XXX — Title
**Hypothesis** (HYP-XXX)  **Motivation**  **Baseline** (EXP id)  **Change**
**Dataset / Split** (split ID, seed, checksum)  **Configuration**  **Seed**
**Metrics** (macro F0.5; blocking recall; reduction ratio; per-country/singleton)
**Results**  **Delta**  **Runtime / Compute** (time, peak RAM)
**Error Analysis**  **Conclusion**  **Decision** / **Related Decision ID**
```

### EXP-001 — Baseline: name-canonical-key + country-exact blocking/matching
**Hypothesis** none (reference point, plan A0) **Motivation** need a working end-to-end pipeline fast under a hard deadline
**Baseline** none (first) **Change** n/a — initial implementation
**Dataset / Split** full `train` (NOT a leakage-safe holdout — P2 grouped split not yet built; this is a same-data sanity check only, comparable in kind to a train-set fit-quality check, not a generalization estimate)
**Configuration** `code/business_entity_resolution/src/baseline/run_baseline.py`: name_key = sorted canonical tokens of NFKC+casefold+punctuation-stripped `business_name` (legal-suffix map from `eda/text_utils.py`); candidates = S1 x (S2 union S3) sharing name_key, with any name_key shared by >400 source-side records dropped entirely (AP-2, avoids candidate-volume explosion on generic names); matches = candidates additionally sharing the literal (open-set) `country` string. No address feature used yet.
**Metrics** (measured via `src/baseline/eval_baseline.py`, all real numbers, none fabricated):
- macro F0.5 = 0.3990
- entities = 2,206,821; singletons = 123,247 (5.585%); non-singleton = 2,083,574 (94.415%)
- candidate recall = 2,378,377 / 7,638,365 = 31.14% — **this is the F0.5 ceiling under this blocking; 69% of true matches are lost before the matcher ever sees them**
- singleton false-merge rate = 50,512 / 123,247 = 40.98% — **major precision leak** (name+country alone is not unique enough; same-name-different-business collisions)
- non-singleton miss rate = 349,717 / 2,083,574 = 16.78%
- candidates/S1: mean 13.34, median 2, p95 72, max 378
**Results** test-set run produced 1,732,544-row `matching_results.tsv`/`candidate_pairs.tsv`; `utils/validate_submission.py --check-ids` PASS (all matched/candidate IDs confirmed to exist in test S2/S3; zero unknown-ID references). **Delta** n/a (first). **Runtime / Compute** train run 295s wall, test run 249s wall; profiling attempts on the full 7-file EDA sweep OOM'd repeatedly (16GB machine, ~5-10GB free under load) even at 1-2 workers — this lighter reduced-column approach did not.
**Error Analysis** the two headline weaknesses (candidate recall, singleton false-merge) both point at the same root cause: name-only+country blocking is too coarse in both directions — it misses true matches with name variation beyond legal-suffix/token-reorder (address-only-similar cases) and it over-merges same-name-different-address businesses. Highest-value next step: bring `business_address` into both blocking (recover missed matches) and the match decision (reject same-name-different-address pairs).
**Conclusion** functional, compliant, precision-conscious-in-intent baseline; validated as the reference point. Not near a competitive score — candidate recall is the hard ceiling and must be raised before any matcher/threshold work matters.
**Decision** ADOPTED as `CURRENT_BASELINE` (first, only comparator so far). Superseded only by a change that is measured on the same train set and does not regress candidate recall or singleton false-merge rate without justification. **Related Decision ID** none yet (see decision.md if formalized).

No further records yet.

## 6. Failed Experiments

None. Never delete; record cause of failure (leakage, instability, cost, rule violation).

## 7. Ablation Results

| Experiment | Component Removed/Added | Metric | Delta | Conclusion |
|---|---|---:|---:|---|
| — | — | — | — | No results yet |

## 8. Model Comparisons

| Model | Validation | Secondary Metrics | Runtime | Memory | Notes |
|---|---:|---|---:|---:|---|
| — | — | — | — | — | No results yet |

## 9. Key Findings

None. (Measured facts so far are data row counts only — architecture.md §3.)

## 10. Follow-up Experiments

Only after EXP-001 exists and Phase 7 error buckets identify headroom (plan §13 climb triggers). Pending, not justified yet: phase-10 stress tests (P10-001..006), pretrained embeddings (blocked by RQ-001).
