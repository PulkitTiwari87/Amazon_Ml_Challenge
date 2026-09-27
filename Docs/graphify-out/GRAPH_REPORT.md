# Graph Report - Amazon Ml Challange  (2026-09-25)

## Corpus Check
- 3 files · ~14,265 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 147 nodes · 337 edges · 8 communities
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 82 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Modeling Principles & Deliverables
- Past Editions & Support
- Documentation & Feature Design
- Submission Files & Validation
- ER Task & Dataset
- Rules & Leaderboards
- Forensic Analysis & Finale
- F0.5 Metric & Thresholding

## God Nodes (most connected - your core abstractions)
1. `Amazon ML Challenge Master Knowledge Base` - 52 edges
2. `Consolidated problem and guidelines summary` - 17 edges
3. `Guidelines and Key Instructions (Amazon ML Challenge 2026)` - 14 edges
4. `Blocking / candidate generation` - 13 edges
5. `Business Entity Resolution Challenge` - 13 edges
6. `F_0.5 evaluation metric` - 12 edges
7. `validate()` - 11 edges
8. `Problem Statement PDF (Business Entity Resolution Challenge)` - 11 edges
9. `Self-scored validation holdout from training data` - 9 edges
10. `Amazon ML Challenge timeline 2021-2025` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Problem Statement PDF (Business Entity Resolution Challenge)` --semantically_similar_to--> `README: ML Challenge 2026 Problem Statement`  [INFERRED] [semantically similar]
  6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf → 6ab10eb3b23ba_student_resource/student_resource/README.md
- `Principle: exact submission format compliance` --conceptually_related_to--> `validate()`  [INFERRED]
  Amazon ML Challenge Forensic Analysis.md → 6ab10eb3b23ba_student_resource/student_resource/utils/validate_submission.py
- `Problem Statement PDF (Business Entity Resolution Challenge)` --references--> `F_0.5 evaluation metric`  [INFERRED]
  6ab5628d5a817_amazon_ml_challenge_problem_statement.pdf → 6ab10eb3b23ba_student_resource/student_resource/README.md
- `Principle: exact submission format compliance` --semantically_similar_to--> `Output validity rules`  [INFERRED] [semantically similar]
  Amazon ML Challenge Forensic Analysis.md → 6ab10eb3b23ba_student_resource/student_resource/README.md
- `Failure mode: false merges including on singletons` --semantically_similar_to--> `Recurring failure modes (OOM, non-compliance, weak parsing)`  [INFERRED] [semantically similar]
  AMAZON_ML_CHALLENGE_MASTER.md → Amazon ML Challenge Forensic Analysis.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Entity resolution pipeline: blocking to matching to scored output** — 6ab10eb3b23ba_student_resource_student_resource_readme_blocking, 6ab10eb3b23ba_student_resource_student_resource_readme_candidate_pairs, 6ab10eb3b23ba_student_resource_student_resource_readme_matching_model, 6ab10eb3b23ba_student_resource_student_resource_readme_matching_results, 6ab10eb3b23ba_student_resource_student_resource_readme_f05 [EXTRACTED 0.95]
- **Final submission zip contents** — 6ab10eb3b23ba_student_resource_student_resource_readme_package, 6ab10eb3b23ba_student_resource_student_resource_readme_matching_results, 6ab10eb3b23ba_student_resource_student_resource_readme_candidate_pairs, 6ab10eb3b23ba_student_resource_student_resource_readme_reproducible_code, 6ab10eb3b23ba_student_resource_student_resource_readme_method_doc [EXTRACTED 1.00]
- **Fair play and compliance rules** — 6ab10eb3b23ba_student_resource_student_resource_readme_external_lookup, 6ab10eb3b23ba_student_resource_student_resource_readme_model_license, 6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026_fairplay, amazon_ml_challenge_forensic_analysis_compliance, amazon_ml_challenge_forensic_analysis_llm_ban [INFERRED 0.85]
- **Submission validity constraints** — 6ab10eb3b23ba_student_resource_student_resource_readme_subset_rule, 6ab10eb3b23ba_student_resource_student_resource_readme_matching_results, 6ab10eb3b23ba_student_resource_student_resource_readme_candidate_pairs, 6ab10eb3b23ba_student_resource_student_resource_readme_tsv [EXTRACTED 0.85]
- **Precision-first ER pipeline: blocking, matching, threshold, singleton handling** — 6ab10eb3b23ba_student_resource_student_resource_readme_blocking, 6ab10eb3b23ba_student_resource_student_resource_readme_matching_model, amazon_ml_challenge_master_threshold_separation, 6ab10eb3b23ba_student_resource_student_resource_readme_singletons, 6ab10eb3b23ba_student_resource_student_resource_readme_f05 [INFERRED 0.75]
- **Compliance constraints: no external lookup, model license/size, fair play** — 6ab10eb3b23ba_student_resource_student_resource_readme_external_lookup, 6ab10eb3b23ba_student_resource_student_resource_readme_model_license, 6ab56657b4f1a_guidelines_and_key_instructions_amazon_ml_challenge_2026_fairplay [EXTRACTED 0.85]

## Communities (8 total, 0 thin omitted)

### Community 0 - "Modeling Principles & Deliverables"
Cohesion: 0.13
Nodes (26): Self-scored validation holdout from training data, Methodology document requirements, Model constraint: MIT/Apache 2.0 license, up to 8B parameters, business_name field, Name noise patterns, Required artefacts: 1-2 page document and commented source code, Top 100 teams follow-up documents, Principle: data-first modeling (80/20 EDA) (+18 more)

### Community 1 - "Past Editions & Support"
Cohesion: 0.10
Nodes (26): Technical support via Unstop email, Unstop hosting platform, 2023 winner: ART in Artificial Intelligence, Principle: baseline-first experimentation, 2021 edition: browse node classification (subset accuracy), 2023 edition: product length regression (MAPE), 2024 edition: image entity extraction (F1), 2025 edition: Smart Product Pricing (SMAPE) (+18 more)

### Community 2 - "Documentation & Feature Design"
Cohesion: 0.15
Nodes (21): Documentation_template.md (methodology write-up template), Solution approach type (blocking + classifier, end-to-end, graph-based, hybrid), Code artefacts appendix and entry points, Error analysis: wrong merges and missed matches, Feature engineering (name, address, other features), Threshold selection by F_0.5 optimization on validation set, Address noise patterns, business_address field (+13 more)

### Community 3 - "Submission Files & Validation"
Cohesion: 0.17
Nodes (20): README: ML Challenge 2026 Problem Statement, candidate_pairs.tsv (blocking candidate set), matching_results.tsv (leaderboard-scored output), Output validity rules, Final submission package (team zip), Final matches must be a subset of candidates, examples(), load_match_targets() (+12 more)

### Community 4 - "ER Task & Dataset"
Cohesion: 0.17
Nodes (18): Zero, one or many matches per Source 1 entity, Business Entity Resolution Challenge, country field (open set of labels), entity_id column (S1-/S2-/S3- prefix), Entity Resolution (ER), France (test-only unseen country), train_ground_truth.tsv, Source 1 (deduplicated reference source) (+10 more)

### Community 5 - "Rules & Leaderboards"
Cohesion: 0.18
Nodes (18): Prohibition on external data lookup, Public and private leaderboards, Tab-separated (.tsv) file format, Guidelines and Key Instructions (Amazon ML Challenge 2026), Access rules: desktop/laptop only, no simultaneous logins, Fair play and instant disqualification (multiple IDs, cheating, plagiarism), Submission limit: 5 per day for 3 days, Challenge window: 25-27 Sep 2026 IST (3 days) (+10 more)

### Community 6 - "Forensic Analysis & Finale"
Cohesion: 0.36
Nodes (9): Amazon ML Challenge Forensic Analysis, Target profile: resourceful, mathematically grounded Applied Scientist, Grand Finale presentation to Amazon scientists (Top 10), Multi-tier judging: leaderboard, document review, finale, Prizes and Pre-Placement Interview (PPI) linkage, Amazon scientist question bank for finalists, Candidate skill matrix, Inferred finalist question prompts (10 questions) (+1 more)

### Community 7 - "F0.5 Metric & Thresholding"
Cohesion: 0.46
Nodes (8): F_0.5 evaluation metric, Per-entity macro-average scoring, Singleton handling (empty list scores 1.0), Conservative thresholding under F0.5, F0.5 formula and per-entity macro-average, Failure mode: false merges including on singletons, Slice reports by country, source pairing, singleton status, Tune candidate coverage and decision threshold separately

## Knowledge Gaps
- **7 isolated node(s):** `business_address field`, `Principle: modularity and model diversity`, `LoRA / QLoRA quantized fine-tuning`, `README: ML Challenge 2026 Problem Statement`, `Line-level citations to problem statement pages` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 13 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Amazon ML Challenge Master Knowledge Base` connect `Modeling Principles & Deliverables` to `Past Editions & Support`, `Documentation & Feature Design`, `Submission Files & Validation`, `ER Task & Dataset`, `Rules & Leaderboards`, `Forensic Analysis & Finale`, `F0.5 Metric & Thresholding`?**
  _High betweenness centrality (0.467) - this node is a cross-community bridge._
- **Why does `Business Entity Resolution Challenge` connect `ER Task & Dataset` to `Past Editions & Support`, `Submission Files & Validation`, `Rules & Leaderboards`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `Amazon ML Challenge timeline 2021-2025` connect `Past Editions & Support` to `Modeling Principles & Deliverables`, `Forensic Analysis & Finale`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Blocking / candidate generation` (e.g. with `Address noise patterns` and `Name noise patterns`) actually correct?**
  _`Blocking / candidate generation` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Business Entity Resolution Challenge` (e.g. with `Prohibition on external data lookup` and `Problem Statement PDF (Business Entity Resolution Challenge)`) actually correct?**
  _`Business Entity Resolution Challenge` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `business_address field`, `Principle: modularity and model diversity`, `LoRA / QLoRA quantized fine-tuning` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Modeling Principles & Deliverables` be split into smaller, more focused modules?**
  _Cohesion score 0.12923076923076923 - nodes in this community are weakly interconnected._