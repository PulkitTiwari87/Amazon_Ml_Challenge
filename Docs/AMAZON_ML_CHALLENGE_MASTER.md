# Amazon ML Challenge — Master Knowledge Base

> **Evidence scope and location.** This knowledge base is grounded only in the two PDFs available in the project mirror: [2026 problem statement](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf) (8 pages) and [2026 guidelines and key instructions](sources/6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf) (2 pages). The requested `E:\Amazon ML Challenge\Docs` drive is not mounted here, so it was not possible to inspect that directory. The result is therefore a verified 2026-focused reference with explicit historical gaps, not a claim that all files at the requested location were reviewed. Existing source files were left unchanged.

## 1. Executive Summary

**[OFFICIAL]** The available 2026 task is cross-source business entity resolution: for each deduplicated Source 1 business, identify zero, one, or many matching records in Sources 2 and 3. The inputs are tab-separated records with noisy business names and addresses; labels are supplied for training only. ([Problem statement, pp. 1–2](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

**[OFFICIAL]** Scoring uses per-Source-1-entity macro-averaged F0.5, including singletons. It rewards precision twice as strongly as recall (beta = 0.5), making false merges especially costly. Public results use a test subset; final rankings use the private test portion. ([Problem statement, pp. 4–5](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

**[OFFICIAL]** External identity lookup and data augmentation are prohibited. A final package includes predictions, candidate pairs, runnable code, pinned dependencies, and a methodology report; top packages receive review before final ranking confirmation. The model must be MIT- or Apache-2.0-licensed and have at most 8 billion parameters. ([Problem statement, pp. 5–7](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

**[INFERENCE]** This edition tests end-to-end decision quality: candidate generation controls achievable recall, while conservative matching and correct singleton handling protect precision. Reproducible, auditable implementation is part of the evidence expected from teams because the final package is reviewed. These are interpretations of the stated task and package requirements, not a separate official scoring rubric.

## 2. Historical Timeline

| Year | Verified information |
|---|---|
| 2021–2025 | Not verified from available documents. |
| 2026 | **[OFFICIAL]** Three-day challenge, 25–27 September 2026 (IST); business entity resolution across three sources; F0.5 macro-average and public/private leaderboards. ([2026 Guidelines, p. 1](sources/6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf); [Problem statement, pp. 1, 4–5](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf)) |
| Later editions | Not verified from available documents. |

## 3. Official Judging Criteria by Year

| Year | Officially documented judging |
|---|---|
| 2021–2025 | Not verified from available documents. |
| 2026 | **[OFFICIAL]** F0.5 macro-averaged across Source 1 entities, including singletons. Public leaderboard is based on a test subset; final rankings use the remaining private portion. **[OFFICIAL]** Guidelines say shortlisting/evaluation consider performance across both leaderboards and eligibility, followed by top-100 team announcement. ([Problem statement, pp. 4–6](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf); [2026 Guidelines, p. 1](sources/6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf)) |

The problem statement says the final decision is based on the private leaderboard, while the guidelines say evaluation and shortlisting are based on performance across both public and private leaderboards. These statements can refer to different stages: leaderboard final ranking versus shortlisting. The documents do not give a detailed formula for combining both leaderboards in shortlisting. **[OFFICIAL; scope distinction unresolved]**

## 4. Official Rules & Restrictions

**2026 rules documented in the available official materials:**

- **[OFFICIAL]** 5 submissions per team per day over 3 days; submit button disabled afterward. Maintain submission version history. ([2026 Guidelines, p. 1](sources/6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf))
- **[OFFICIAL]** No external databases, APIs, services, government business-registration lookup, geocoding APIs, or internet-based data augmentation for identity resolution. The problem statement says evidence can lead to immediate disqualification. ([Problem statement, p. 7](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))
- **[OFFICIAL]** Final model license must be MIT or Apache 2.0; parameter count must be no more than 8 billion. ([Problem statement, p. 6](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))
- **[OFFICIAL]** No cheating, plagiarism, unfair practices, or attempting via multiple IDs. One desktop/laptop login per participant; simultaneous logins are disallowed. ([2026 Guidelines, p. 1](sources/6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf))
- **[OFFICIAL]** Use TSV with explicit tab delimiter. Every test Source 1 record must appear exactly once; matched IDs must exist in test Source 2/3, must not duplicate, and must be a subset of candidate IDs. Submission validator is provided. ([Problem statement, pp. 2–4](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))
- **[OFFICIAL]** Leaderboard upload is `matching_results.tsv`; final ZIP must also include `candidate_pairs.tsv`, self-contained runnable source, README, dependency pins, and methodology document. ([Problem statement, pp. 3–6](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))
- **[OFFICIAL]** External lookup constraints do not explicitly resolve whether pretrained models are permitted. The documented model license/size condition is not by itself evidence that arbitrary pretrained data or online inference is allowed. **Not verified from available documents.**

## 5. Metrics and What They Reward

For each Source 1 entity, calculate precision and recall for its predicted matched-ID set, then compute F0.5:

`F0.5 = (1.25 × Precision × Recall) / (0.25 × Precision + Recall)`

The competition score is the arithmetic macro-average of per-entity F0.5 across all Source 1 entities. ([Problem statement, p. 4](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

**[OFFICIAL]** At beta 0.5, precision has twice the relative weight of recall. An incorrect extra match (false positive / false merge) is more costly than a missed link. Correctly predicting an empty list for a true singleton earns 1.0; predicting any match for a singleton earns 0.0. ([Problem statement, p. 4](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

**[INFERENCE]** Tune candidate coverage and final decision thresholds separately. High candidate recall is necessary to preserve possible true links; the final matcher should reject uncertain candidates where false merges would lower per-entity precision. Validate singleton handling explicitly.

## 6. Problem/Dataset Evolution

Only the 2026 dataset is evidenced in the available documents; evolution across years cannot be established.

| Year | Problem | Data | Metric | Judging | Restrictions | Finalist Process |
|---|---|---|---|---|---|---|
| 2021–2025 | Not verified | Not verified | Not verified | Not verified | Not verified | Not verified |
| 2026 | Business entity resolution: map each Source 1 entity to zero or more matching Source 2/3 entities | TSV; `entity_id`, `business_name`, `business_address`, `country`; training countries US and India; test also includes France, absent from training | Macro F0.5 per Source 1 entity; singleton-inclusive | Public subset during event; private remainder determines final ranking; guidelines also say shortlisting considers both leaderboards | No external identity lookup/augmentation; MIT/Apache 2.0 model ≤8B parameters; output and package validation rules | Top 100 announced after artifacts, score, and eligibility; top 100 provide methodology, blocking, architecture/features, and approach details. Strong/top packages may be reviewed before final ranks. |

Sources: [Problem statement, pp. 1–7](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf); [2026 Guidelines, p. 1](sources/6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf).

**[OFFICIAL]** Inputs contain name variation (abbreviations, legal suffixes, DBAs, punctuation, reordered words, typos) and address variation (abbreviations, transliterations, missing components, landmarks, municipal-number formats, reordered components). The test includes France as an unseen country; the country field must be treated as open-set and all test entities must be represented. ([Problem statement, pp. 1–2](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

## 7. Winner & Finalist Solution Patterns

No winning or finalist team write-ups, ranks, or scores are present in the available documents. Do not infer actual winning approaches from the official tips.

| Year | Rank/Team | Approach | Key Features | Model | Validation | Post-processing | Score |
|---|---|---|---|---|---|---|---|
| 2026 | Not verified from available documents | Not verified | Not verified | Not verified | **[OFFICIAL task guidance]** Hold out training data; score with F0.5. | Not verified | Not verified |

**[OFFICIAL guidance, not a winning-team claim]** The problem statement suggests blocking/candidate generation, Jaccard/Levenshtein/TF-IDF cosine similarity for names and addresses, attention to country-specific address patterns, precision/recall tradeoff, singleton detection, and local output validation. ([Problem statement, p. 7](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

## 8. Recurring Technical Principles

The source set has only one competition year and no documented team solutions. Therefore, no principle can responsibly be described as recurring across years or repeatedly demonstrated by successful teams. The following are **single-edition official task requirements or guidance**, not cross-year patterns:

| Principle | Evidence and status |
|---|---|
| Metric-first decisions | **[OFFICIAL 2026]** F0.5 macro-average and precision-heavy penalty are explicitly described. |
| Data understanding | **[OFFICIAL 2026]** Names/addresses are noisy; test includes unseen France; country must remain open-set. |
| Candidate generation | **[OFFICIAL 2026]** Candidate output is required and blocking controls recall ceiling; candidate set is audited. |
| Metric-aligned similarity features | **[OFFICIAL 2026 guidance]** Jaccard, Levenshtein, TF-IDF cosine suggested. |
| Validation and error analysis | **[OFFICIAL 2026]** Hold out training data and calculate F0.5; singleton outcomes explicitly matter. Detailed error-analysis requirements are not stated. |
| Generalization | **[INFERENCE, based on official data description]** Open-set country handling and private test evaluation favor robust generalization; this is not an official scoring category. |
| Reproducibility and compliance | **[OFFICIAL 2026]** Self-contained runnable code, pinned dependencies, documentation, code and outputs are required for final package; external lookup is prohibited. |
| Ensembles, advanced architectures, post-processing | No winning-team evidence; not verified as expected or recurring. |

## 9. Validation, Error Analysis & Generalization

- **[OFFICIAL]** Create a holdout from training data and score it using the exact per-Source-1 macro F0.5 formula. ([Problem statement, p. 2 and p. 4](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))
- **[INFERENCE]** Split at the entity/source grouping level so related records do not leak across train and validation. The official document does not prescribe a split strategy; this is a prudent safeguard for matching data, not an official requirement.
- **[OFFICIAL]** Candidate recall and reduction ratio are analyzed through `candidate_pairs.tsv`; final predictions must be a subset of that file. ([Problem statement, pp. 3–4](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))
- **[INFERENCE]** Report blocking recall (fraction of true matches retained), candidate reduction, precision/recall and F0.5 by entity class, country, source pairing, and singleton status. Inspect false merges separately because the metric emphasizes precision.
- **[OFFICIAL]** France is absent in training but present in test. Avoid hard-coding training country values, dropping unseen labels, or relying on a closed-set country encoding. ([Problem statement, p. 2](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))
- **[INFERENCE]** Keep a final validation set untouched during feature/threshold selection to reduce overfitting to iterative experimentation. The documents do not define a validation protocol.

## 10. Compute & Scalability

**[OFFICIAL]** The final model cap is 8 billion parameters and its license must be MIT or Apache 2.0. External identity lookup is prohibited. No hardware, runtime, memory, inference latency, or package-size limits are documented in the available files. ([Problem statement, pp. 6–7](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

**[INFERENCE]** Pairwise comparison across all records can grow prohibitively; blocking reduces candidate volume and is explicitly central to the supplied artifact review. Track candidate counts, recall and runtime. Ensure the complete test pipeline can run from packaged code and dependencies. No specific compute target is verified.

## 11. Finalist / Amazon Scientist Question Bank

The documents require a methodology explanation, but do not provide actual scientist interview questions. Questions below are **[INFERENCE]** prompts derived from task requirements, not verified historical questions:

1. How did you define the validation split, and how did you prevent entity or source leakage?
2. What is the candidate-generation recall and reduction ratio? Where are true matches lost?
3. Why does your decision threshold optimize macro F0.5 rather than a pooled metric?
4. How do you distinguish a true singleton from a blocked-out match?
5. Which name and address normalizations help, and which can accidentally merge distinct businesses?
6. How does the pipeline handle an unseen country such as France?
7. Which false-positive and false-negative clusters remain, and what evidence supports your fixes?
8. Can an independent reviewer reproduce both TSV files from the packaged training/test inputs?
9. What model license and parameter count apply? Does any component access external data or services?
10. What are the runtime, memory, and candidate-volume tradeoffs?

**[OFFICIAL]** 2026 materials request a 1–2 page approach/model/experiments/conclusion note and source code with comments in the guidelines; the problem statement's final package template asks for methodology, blocking, architecture/features, and relevant details, with no page limit and clarity/technical depth prioritized. The top 100 are asked for these details. The documents differ in scope and expected length; satisfy the more detailed final package template if shortlisted. ([2026 Guidelines, p. 1](sources/6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf); [Problem statement, pp. 5–6](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf))

## 12. Common Failure Modes

The following are grounded in explicit 2026 instructions; observed frequency among teams is not documented:

- **[OFFICIAL]** Reading TSV as comma-separated can silently make one column; always specify tab separator. (Problem statement, p. 1.)
- **[OFFICIAL]** Dropping unseen country records or hard-coding only US/India violates the open-set instruction and omits France test entities. (p. 2.)
- **[OFFICIAL]** Poor blocking caps recall; final outputs not contained in candidate pairs indicate a pipeline bug. (pp. 3, 7.)
- **[OFFICIAL]** Missing Source 1 rows, duplicate IDs, nonexistent or Source 1 matched IDs, and invalid formatting cause rejection. (pp. 3–4.)
- **[OFFICIAL]** False merges, including on singleton entities, are strongly penalized. (p. 4.)
- **[OFFICIAL]** External business lookups/data augmentation can result in immediate disqualification. (p. 7.)
- **[OFFICIAL]** Multiple participant IDs, plagiarism, unfair practices, or simultaneous logins can trigger disqualification/termination. (2026 Guidelines, p. 1.)
- **[INFERENCE]** Overfitting submission iterations to the public leaderboard risks weaker private performance; the documents establish separate public/private portions but do not describe observed overfitting cases.

## 13. Candidate Skill Requirements

**[INFERENCE from the 2026 task and required artifacts]** A prepared candidate should be able to:

- Formalize one-to-many entity matching and explain set-based precision/recall.
- Inspect messy names and addresses, identify variation patterns, and build robust normalization/features.
- Design blocking with measured recall and manageable candidate volume.
- Tune a precision-sensitive decision process and handle no-match/singleton cases.
- Build validation that reflects the scoring aggregation and guards against leakage.
- Produce clean, schema-valid TSV output and test it with the supplied validator.
- Package a reproducible pipeline with pinned dependencies and a clear technical write-up.
- Explain compliance, model license/size, generalization and computational tradeoffs.

## 14. Amazon-Ready Project Architecture

This is a **[INFERENCE]** implementation blueprint derived from the 2026 task and submission package, not Amazon's prescribed architecture.

1. **Input contract:** explicit TSV loading; schema, ID uniqueness, source-prefix and null checks; preserve unseen country values.
2. **Profiling:** counts, missingness, country/source distributions, label cardinalities, name/address noise examples.
3. **Normalization/features:** preserve raw text; create conservative normalized name/address variants; country-aware parsing that does not require known country labels; similarity features such as token overlap, edit similarity and TF-IDF cosine.
4. **Blocking:** union complementary exact/normalized/token/inverted-index rules; retain candidate provenance; measure validation recall and reduction ratio.
5. **Matching:** calibrated pair scorer or interpretable threshold rules; tune for per-entity macro F0.5; explicit no-match/singleton decision.
6. **Validation:** entity-safe holdout; exact competition metric; slice reports and reviewed false-positive/negative examples.
7. **Output:** create one row per test Source 1 ID; only existing Source 2/3 IDs; de-duplicate; enforce matches ⊆ candidates; write UTF-8 TSV with exact headers.
8. **Reproduction:** packaged source, README with exact commands, pinned dependencies, methodology file, both outputs, local validator.

## 15. Competition Preparation Checklist

- [ ] Confirm challenge dates, portal rules, eligibility, and submission counter.
- [ ] Read current-year statement and guidelines independently; version all submissions.
- [ ] Load every TSV with an explicit tab separator and validate schemas/IDs.
- [ ] Profile train/test differences, missingness, noise, and unseen categories/countries.
- [ ] Establish a leakage-resistant validation holdout and implement exact macro F0.5 including singletons.
- [ ] Build blocking first; measure candidate recall and reduction ratio.
- [ ] Engineer name/address similarity features; validate normalization against false merges.
- [ ] Tune the matcher and singleton/no-match threshold for the actual metric.
- [ ] Analyze false positives/negatives by country, source, and entity size.
- [ ] Avoid external lookup or augmentation; verify model license and ≤8B parameter limit.
- [ ] Generate complete `matching_results.tsv` and `candidate_pairs.tsv`; verify subset and ID constraints.
- [ ] Run the provided submission validator.
- [ ] Package runnable source, pinned dependencies, README, methodology, outputs; reproduce from package contents.
- [ ] Prepare to explain design choices, experiments, failures, performance tradeoffs, and compliance.

## 16. Historical Trends

**Not verified from available documents.** There is no basis here to claim how the competition has changed from 2021 onward or whether any particular method has repeatedly won.

Within the single documented 2026 edition, the materials combine a live leaderboard exercise with an auditable final package, requiring both a scored prediction artifact and evidence of the process that generated it. **[INFERENCE]** This indicates emphasis on practical ML delivery and reviewability, but cannot be generalized to prior editions.

## 17. Evidence Gaps / Unverified Claims

- 2021–2025 problems, datasets, metrics, restrictions, finalist selection, winners, team solutions, scores and question/interview history: **Not verified from available documents.**
- Whether pretrained models are allowed, if so which weights/data, and whether local LLMs are acceptable: **Not verified from available documents.** The external lookup ban and license/size rule do not settle this.
- Exact submission portal behavior beyond stated caps, schedule and file instructions: **Not verified from available documents.**
- Exact public/private leaderboard split size and the rule combining both for shortlisting: **Not verified from available documents.**
- Hardware/runtime limits: **Not verified from available documents.**
- Actual winning/finalist approaches and measured recurring techniques: **Not verified from available documents.**
- Exact page mapping for extracted sections is given wherever available; section titles are used where printed pagination may differ in a PDF viewer.
- The user-specified E: directory could not be accessed because the drive is not mounted; only the two mirrored PDFs were available for analysis.

## 18. Source Index

| Source | Type / evidence class | Relevant content |
|---|---|---|
| [6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf](sources/6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf) | Official 2026 competition problem statement | ER task, dataset/schema/noise, test-only France, TSV output formats, candidate-pair audit, submission package, F0.5 formula, leaderboards, model constraints, prohibited lookup, official tips. 8 pages. |
| [6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf](sources/6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026.pdf) | Official 2026 guidelines | Event dates, 5 submissions/day, artifacts, public/private evaluation and top-100 process, device/login and fair-play instructions. 2 pages. |

No winner or participant sources were available; no `[WINNER/FINALIST]` or `[PARTICIPANT]` claims are made.

### What Amazon ML Challenge Is Really Testing

**[INFERENCE, limited to the available 2026 evidence]** The challenge tests whether a candidate can turn messy, incomplete records into defensible entity-level decisions under a precision-heavy metric. The candidate must understand noisy data, preserve recall through blocking, avoid false merges, recognize true no-match cases, validate against the actual macro score, handle unseen categories, and deliver a compliant, reproducible pipeline. The final package and review requirements also test whether the candidate can explain and reproduce the work. The two available documents do not establish that these expectations recur across historical editions.

### If I Want to Rank Highly, What Must My Project Demonstrate?

These categories are practical synthesis, **not Amazon's official scoring rubric**.

**Must-have**
- Correct complete output, strict format, valid IDs, and matches contained in candidates.
- Leakage-aware validation with the exact singleton-inclusive macro F0.5.
- Strong candidate recall and precision-conscious final matching.
- Compliance with external-data, licensing, and model-size rules.
- Reproducible code, dependencies, outputs, and clear methodology.

**High-value**
- Thorough EDA and noise-aware name/address feature engineering.
- Measured blocking recall/reduction, threshold calibration, singleton detection, and false-merge analysis.
- Robust treatment of unseen countries and private-set generalization.
- Efficient inference with runtime/candidate counts documented.

**Problem-dependent**
- Country-specific address parsing, transliteration handling, advanced string models, or ensemble strategies when validation demonstrates value.
- Specialized model architectures only if licensing, size, and competition rules are satisfied.

**Nice-to-have**
- Candidate provenance and diagnostics that make review easier.
- Clear ablations and sensitivity analysis around thresholds and blocking rules.
- A concise presentation that explains decisions, tradeoffs, experiments, and remaining errors.
