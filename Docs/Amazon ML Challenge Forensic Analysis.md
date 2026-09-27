# **Forensic Research Report: The Amazon ML Challenge Candidate Profile and Evaluation Mechanisms**

## **Executive Summary**

The Amazon ML Challenge serves as a critical identification pipeline for collegiate machine learning talent in India, operating as a rigorous evaluation mechanism for prospective Applied Scientist interns and full-time engineers. This comprehensive forensic analysis deconstructs the competition’s architecture from its inception in 2021 through the 2025 edition, providing an evolutionary perspective on the upcoming 2026 challenge. By reverse-engineering official judging guidelines, historical dataset characteristics, documented finalist presentations, and open-source winner repositories, the ensuing analysis isolates the core technical and engineering capabilities that Amazon evaluates. The findings demonstrate a definitive historical shift from classical machine learning and structured tabular data parsing toward compute-constrained, multimodal deep learning and robust system-level pipeline architecture. The analysis indicates that candidates are primarily tested on their ability to translate ambiguous business objectives into strict mathematical metrics, execute rigorous local validation under severe compute constraints, and defend complex architectural decisions before senior industry scientists.

## **1\. Amazon ML Challenge Timeline**

The historical structure of the competition reveals a systematic escalation in problem complexity, dataset dimensionality, and compliance rigidity. The following table reconstructs the operational and structural history of the competition.

| Dimension | 2021 | 2022 | 2023 | 2024 | 2025 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Competition Dates** | July 20211 | Jul 29–31, 20222 | Not publicly verified from accessible primary sources. | Sep 13–15, 20243 | Oct 10–13, 2025 (Round 1); Oct 17, 2025 (Finale)4 |
| **Hosting Platform** | HackerEarth1 | HackerEarth2 | HackerEarth \[INFERENCE\] | Unstop4 | Unstop4 |
| **Eligibility** | Engineering professionals / students6 | Engineering students graduating 2022/20239 | Engineering students10 | Engineering students7 | B.E/B.Tech/M.E/M.Tech/PhD graduating 2026/20274 |
| **Team Size** | Not publicly verified from accessible primary sources. | 2–4 members9 | 4 members12 | 3–4 members7 | 3–4 members4 |
| **Problem Statement** | Classify products into hierarchical browse nodes5 | Predict browse node assignment from metadata13 | Predict product length dimension10 | Extract specific product entity values from images7 | Predict product price holistically14 |
| **ML Task Type** | Multiclass Classification5 | Multiclass Classification13 | Regression10 | Multimodal Extraction / Optical Character Recognition7 | Multimodal Regression14 |
| **Dataset Size** | 2.9M Train, 110K Test5 | Not publicly verified from accessible primary sources. | 2.2M Train, 734K Test10 | \~260,000+ images17 | 75K Train, 75K Test14 |
| **Modalities** | Text/Tabular5 | Text/Tabular13 | Text/Tabular10 | Image, Text7 | Image, Text14 |
| **Target Variable** | BROWSE\_NODE\_ID \[cite: 5\] | BROWSE\_NODE\_ID \[cite: 13\] | PRODUCT\_LENGTH \[cite: 10\] | entity\_value \[cite: 7\] | price \[cite: 14\] |
| **Evaluation Metric** | Subset Accuracy5 | Not publicly verified from accessible primary sources. | Mean Absolute Percentage Error (MAPE)10 | F1 Score18 | Symmetric Mean Absolute Percentage Error (SMAPE)14 |
| **Metric Formula** | Exact label set match5 | Not publicly verified from accessible primary sources. | ![][image1] \[cite: 10\] | ![][image2] \[cite: 18\] | ![][image3] \[cite: 14\] |
| **Leaderboard Structure** | Public/Private Split4 | Public/Private Split \[INFERENCE\] | Public/Private Split4 | Public/Private Split4 | Public/Private Split4 |
| **Public/Private Split** | Not publicly verified from accessible primary sources. | 50% Public evaluation during contest19 | Not publicly verified from accessible primary sources. | Not publicly verified from accessible primary sources. | Private leaderboard evaluated on full 75K test set14 |
| **Submission Limits** | Not publicly verified from accessible primary sources. | Not publicly verified from accessible primary sources. | Not publicly verified from accessible primary sources. | 15 Submissions3 | Not publicly verified from accessible primary sources. |
| **Required Documentation** | Source code & Presentation8 | Not publicly verified from accessible primary sources. | Strict CSV format limits10 | 2-page methodology document7 | 1-page methodology document14 |
| **Code Submission** | Zip file required8 | Not publicly verified from accessible primary sources. | Not publicly verified from accessible primary sources. | Zip file required7 | Zip file required4 |
| **Model Constraints** | None explicitly noted. | Not publicly verified from accessible primary sources. | None explicitly noted. | No commercial LLM APIs permitted3 | Maximum 8 Billion parameters, MIT/Apache 2.0 license required14 |
| **Data Restrictions** | Not publicly verified from accessible primary sources. | Not publicly verified from accessible primary sources. | Not publicly verified from accessible primary sources. | No commercial LLM APIs3 | Strict prohibition on external price lookup or web scraping14 |
| **LLM/API Restrictions** | Not applicable (2021 landscape) | Not applicable. | Not publicly verified from accessible primary sources. | Banned usage of proprietary APIs (OpenAI, Anthropic, Google)3 | Must utilize open-source models capable of local inference14 |
| **Finalist Selection** | Top 10 via Leaderboard \+ Documentation4 | Not publicly verified from accessible primary sources. | Top 10 via Leaderboard \+ Documentation4 | Top 10 via Leaderboard \+ Documentation7 | Top 10 via Leaderboard \+ Documentation4 |
| **Number of Finalists** | 10 Teams4 | Not publicly verified from accessible primary sources. | 10 Teams12 | 10 Teams7 | 10 Teams4 |
| **Finale Requirements** | Presentation to scientists4 | Not publicly verified from accessible primary sources. | Presentation to scientists12 | Virtual presentation to scientists7 | Virtual presentation to Amazon Scientists4 |
| **Prizes** | Pre-Placement Interviews (PPIs) \+ Cash6 | Not publicly verified from accessible primary sources. | PPIs \+ Cash \[INFERENCE\] | PPIs \+ Cash7 | ₹1,00,000 (1st), ₹75,000 (2nd), ₹50,000 (3rd)4 |
| **PPI / PPO Linkage** | Pre-Placement Interview opportunity6 | Not publicly verified from accessible primary sources. | Top 50 teams awarded Online Assessment / PPI12 | Top 50 teams awarded PPI for Applied Scientist Intern7 | Top 50 teams awarded PPI for Applied Scientist Intern4 |

## **2\. Official Judging Rules by Year**

A forensic mapping of the official evaluation rules demonstrates that Amazon utilizes a multi-tiered filtering mechanism, relying first on automated empirical evaluation and subsequently on deep human peer review.

### **A. Automated Leaderboard Scoring**

Automated scoring determines the initial rank trajectory during the limited hackathon window. The evaluation metric is rigorously mathematical and uniformly applied to a subset of the test data (for example, exactly 50% of the test data during the active 2022 contest window) \[OFFICIAL\]19. This public leaderboard serves strictly as a temporary benchmark, deliberately engineered to punish teams that overfit to the visible distribution.

### **B. Private Leaderboard Scoring**

The private leaderboard operates as the final quantitative arbiter of predictive capability. Submissions are rigorously validated against the complete, held-out test dataset, as explicitly documented in the 2025 edition where final rankings were computed on the entire 75,000-item test set \[OFFICIAL\]14. Does the private leaderboard override the public leaderboard? Yes. \[OFFICIAL\] The final empirical standings are derived exclusively from this private validation phase4. Is the winner determined purely by the metric? No. \[OFFICIAL\] The quantitative score acts strictly as a gateway filter, determining which teams advance to the mandatory documentation review and the presentation phases4.

### **C. Human Evaluation / Document Review**

Can documentation influence finalist selection? Yes. \[OFFICIAL\] The determination of the Top 10 finalists involves a human review of a mandatory one-to-two-page methodology document. Evaluators assess the selected model architecture, algorithmic efficiency, and the sophistication of the applied feature engineering techniques \[OFFICIAL\]14. Furthermore, technical submissions that fail basic sanity checks or strict formatting rules (e.g., mismatched sample counts) are discarded without evaluation \[OFFICIAL\]21.

### **D. Finale Presentation Evaluation**

Can the presentation influence the final winner selection? Yes. \[OFFICIAL\] The Top 10 teams are invited to a Grand Finale to defend their solutions in a live virtual environment before Amazon Scientists. The final hierarchical ranking (Winners, First Runners-up, Second Runners-up) is decided entirely at this stage \[OFFICIAL\]4. Are there published human-judging categories? Teams are historically questioned on fundamental problem understanding, theoretical mathematics, technical architecture, and system limitations \[DOCUMENTED PARTICIPANT PATTERN\]12. However, regarding a granular, numeric score sheet: NO PUBLIC NUMERIC RUBRIC FOUND. \[OFFICIAL\] Are there tie-breaking rules? Not publicly verified from accessible primary sources.

### **E. Eligibility / Compliance Checks**

Are experiments and code audited? Yes. \[OFFICIAL\] All submitted code pipelines, methodologies, and models are thoroughly reviewed and verified prior to the final standings announcement14. The 2025 edition featured strict parameter constraints, requiring models to remain under 8 Billion parameters and to be licensed under open-source MIT or Apache 2.0 structures \[OFFICIAL\]14.

### **F. Disqualification Conditions**

Are violations grounds for immediate disqualification? Yes. \[OFFICIAL\] Disqualification conditions are heavily enforced. Documented violations include registering with multiple IDs, academic cheating, and plagiarism3. Crucially, the usage of commercially available or proprietary Large Language Model APIs (e.g., OpenAI, Anthropic, Google) is strictly prohibited and results in immediate discarding of the submission3. In 2025, any evidence of external price lookups or web scraping to augment the training data was explicitly cited as grounds for instant disqualification \[OFFICIAL\]14.

## **3\. Historical Metrics and What They Reward**

The choice of evaluation metric is the most critical design decision in a machine learning competition. Amazon's historical selection of metrics dictates candidate engineering behavior, feature engineering priorities, and validation strategies.

### **Accuracy (2021)**

Mathematically, accuracy is defined as the ratio of correct predictions to total predictions. In the 2021 hierarchical classification task, Amazon required subset accuracy—mandating that the predicted set of labels for a sample exactly match the corresponding set of ground truth labels \[OFFICIAL\]5. This metric heavily rewards high-confidence, exact classification across thousands of potential browse nodes. It aggressively punishes near-misses or partial semantic matches within the hierarchy. This structure encourages rigid class boundaries and conservative prediction thresholding over continuous semantic similarity scoring. Validation strategies required stratified sampling across the massive 9,919 class distribution to ensure robust representation of long-tail nodes.

### **MAPE (2023)**

The Mean Absolute Percentage Error (MAPE) is mathematically defined as ![][image4]. Amazon inverted this into a maximization score using the formula ![][image1] \[OFFICIAL\]10. This metric rewards predictions that are proportionally close to the true value, making it scale-invariant. However, MAPE disproportionately punishes over-prediction. If the actual length is 10 and the prediction is 20, the error is 100%; if the prediction approaches zero, the error is capped at 100%, but overestimating by multiples creates unbounded mathematical penalties. Consequently, this encourages the implementation of asymmetric loss functions during model training that artificially penalize overestimations \[INFERENCE\]. A common failure mode involves teams optimizing for Mean Squared Error (MSE) during training, thereby inadvertently producing highly penalized outlier over-predictions on the leaderboard.

### **F1 Score (2024)**

Mathematically, the F1 Score is the harmonic mean of precision and recall (![][image2]) \[OFFICIAL\]18. In the context of entity extraction from images, it rewards the delicate balance between correctly identifying an entity value and missing none of the existing entities. It severely punishes false positives (hallucinations generated by Vision-Language Models) and false negatives (missed text due to suboptimal Optical Character Recognition). Because the evaluation script required exact string formatting (e.g., "34 gram"), it heavily encouraged rigorous confidence calibration and exhaustive Regex-based post-processing \[DOCUMENTED PARTICIPANT PATTERN\]7. Teams accidentally optimized the wrong objective by improving their model's semantic understanding without building the necessary string-parsing pipelines, resulting in zero-scores despite accurate visual recognition.

### **SMAPE (2025)**

Symmetric Mean Absolute Percentage Error (SMAPE) is mathematically defined as ![][image3] \[OFFICIAL\]14. SMAPE treats positive and negative errors symmetrically, bounding the total relative error between 0% and 200%. This rewards stable, bounded predictions in highly skewed datasets like e-commerce pricing. It punishes extreme outliers, though less violently and asymmetrically than raw MSE or standard MAPE. This encouraged top-tier teams to engineer custom log-based MSE loss functions during deep learning training to mathematically approximate the SMAPE evaluation curve \[DOCUMENTED PARTICIPANT PATTERN\]15.

### **F0.5 Score (2026 Evolution Reference)**

Mathematically, F0.5 weights precision twice as heavily as recall. It rewards extreme certainty before merging entities and heavily punishes false positives (false merges). This encourages highly conservative thresholding in similarity graphs, where the cost of mistakenly combining two distinct businesses is engineered to be substantially higher than the cost of maintaining them as singletons \[INFERENCE\].

### **WHAT AMAZON'S CHOICE OF METRICS REVEALS ABOUT THE ENGINEERING SKILLS BEING TESTED**

The chronological evolution of these metrics reveals a strategic transition from testing basic classification logic (Subset Accuracy) to advanced, business-aligned risk management (SMAPE, F1, F0.5). By choosing SMAPE in 2025, Amazon signaled that candidates must understand how to bound relative error in volatile, real-world datasets where prices vary exponentially \[INFERENCE\]. Furthermore, the rigid format constraints inextricably linked to these metrics (such as the F1 score in 2024 requiring precise structural formatting like "34 gram" rather than "34g" or "34 grams" \[OFFICIAL\]7) test a candidate's capacity to implement robust post-processing and parsing systems. Amazon evaluates whether a candidate can deploy machine learning models that interact seamlessly with strict downstream databases and legacy software architectures \[INFERENCE\].

## **4\. Problem Statement Evolution**

Analyzing the historical problem statements across the 2021 to 2025 editions yields several recurring structural characteristics that define an Amazon-caliber challenge. The datasets are defined by their sheer scale, ranging from 2.2 million to 2.9 million structured rows in earlier editions \[OFFICIAL\]5 to highly compute-intensive pools of over 260,000 images in the multimodal era \[OFFICIAL\]17.  
Noise in real-world data is explicitly highlighted by the organizers as a primary hurdle ("Note that there is some noise in the data \- real world data looks like this\!\!") \[OFFICIAL\]5. Missing data and hidden contexts are prevalent, requiring models to predict complex node assignments even when explicit categorical information is absent \[OFFICIAL\]5. The competition has distinctly shifted toward multimodal data representation, moving from text-heavy metadata and bullet points to requiring simultaneous processing of product images and unstructured HTML-laden text \[OFFICIAL\]7. Across all years, the requirement for exact-format prediction and data normalization remains invariant, forcing models to conform to rigid business ontologies.  
*What type of ML problem should a candidate be prepared to solve when entering Amazon ML Challenge?* Rather than anticipating a specific task (such as computer vision or natural language processing in isolation), candidates must be prepared to solve a **high-volume, noisy, multi-modal feature mapping problem requiring extreme compute efficiency and stringent post-processing.** \[INFERENCE\] The exact algorithmic objective (classification vs. regression) varies, but the structural constant is the necessity of mapping raw, unstructured real-world catalog artifacts into strict quantitative or categorical business logic without relying on expensive, unscalable external LLM calls.

## **5\. Winner and Finalist Solution Analysis**

Forensic analysis of publicly available repositories, technical write-ups, and post-mortems from top-ranked teams reveals distinct, repeatable methodological choices that secure leaderboard dominance.

### **2023 Winner: Team "ART in Artificial Intelligence" (Rank \#1)**

12

* **Task:** Product Length Prediction (Regression).  
* **Strategy & Baseline:** The team established a strict timeline: utilizing baseline holdout validation on Day 1, refining the optimal approach on Day 2 without introducing new architectures, and dedicating Day 3 entirely to ensembling for leaderboard stabilization \[DOCUMENTED PARTICIPANT PATTERN\]12.  
* **Compute Constraints:** The team secured victory utilizing only free Kaggle GPUs, demonstrating that massive computational power was not strictly necessary for tabular and text-based tasks when the architecture is highly optimized \[DOCUMENTED PARTICIPANT PATTERN\]12.  
* **Documented Limitations:** The winners explicitly avoided deploying massive Large Language Models, opting instead for smaller, task-specific architectures combined with strategic data sampling to maintain the underlying distribution \[DOCUMENTED PARTICIPANT PATTERN\]12.

### **2024 Winner: Team "NeuralNinjas" (Rank \#1)**

18

* **Task:** Entity Extraction from Images (F1 Optimization).  
* **Model Architecture:** The team bypassed pure OCR pipelines and fine-tuned a Vision-Language Model, specifically Qwen2-VL-7B-Instruct, utilizing LLaMA-Factory with QLoRA (8-bit quantization) \[DOCUMENTED PARTICIPANT PATTERN\]18.  
* **Hyperparameters:** Execution required strict memory management, utilizing a batch size of 8, a learning rate of 5e-5, gradient accumulation steps of 8, and a cosine learning rate scheduler \[DOCUMENTED PARTICIPANT PATTERN\]18.  
* **Preprocessing & Error Correction:** The team aggressively cleaned the noisy dataset, systematically replacing invalid measurement units with "NA" and replacing ranges with maximum values to perfectly align with the rigid F1 evaluation script requirements \[DOCUMENTED PARTICIPANT PATTERN\]18.  
* **Final Score:** Achieved an F1 score of 0.865 on a curated 1,600-sample local validation set, leaping from a 0.679 baseline \[DOCUMENTED PARTICIPANT PATTERN\]18.

### **2025 Top Tier: Team "SPAM\_LLMs" (Rank \#5 Private Leaderboard)**

15

* **Task:** Smart Product Pricing (SMAPE Optimization).  
* **Model Architecture:** Implemented a robust multimodal ensemble featuring SigLIP2-Giant (1 Billion parameters) for cross-modal embeddings, alongside Qwen-3-4B for text understanding, and DinoV3 for pure image feature extraction \[DOCUMENTED PARTICIPANT PATTERN\]15.  
* **Key Insight:** The team discovered that utilizing massive, pretrained frozen encoders drastically outperformed smaller, extensively fine-tuned models due to the degradation of embedding quality in distilled architectures \[DOCUMENTED PARTICIPANT PATTERN\]15.  
* **Metric Optimization:** Engineered a custom Log-based Mean Squared Error (MSE) loss function to mathematically bridge the gap to the SMAPE evaluation bounds \[DOCUMENTED PARTICIPANT PATTERN\]15.  
* **Data Cleaning:** Implemented rigorous standardization mapping (e.g., converting "gms" to "grams") and transformed numerical digits into text words (e.g., "100" to "One Hundred") to substantially stabilize the embedding space \[DOCUMENTED PARTICIPANT PATTERN\]15.

### **2025 Top Tier: Team "NeelDevenShah" (Rank \#80)**

16

* **Task:** Smart Product Pricing.  
* **Strategy:** Heavily prioritized Exploratory Data Analysis (EDA) over immediate modeling (an application of the 80/20 rule). The architecture utilized CLIP-based image and brand features cascaded into traditional machine learning ensembles including XGBoost and LightGBM \[DOCUMENTED PARTICIPANT PATTERN\]16.  
* **Validation Method:** Relied on rigorous local validation on a meticulously stratified subset to avoid the common pitfall of public leaderboard overfitting \[DOCUMENTED PARTICIPANT PATTERN\]16.

### **REPEATED PATTERNS**

Analysis of these solutions allows for the categorization of technical approaches by their frequency and operational leverage.

* **Vision-Language Models (VLMs) (e.g., Qwen-VL, SigLIP2):** \[HIGH-LEVERAGE\] These architectures became the dominant paradigm in 2024 and 2025 for extracting contextual features from images, vastly outperforming legacy OCR pipelines \[DOCUMENTED PARTICIPANT PATTERN\]15.  
* **LoRA / QLoRA / Quantization:** \[COMMON\] Absolutely essential for fine-tuning multi-billion parameter models within the 40-80GB VRAM limits of accessible hardware or free Kaggle tier environments \[DOCUMENTED PARTICIPANT PATTERN\]17.  
* **Optical Character Recognition (OCR):** \[OCCASIONAL\] Utilized extensively by lower-ranked teams in 2024, but frequently cited as a computational bottleneck that proved inferior to VLMs for complex spatial and contextual entity extraction \[DOCUMENTED PARTICIPANT PATTERN\]7.  
* **Ensembling & Stacking:** \[COMMON\] The standard operational practice for top-tier teams during the final 24 hours to stabilize predictive variance and insulate the submission against catastrophic private leaderboard shakeups \[DOCUMENTED PARTICIPANT PATTERN\]12.  
* **Regex & Entity Parsing:** \[HIGH-LEVERAGE\] A critical differentiator in 2024; the ability to convert raw text outputs into exact string formats was often the sole barrier between a winning score and a total failure \[DOCUMENTED PARTICIPANT PATTERN\]7.  
* **Unit Normalization & Target Encoding:** \[COMMON\] Standardizing label formats and transforming non-linear target distributions (e.g., logarithmic transformations for expansive price ranges) proved to be an invariant feature engineering requirement \[DOCUMENTED PARTICIPANT PATTERN\]15.

## **7\. Recurring Engineering Patterns**

The severe constraint of a 72-hour competition window enforces exceptional engineering discipline, yielding recurring operational patterns among finalists. Foremost among these is the strategy of compute stratification. Top-performing teams frequently utilized a hybrid hardware approach, implementing aggressive data chunking and batch processing to prevent out-of-memory errors on free Colab or Kaggle instances, while reserving paid cloud compute or university GPU clusters strictly for heavy, final-stage training epochs \[DOCUMENTED PARTICIPANT PATTERN\]12.  
Inference optimization also emerges as a distinct engineering priority. The implementation of Sparse Attention and Flash Attention mechanisms to manage the computational scaling constraints of Transformer architectures was critical to processing hundreds of thousands of images within the submission deadline \[DOCUMENTED PARTICIPANT PATTERN\]17. Furthermore, modality fusion strategies separated the elite teams from the rest. Rather than attempting to train a massive joint multimodal space from scratch, highly ranked teams utilized late fusion mechanisms—such as applying Gated Fusion to combine CLIP image embeddings with textual embeddings immediately prior to feeding them into an XGBoost regressor—to achieve high predictive power at a fraction of the computational cost \[DOCUMENTED PARTICIPANT PATTERN\]25.

## **8\. Recurring Finalist Presentation Patterns**

The Grand Finale mandates that the Top 10 teams defend their architectural choices in a live virtual environment before Amazon Applied Scientists \[OFFICIAL\]4. Detailed participant testimony provides a high-fidelity reconstruction of the expected inquiries, serving as an "Amazon Scientist Question Bank" \[DOCUMENTED PARTICIPANT PATTERN\]17.

| Evaluation Category | Representative Inquiries from Amazon Scientists |
| :---- | :---- |
| **Problem Understanding** | "Why is this problem structurally difficult? What are the primary sources of signal in this noisy dataset?" |
| **Data & Preprocessing** | "How did you systematically handle noise? How did you construct your validation splits to ensure no target leakage occurred?" |
| **Modeling Decisions** | "Why did you select this specific architecture over a computationally cheaper alternative? What is the fundamental difference between the VLM utilized and a standard LLM?" |
| **Mathematical Foundations** | "Explain the mathematical difference between Batch Norm and Layer Norm. Walk through the manual calculation of Entropy, Gini Index, and Information Gain for a hypothetical split." |
| **Experiments & Ablations** | "What approaches failed during the first 48 hours? What specific ablations drove the most significant performance gains?" |
| **Error Analysis** | "What specific edge cases does the model consistently fail on, and what is the underlying architectural reason for this failure?" |
| **Engineering & Scale** | "Trace a single token's journey through the Transformer architecture. How can Attention be optimized using Sparse or Flash Attention mechanisms?" |
| **Team Understanding** | "Can every member of the team explicitly defend the mathematical choices behind the rank decomposition matrices in your LoRA implementation?" |

## **9\. What Amazon Appears to Test**

Synthesizing the Official Rules, Metric Selection criteria, and Finale Interview testimonies allows for the inference of the underlying capabilities Amazon is actively filtering for. These capabilities are ranked by evidentiary strength.  
**A. Directly Documented by Amazon**

> 1. **Metric Optimization & Problem Formulation:** The ability to translate an ambiguous business objective (e.g., "Smart Pricing") into a highly specific statistical framework (SMAPE) without hallucinating logic \[OFFICIAL\]14.  
> 2. **Resource Efficiency & Compliance:** The capacity to innovate within strictly enforced parameters, such as the 8 Billion parameter maximum and the mandate to utilize only open-source, locally inferable models \[OFFICIAL\]14.

**B. Repeatedly Demonstrated by Top Solutions** 3\. **Multimodal Deep Learning Architecture:** Deep competence in deploying Vision-Language Models, utilizing frozen embeddings, and aligning disparate textual and visual modalities \[DOCUMENTED PARTICIPANT PATTERN\]15. 4\. **Data Engineering & Noise Robustness:** The discipline to write rigorous parsers, regular expressions, and standardizers to sanitize noisy "real-world" Amazon catalog data before it is introduced to the training pipeline \[DOCUMENTED PARTICIPANT PATTERN\]5.  
**C. Strong Analytical Inference** 5\. **Machine Learning Fundamentals:** The bar-raiser interviews explicitly probe classic machine learning mathematics (e.g., Entropy calculations, L1/L2 regularization theory) \[DOCUMENTED PARTICIPANT PATTERN\]17. This indicates that Amazon highly values foundational statistical comprehension over the mere orchestration of high-level APIs \[INFERENCE\]. 6\. **Experimentation Rigor:** The absolute necessity of establishing strong local cross-validation to survive the private leaderboard shakeup serves as an indirect test of a candidate's scientific methodology and resistance to overfitting \[INFERENCE\].  
**D. Weak Evidence** 7\. **Subjective Business Understanding:** While problem statements reference e-commerce business value, the actual evaluation mechanisms are purely mathematical (leaderboard score) and technical (code review and architectural defense). This minimizes the necessity for subjective, qualitative business analysis in favor of hard engineering execution \[INFERENCE\].

## **10\. Core Principles for a High-Performing Project**

Based on the forensic extraction of historical evidence, successful submissions consistently adhere to several non-negotiable design principles.  
**Baseline-First Experimentation:** Top teams explicitly reserve the first 24 hours for the establishment of a naive baseline and the construction of holdout validation mechanisms. The historical evidence demonstrates that refining a proven approach yields higher returns than constantly swapping architectures \[DOCUMENTED PARTICIPANT PATTERN\]12.  
**Data-First Modeling (The 80/20 Rule):** Extensive Exploratory Data Analysis (EDA) yields exponentially higher returns than indiscriminate model scaling. Team NeelDevenShah explicitly noted that the "biggest gains came from deeply understanding the data before training" rather than relying on brute-force parameter increases \[DOCUMENTED PARTICIPANT PATTERN\]16.  
**Metric-Aligned Training:** The loss function must mathematically align with the final evaluation metric. Team SPAM\_LLMs successfully implemented a Custom Log-based MSE to approximate the mathematical constraints of SMAPE, resulting in superior boundary predictions \[DOCUMENTED PARTICIPANT PATTERN\]15.  
**Exact Submission Compliance:** Output formatting must be flawless. Historical examples from 2024 show that teams utilizing raw OCR often failed entirely because their unparsed outputs (e.g., "2 gms") did not exactly match the strict constraints (e.g., "2 gram") enforced by the scoring sanity checker \[DOCUMENTED PARTICIPANT PATTERN\]7.  
**Modularity and Model Diversity:** High-performing pipelines ensemble distinct architectural paradigms to mitigate inherent weaknesses. The combination of tree-based models (such as XGBoost) for structured tabular data with Transformer-based models (such as CLIP) for unstructured image data provides robust generalization against private leaderboard shakeups \[DOCUMENTED PARTICIPANT PATTERN\]16.

## **11\. Failure Modes**

Participant post-mortems provide a crucial forensic window into the recurring traps that eliminate the vast majority of the 75,000+ applicants. The primary failure mode involves attempting to train massive models without adequate compute profiling. For instance, Team SMV attempted to fine-tune LLaVA on 40GB of data using Kaggle's restrictive 30GB VRAM limits, resulting in catastrophic memory leaks, out-of-memory errors, and ultimately, late submissions \[DOCUMENTED PARTICIPANT PATTERN\]26. Prevention requires aggressive early utilization of QLoRA and 4-bit quantization.  
A secondary failure mode involves non-compliance with data restrictions. Teams attempting to circumvent constraints by utilizing proprietary APIs like OpenAI, or by scraping external pricing data, had their solutions instantly discarded and faced disqualification \[OFFICIAL\]3. Prevention dictates strict adherence to local inference and open-weight architectures.  
Finally, poor parsing and weak post-processing pipelines consistently destroy viable models. In 2024, teams successfully extracting text via OCR failed to register a competitive score because they lacked the requisite Regex pipelines to format the output as the sanity checker demanded \[DOCUMENTED PARTICIPANT PATTERN\]7. Prevention requires building rigorous Python post-processing validation layers prior to CSV export. Furthermore, teams that bypass statistical EDA to blindly throw architectures like BERT or ResNet at a problem routinely miss crucial feature correlations, resulting in underperforming embeddings \[DOCUMENTED PARTICIPANT PATTERN\]16.

## **12\. Candidate Skill Matrix**

A competitive candidate profile necessitates mastery across diverse domains of data science, deep learning, and systems engineering. The following matrix delineates the required depth of capability based on historical competition demands.

| Skill / Capability | Required Depth | How Candidate Can Demonstrate It |
| :---- | :---- | :---- |
| **Python / Pandas / NumPy** | Mastery | Developing vectorized data cleaning scripts, efficient chunking of 2M+ row DataFrames, and strict memory management. |
| **Scikit-learn / XGBoost** | Mastery | Architecting robust tree-based ensembles, executing rigorous hyperparameter tuning, and establishing local cross-validation. |
| **Deep Learning (PyTorch)** | High | Programming custom loss functions, building custom datasets and dataloaders, and managing tensor allocation on constrained GPUs. |
| **Transformers / Embeddings** | High | Extracting and manipulating frozen embeddings from models like SigLIP/CLIP; conceptually tracing token pathways. |
| **Fine-Tuning (LoRA/QLoRA)** | High | Implementing Parameter-Efficient Fine-Tuning, defending the math of rank matrices, and managing 4-bit/8-bit quantization. |
| **VLMs / Multimodal Learning** | High | Aligning unstructured text and image modalities via mathematically sound early or late fusion mechanisms. |
| **Statistics & Classical ML** | Medium-High | Verbally defending the mathematics of Gini Index, Entropy, and Regularization (a strict Bar-Raiser requirement). |
| **Feature Engineering / Regex** | Mastery | Developing strict parsers for noisy OCR outputs, unit standardization mapping, and executing target encoding. |
| **Git / Reproducibility** | Medium | Architecting a clean, documented repository featuring highly reproducible pipeline scripts and modular EDA notebooks. |

## **13\. Amazon ML Challenge Preparation Framework**

For candidates engineering their preparation strategy, the historical evidence dictates a highly specific, tiered analytical framework to maximize alignment with Amazon's evaluation criteria \[INFERENCE\].

| Priority Tier | Conceptual and Technical Focus Areas |
| :---- | :---- |
| **A. Must Know** | Mathematical foundations of evaluation metrics (F1, MAPE, SMAPE, RMSE). Fundamentals of structured tabular ML (XGBoost, LightGBM). Core mechanics of Deep Learning (Loss Functions, Gradient Descent). |
| **B. Should Know** | Deployment and fine-tuning protocols for open-source Vision-Language Models (Qwen-VL, SigLIP). Low-Rank Adaptation (LoRA) mechanisms for compute constraints. Cross-modal late fusion strategies. |
| **C. Nice to Know** | Flash Attention and Sparse Attention optimization for inference speed. Advanced scaling laws and Distributed Data Parallel (DDP) training pipelines. |
| **D. Must Practice** | Rapid data preprocessing on massive, noisy Kaggle-style datasets under strict temporal constraints. Writing flawless Regex parsers for string normalization. Validating models locally to prevent catastrophic leaderboard overfitting. |
| **E. Must Explain (Without Notes)** | The mathematical derivatives of the implemented loss function. The explicit reasoning for selecting a specific architecture over an alternative. The theoretical time and space computational complexity of the applied algorithms. |

## **14\. Project Readiness Framework**

*(Note: This is an analytical preparation framework designed to simulate Amazon's rigorous requirements; it is NOT Amazon's officially published rubric).*  
To objectively self-evaluate whether an ML pipeline is "Amazon-Ready," candidates should rigorously assess their architecture against the following engineering dimensions.

| Evaluation Dimension | Characteristics of a Weak Implementation | Characteristics of a Strong Implementation |
| :---- | :---- | :---- |
| **Problem Formulation** | Defaults to standard MSE loss regardless of the actual metric constraints. | Actively implements a custom, mathematically mapped loss function (e.g., log-based for SMAPE). |
| **Data Quality** | Indiscriminately drops missing values and passes raw, noisy strings directly to a tokenizer. | Executes systematic unit normalization, standardizes noisy HTML text, and extracts metadata into structured columns. |
| **Model Selection** | Relies entirely on black-box, proprietary LLM API calls with zero architectural understanding. | Integrates task-specific frozen encoders fused with boosted trees; deeply understands internal tensor flow. |
| **Efficiency & Robustness** | Pipeline triggers catastrophic Out-of-Memory (OOM) errors; validation inference requires 20+ hours. | Deploys batched inference, 4-bit quantization, and memory chunking to run seamlessly on accessible, low-tier GPUs. |
| **Documentation** | Submits a single, unstructured Jupyter notebook containing hardcoded local file paths and minimal commentary. | Submits a modular GitHub repository with a strict requirements.txt, clean EDA separation, and a professional 1-page methodology PDF. |

## **15\. 2021–2025 Evolution**

The Amazon ML Challenge has evolved drastically, serving as a microcosm for the broader paradigm shifts occurring within the artificial intelligence industry. Between 2021 and 2023, the challenges were heavily anchored in structured metadata, natural language processing, and classical scaling issues. The 2021 dataset classifying 2.9 million products into browse nodes \[OFFICIAL\]5, and the 2023 dataset predicting physical product length \[OFFICIAL\]10, fundamentally tested a candidate's ability to handle massive tabular and textual data efficiently utilizing TF-IDF, BERT embeddings, and highly robust feature engineering.  
Beginning in 2024, the competition underwent a stark pivot toward multimodal and Generative AI contexts. The 2024 visual entity extraction task \[OFFICIAL\]7 demanded high competence in Optical Character Recognition and early Vision-Language Models. By 2025, the pricing challenge mandated sophisticated multimodal regression, requiring the seamless mathematical fusion of text and image inputs \[OFFICIAL\]14. Furthermore, rule compliance became exceedingly strict. As commercial APIs democratized AI, Amazon enforced rigid technical constraints: external LLM APIs were banned in 2024 \[OFFICIAL\]3, and an absolute 8-Billion parameter cap coupled with an open-source license mandate was established in 2025 \[OFFICIAL\]14.  
This evolutionary trajectory demonstrates that capabilities in pipeline architecture, multi-modal alignment, and hardware-constrained quantization are becoming vastly more critical \[INFERENCE\]. Conversely, the necessity for data cleaning, rigorous cross-validation, and a deep understanding of classical ML mathematical fundamentals remains resolutely invariant \[INFERENCE\].

## **16\. 2026 Evolution**

The parameters of the 2026 challenge—focusing on Business Entity Resolution evaluated via the F0.5 metric \[OFFICIAL\] \[cite: user prompt\]—signal yet another profound structural evolution.  
Entity Resolution introduces fundamental scaling complexities. It requires advanced blocking, candidate generation, string similarity computation, and semantic embeddings. Unlike the straightforward regression task of 2025 or the visual extraction of 2024, Entity Resolution operates as an ![][image5] computational problem if approached naively. Consequently, candidates must demonstrate exceptional systems engineering competence in clustering and highly optimized indexing algorithms \[INFERENCE\]. Furthermore, the deployment of the F0.5 metric—which mathematically weights precision twice as heavily as recall—dictates that false merges (erroneously predicting two distinct business entities are the same) will be severely penalized \[INFERENCE\].  
*Does the 2026 competition suggest a broader shift from pure prediction toward complete ML pipeline design?* Yes. \[INFERENCE\] The mathematical reality of Entity Resolution inherently necessitates a complex, multi-stage data pipeline (blocking ![][image6] pairwise feature extraction ![][image6] probabilistic matching ![][image6] graph clustering). It fundamentally cannot be resolved by simply pushing raw data through a single, monolithic VLM forward pass. This enforces a strict systems-engineering approach to machine learning, elevating the competition from a pure modeling exercise to a full-stack data architecture challenge.

## **17\. Evidence Gaps and Uncertainty**

While this forensic analysis synthesizes substantial empirical evidence, specific epistemological gaps remain within the historical record. The exact problem statement, dataset dimensions, and evaluation metric for the 2022 edition remain undocumented beyond confirmation of the competition's occurrence on the HackerEarth platform \[OFFICIAL\]2. Additionally, the precise mathematical weighting and algorithmic split utilized to calculate the private leaderboard standings remain proprietary to Amazon and Unstop. Finally, as previously noted, there is no publicly verifiable, numeric scorecard accessible regarding the exact grading parameters utilized by Amazon Scientists during the Grand Finale presentations.

## **The Amazon ML Challenge Candidate Profile**

The Amazon ML Challenge is meticulously engineered to identify and filter for a highly specific professional archetype: **The Resourceful, Mathematically Grounded Applied Scientist.**  
The empirical evidence definitively demonstrates that Amazon is not evaluating a candidate's ability to merely chain commercial APIs or prompt a massive frontier model. The implementation of strict model size caps, the outright banning of proprietary APIs, and the selection of highly sensitive, complex mathematical metrics serve as an intentional filtration system. Amazon seeks candidates who possess the engineering discipline to ingest noisy, massive, real-world e-commerce datasets; to normalize that data through exceptionally rigorous feature engineering; to deploy open-source models optimized for strict hardware constraints utilizing advanced quantization techniques; and crucially, to verbally defend the underlying calculus, statistical theory, and architectural trade-offs in a live, high-pressure environment against senior industry scientists. Absolute alignment with this profile—demonstrating profound respect for data fidelity, extreme validation rigor, and deep technical accountability—constitutes the definitive blueprint for success within the Amazon ML Challenge ecosystem.

#### **Works cited**

> 1. Discussions on Amazon ML Challenge \- HackerEarth, [https://www.hackerearth.com/challenges/competitive/amazon-ml-challenge/discussion/](https://www.hackerearth.com/challenges/competitive/amazon-ml-challenge/discussion/)  
> 2. Leaderboard \- Amazon ML Challenge \- HackerEarth, [https://www.hackerearth.com/challenges/competitive/amazon-ml-challenge-2022/leaderboard/](https://www.hackerearth.com/challenges/competitive/amazon-ml-challenge-2022/leaderboard/)  
> 3. Amazon ML Challenge 2024 Guidelines | PDF \- Scribd, [https://www.scribd.com/document/863057657/Amazon-ML-Challenge-2024-1](https://www.scribd.com/document/863057657/Amazon-ML-Challenge-2024-1)  
> 4. Amazon ML Challenge 2025 \- Unstop, [https://unstop.com/hackathons/crp-amazon-ml-challenge-2025-amazon-1560375](https://unstop.com/hackathons/crp-amazon-ml-challenge-2025-amazon-1560375)  
> 5. Amazon ML Challenge 2021 \- Kaggle, [https://www.kaggle.com/datasets/adityab19/amazon-ml-challenge](https://www.kaggle.com/datasets/adityab19/amazon-ml-challenge)  
> 6. GitHub \- akshatprogrammer/Amazon-ML-Challenge, [https://github.com/akshatprogrammer/Amazon-ML-Challenge](https://github.com/akshatprogrammer/Amazon-ML-Challenge)  
> 7. Amazon ML Challenge 2024: Ranked 357 of 74850 \- Medium, [https://medium.com/@aman\_prakash/how-we-secured-357th-spot-among-74-850-in-amazon-ml-challenge-2024-aef31f4e31b0](https://medium.com/@aman_prakash/how-we-secured-357th-spot-among-74-850-in-amazon-ml-challenge-2024-aef31f4e31b0)  
> 8. Amazon Business Research Analyst Hiring Challenge: Round 1, [https://www.hackerearth.com/challenges/hiring/amazon-ml-engineer-hiring-challenge-may21-round-1/](https://www.hackerearth.com/challenges/hiring/amazon-ml-engineer-hiring-challenge-may21-round-1/)  
> 9. Amazon ML challenge | Kaggle, [https://www.kaggle.com/general/252820](https://www.kaggle.com/general/252820)  
> 10. GitHub \- Marinto-Richee/Amazon-ML-Challenge-2023, [https://github.com/Marinto-Richee/Amazon-ML-Challenge-2023](https://github.com/Marinto-Richee/Amazon-ML-Challenge-2023)  
> 11. Amazon ML Challenge 2026: Your Complete Prep Guide with Live, [https://builder.aws.com/content/3HiM6zDmFrF98fRzOUETnGFDoqz/amazon-ml-challenge-2026-your-complete-prep-guide-with-live-demo](https://builder.aws.com/content/3HiM6zDmFrF98fRzOUETnGFDoqz/amazon-ml-challenge-2026-your-complete-prep-guide-with-live-demo)  
> 12. Amazon ML Challange is back for 2025\! I won it 2 times, here is how, [https://www.reddit.com/r/Btechtards/comments/1ntmvrr/amazon\_ml\_challange\_is\_back\_for\_2025\_i\_won\_it\_2/](https://www.reddit.com/r/Btechtards/comments/1ntmvrr/amazon_ml_challange_is_back_for_2025_i_won_it_2/)  
> 13. Amazon ML Challenge Finale Solutions \- Kaggle, [https://www.kaggle.com/discussions/general/262376](https://www.kaggle.com/discussions/general/262376)  
> 14. Amazon ML Challenge 2025 \- Kaggle, [https://www.kaggle.com/datasets/raghavdharwal/amazon-ml-challenge-2025](https://www.kaggle.com/datasets/raghavdharwal/amazon-ml-challenge-2025)  
> 15. Official Solution for Amazon ML Challenge 2025 by team ... \- GitHub, [https://github.com/RudrakshSJoshi/amlc-multimodal-mlp](https://github.com/RudrakshSJoshi/amlc-multimodal-mlp)  
> 16. Amazon ML Challenge 2025 \- Price Prediction \- GitHub, [https://github.com/NeelDevenShah/Amazon-ML-Challenge-2025](https://github.com/NeelDevenShah/Amazon-ML-Challenge-2025)  
> 17. Amazon Applied Scientist Intern Interview Experience (ML ... \- Medium, [https://medium.com/nybles/amazon-applied-scientist-intern-interview-experience-ml-challenge-2025-5092441d0b2e](https://medium.com/nybles/amazon-applied-scientist-intern-interview-experience-ml-challenge-2025-5092441d0b2e)  
> 18. GitHub \- KhadgaA/Amazon-ML-Challenge, [https://github.com/KhadgaA/Amazon-ML-Challenge](https://github.com/KhadgaA/Amazon-ML-Challenge)  
> 19. Machine Learning Challenge \#1 \- HackerEarth, [https://www.hackerearth.com/challenges/competitive/machine-learning-challenge-one/](https://www.hackerearth.com/challenges/competitive/machine-learning-challenge-one/)  
> 20. Amazon ML Challenge 2026 ₹2.25 Lakh \+ Amazon PPI \- YouTube, [https://www.youtube.com/watch?v=Fc4P-lUSbDM](https://www.youtube.com/watch?v=Fc4P-lUSbDM)  
> 21. Amazon ML Challenge 2024 Dataset \- Kaggle, [https://www.kaggle.com/datasets/suvroo/amazon-ml-challenge](https://www.kaggle.com/datasets/suvroo/amazon-ml-challenge)  
> 22. amazon-ml-challenge-2025 · GitHub Topics, [https://github.com/topics/amazon-ml-challenge-2025](https://github.com/topics/amazon-ml-challenge-2025)  
> 23. AMAZON ML CHALLENGE : r/learnmachinelearning \- Reddit, [https://www.reddit.com/r/learnmachinelearning/comments/1ffddqt/amazon\_ml\_challenge/](https://www.reddit.com/r/learnmachinelearning/comments/1ffddqt/amazon_ml_challenge/)  
> 24. Solutions Of Amazon ML Challenge : r/learnmachinelearning \- Reddit, [https://www.reddit.com/r/learnmachinelearning/comments/1fhzz7a/solutions\_of\_amazon\_ml\_challenge/](https://www.reddit.com/r/learnmachinelearning/comments/1fhzz7a/solutions_of_amazon_ml_challenge/)  
> 25. Amazon ML Challenge, 2025\. Problem statement \- Medium, [https://medium.com/@sherlock75664/amazon-ml-challenge-2025-2964600825c3](https://medium.com/@sherlock75664/amazon-ml-challenge-2025-2964600825c3)  
> 26. From Heroes to Zeroes — My Amazon ML Challenge 2024, [https://medium.com/@the.smv/from-heroes-to-zeroes-my-amazon-ml-challenge-2024-experience-c31e29dd7245](https://medium.com/@the.smv/from-heroes-to-zeroes-my-amazon-ml-challenge-2024-experience-c31e29dd7245)

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAF0AAAAdCAYAAADIKWCvAAAEPElEQVR4Xu2ZTcgVVRjHn6gk8yPU6APFFyWFCrEyRSWF1BAXCVaQIJGkoIuKCEotNUvFBBeS0iIVSVAxcCGikUUIioYrA2khLVJw0UJctQlM/z+emXfunfeeufNxv8z7hx/3vTPnnTvzn+c855znmPUV0gPiI7FdPJw61xY9KJaIF9In7iOtFm+JOeJzc0/aps/ESXFNvJ4611cbNVKctXym0w3Hiacr8Ihli/ON2vDbi8VpS3rlBPGeeChuVFDDzQNvn3gsOrZQzB9sERZpaET6YF4VMZ22Z8Qdcd38Zr/L4IC4LP6N/gf2mhsYEvfR6F6eNU8BmLQlOrZG7I8blBDXmy1+NE8tvGx6Pum2mWaItemDeVXEdPSiuBUxK3UuJHLka+JP8ZcYX3e2XiHTnxATzSP9FfMXd1isEMPEHjElasszfWFDgyDmQ/PeQXtM/1mMMe85v4nJNvSaaXXUdPS2+E9cMTcjr8aKX8Ty9IkahUxHPGhs0OPinJhe16K41pnPWtAi86jPkzY6bjr5jIghXfBZZJr1vPjWwnk4y3SOE91E+Uzxq3n08/C7rNys43vxRvQ3qYsXMNqaX7PjpiMinEgn4on8vMIwIjX0MFmmD4hT5lO8i+b5nGsRoZ/WtCuiN8UR85Rz0zyf57lmadP5gUPiH/OH+MQazxxCIqfH+Z1c3wqFTI+j+0nzGdQPYml0jhTxqhgVfc8r0ggDKCbTA0lX8XjT7JqlTa8qjCAaSDPk6njaVUUh06eJP8xzONHJIEdaI0h2mI8T9Noi+sB8YOYlcj2ui/Jcs2umIx6cqMP4DZY9HcyjkOn8zrtim1hm4fRURE+J9WKreC51rpm6ajoi114Vty3p8mUVMr3XVNj0eKESoozompjO4qdKFIZMT99jp0mrsOntEIMqaaZqXg+Z3mvquukD4kT0WVV903OIyCbC85YEmqlvehMxo9hpvpDIqyqLo15SV0zH8N2WLKHz6hnz0kFoEfa/Np0HIy2wEmNZTaFnpeWbZ9OG1SvkaR+L+jVLd0qyIbXCdAprLHa+Mg8O7pGFDuXhVqmw6Sx1V5kXeH4yv0k2GM5Gn83E9JCHKlLoYvFxyby+kfXwVU3HYMx4SVwwH9xbVZGsVWHTMZnq3ElLFjNc5Lz5DWaJAfN3S/YVs/hSHBN/WzLfpWAVSi2oqulxnZznoifzPa5IMpbME5sHW5dXYdMR0c7bp2CP3hffJKcbapQ4br5rVJZ3LFtzI6qIaD9ovsGBqu4wNdJUK7H6ZveFYg8FHeBvooASZ7No73XxPPRiIpwXQA2eF0AvZRDneFf0sSV7jdzkUbHJfPP3Xlc80DO72iJumJee2Y5jY2LSYMsOiz3A2oGQefOjNd/vZdFTybks3BZY0qMni6/Nze+rxWI7kMLbOKtfLbOIY8b2cvS9rxaKQY4ZykbrR/X9p7tyxuneB6eRKQAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADsAAAAaCAYAAAAJ1SQgAAADbklEQVR4Xu2XS6hNURjHP6HIK++8IwPyTkTJQBIDBhgoDMXAyDMyOCWJgYQi1M0AiRhIFym33AyYKVFIJELIUAr/311rsfc6e++77+Oca3B+9e/cvda+e6/vW+v7r7XNGvxX9JbWSWel/dLgdHfPMlDqFzd2ga3SEnNBH5BapeGJ/iFS38R1p+GhK6T10nRzLyxirtRkbgDdAYlrkc776ynSe2lVuEEslC5aJ9/ZS1oqPZKapY1ed6UX0oJ/t6YYL92XZsQdYoT0QPrt9U2ambrDbI/vC3onzfKa5O8h4QS73F8HNklnrIMzzM1HpNdWHRR91A0DnRf1kaDjUiVqj1kjfTcXTCXd1QYJeyhNizs8e80lnRlP0l+6Ka2N2nMhmNPSV3NLIwsy+0U6ZS7AALP03P8WUTFXg8zaM2l0qtdsjnRO6hO1A2O6JA2LOzwbzCWq1HLeJv3yv3kMlR5LT80tzQAZv2XFxjTAXO0xeySL2WWASSiXHVEb4AWHzT2DYEelu9ugnl+aM7NCppqrhaxsJwnBvpHG+DYCJFC2hSIYDLPG/YulH9Jtc0swQAnFg6Vej0oTzb1zs1WXGJCIe9b+ONqWF5k+FLXHMOAPlg6WX65Xh5tywEF3+78JkEAJmMCBRF6xdLJJzA2rNi5WRxYXzDlzssRSBHtnCccuF0M/9+Gsg3zbfOmjVc9ITMXSz2cJM/hQ//gBnpFVr2WhnFqs2sD+EmYG4+GFRZywaicl2Lf+N49Qr+MSbcwgZcNMTbb8eu0IBEuZsUoyCcEml2YWE8zts58tvZeWCTZZr0kq5pK33bLrtaMQ7Csr8B1cFXctCpZlts/cwHZGfWWCZX/l/2OCMVIGdyzt8J2h3WVMjVyWflp+ZtnjOExwqIhPKVlHuJiKZfsBSQzb0DXrWr0CBosjUza5cCIimCarDmaZ9Ek6ZultIhBWBoeFLEaam7XZcYcnbEN5/18WEocT4yvtwt7FpsyZOJyHm6Un5gLOs3PaSVL8EjZ+npXcNk5a9ccECbxu+auqLJgS76NkSsFAcGS+ctg3x1p+kEnYRnhRrgvWAVYI7o6z1xQ+BVullXFHnWBCDnqVmZwuw/K5atl1XWtwdYyJo2VdIKMcB1FdsuvBUPGM0p933QUv3iUtijtqyBbrufJp0KBBDfkDy6+jpxoHidQAAAAASUVORK5CYII=>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAYCAYAAAAVibZIAAAAdklEQVR4XmNgGAWjYMABBxCnATEPugQlgBGIW4HYGF2CUgAysBeIWdAlKAEg1xYAcRyUjRUIALEkiVgOiOcD8WQg5mOgEjAB4tVALIMuQS4QBuLFQCyPLkEJyALiCHRBSgAonU4FYml0CUoAKLZ5ofQoGAX0AAA5bAi7Yfn2hgAAAABJRU5ErkJggg==>