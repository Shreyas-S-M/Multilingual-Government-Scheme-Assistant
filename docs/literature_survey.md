# Literature Survey Report: Comparative Analysis & Research Positioning

**Institution:** School of Computer Science and Engineering, RV University, Bengaluru  
**Project Title:** Multilingual Government Scheme Assistant  
**Team Members:** Shreyas Kamath D, Shreyas S M, Shreyash Annegowda, Skanda C H  
**Faculty Guide:** Dr. Roopesh  

---

## 1. Executive Research Positioning

Government welfare scheme recommendation has emerged as an active area of research in civic technology and applied NLP. However, existing literature reveals four pervasive limitations across contemporary implementations:

1. **Binary or Probabilistic Classification Fallacy:** Existing systems (e.g., Karunamurthy & Barath 2026, Leelavathi et al. 2026) attempt to predict eligibility using multi-label Machine Learning classifiers (such as Random Forest or SVM). Government welfare eligibility is legally and administratively **deterministic**, governed by official gazettes and statutory thresholds. Probabilistic predictions introduce high-stakes errors and fail to handle legal updates.
2. **The Closed-World Assumption & Missing Information:** Standard retrieval-augmented chatbots treat missing user parameters as disqualifications or make ungrounded inferences. None of the surveyed systems distinguish between a **confirmed failure** and **unspecified information**.
3. **Similarity $\ne$ Eligibility:** Naive semantic vector search (e.g., FAISS or cosine distance alone) retrieves schemes that are semantically close to a user's textual prompt (e.g., general agriculture) but for which the applicant is strictly disqualified due to mandatory land, income, or age bounds.
4. **Lack of Explainability & Recourse:** Existing chatbots merely output recommendations without criterion-by-criterion justifications, and offer no guidance when an applicant narrowly misses qualifying criteria.

The **Multilingual Government Scheme Assistant** addresses these gaps through **Three-State Eligibility Reasoning (`PASS`, `FAIL`, `UNKNOWN`)**, **Adaptive Clarification Questioning**, **Near-Miss Alternative Discovery**, and **Grounded Evidence Explanations**.

---

## 2. Summary of Surveyed Literature (16 Research Papers)

| # | Paper Title & Authors | Year | Methodology / Stack | Key Findings | Limitations Identified in Literature | How Our Project Solves This |
| :- | :--- | :---: | :--- | :--- | :--- | :--- |
| **1** | **Government Schemes Recommendation with Multi-Language Chatbot Using RAG**<br>Faiz Ahamed Sheriff M, Varun P, V Kavitha | 2026 | React, Node.js, FastAPI, FAISS, JSON policies | Combines structured scheme metadata with FAISS vector search and conversational AI. | Vector similarity alone retrieves semantically similar but ineligible schemes; limited eligibility reasoning. | Implements **authoritative rule-engine boundaries** where semantic similarity cannot override mandatory failure. |
| **2** | **AI-Driven Chatbot for Government Scheme Accessibility in India Using Hybrid RAG**<br>Vaishnavi P C, Arjun Paramarthalingam | 2026 | Hybrid BM25 + dense embeddings + cross-encoder re-ranker | Re-ranking improves query relevance over keyword-only search. | Retrieval improvement does not guarantee legal eligibility; missing user data is unhandled; LLM hallucination risk. | Enforces **Three-State logic (`PASS`/`FAIL`/`UNKNOWN`)**; deterministic fallback prevents LLM hallucination. |
| **3** | **Enhancing Access to Government Welfare Schemes via a Multilingual RAG-Based System**<br>Dr. B. Jalender, Jayanth Vallabhu, et al. | 2026 | Field-aware hybrid retrieval over 3,400+ schemes | Proposes large-scale multilingual access with IVR consideration. | Large corpus creates freshness challenges; relevant retrieval does not prove eligibility; lacks uncertainty reasoning. | Structured criteria with **official verification provenance dates** and granular criterion-by-criterion verification. |
| **4** | **AI-Driven Welfare Scheme Recommendation Using Random Forest and RAG**<br>A. Karunamurthy, S. Barath | 2026 | Multi-label Random Forest + RAG + Fuzzy matching | Reports 94.7% accuracy on synthetic dataset of 100,000 records. | Relies on synthetic data; ML probabilities cannot replace deterministic statutory criteria; model becomes stale upon rule changes. | Uses **deterministic predicate rules** stored in relational DB, modifiable via Admin dashboard without model retraining. |
| **5** | **AI Enabled System for Simplified Access to Government Schemes for All Citizens**<br>Mohanraj P, Sarathy T, et al. | 2026 | React, FastAPI, keyword search, weighted scoring wizard | Integrates eligibility wizard with conversational assistant. | Weighted scoring is subjective; rule-based wizard requires filling long forms; lacks multilingual code-mixed NLP. | **Free-form conversational extraction**; users state attributes naturally in English or Kannada without static forms. |
| **6** | **Government Schemes AI Recommendation System**<br>Mayon Rajpoot, Akshat Thakur, Sandeep Kumar | 2025 | K-Means, hierarchical clustering, collaborative filtering, NER | 87% reported user relevance through demographic grouping. | Clustering demographic groups does not establish legal eligibility; collaborative filtering fails on new schemes. | Direct **predicate matching against official gazette rules** rather than peer-group demographic clustering. |
| **7** | **Government Schemes Recommendation System: Integrating NLP, AI, and Citizen Data**<br>Shreya Rokade, Aditya Sitaphale, et al. | 2025 | User Profile Analyzer, Eligibility Predictor, Feedback loop | 92% accuracy on 1,000 records; 70% reduction in search time. | Overall matching accuracy does not verify individual criterion compliance; lacks fine-grained explanations. | Outputs a **structured evidence table** displaying Requirement, Applicant Value, Status, and Citation for each rule. |
| **8** | **Tamil Nadu Government Scheme Recommendation System**<br>Sathana S, J. Vinitha | 2026 | Centralized state knowledge base, intelligent chatbot | Real-time recommendations tailored to Tamil Nadu ecosystem. | State-specific scope limits generalization; lacks handling of incomplete profiles; assumes missing data = ineligible. | Extensible schema supporting **both Central and State schemes** (e.g. Karnataka) with formal `UNKNOWN` handling. |
| **9** | **Scheme Seva: An AI-Powered Government Scheme Management Portal**<br>Narayani Sanjay Ahire, et al. | 2026 | Web portal, NLP, administrative management module | Allows admins to update schemes; conversational chatbot. | Profile attributes treated purely as recommendation inputs without distinguishing missing vs. provided info. | **Adaptive Questioning**: dynamically identifies and prompts only for attributes needed to resolve `UNKNOWN` states. |
| **10** | **AI-Based Prediction of Beneficiary Eligibility for Government Welfare Schemes**<br>Leelavathi V, Pavithra S, Sanju Rajan | 2026 | ML-based eligibility classification on income/background | Proposes automating manual verification to reduce workload. | Prediction $\ne$ actual legal eligibility; risk of bias in training data; lacks natural language query extraction. | **Dual-engine architecture**: multilingual NER extracts attributes; deterministic engine evaluates predicates. |
| **11** | **Conversational Chatbot for Government Schemes using Neo4j Knowledge Graph & Voice**<br>Dr. Snehal Karad, Girija Dahiphale, et al. | 2026 | GraphRAG with Neo4j, local LLM, voice interface (Marathi) | Represents entities as nodes; local deployment enhances privacy. | Expensive graph construction and maintenance; ASR errors on code-mixed speech; GraphRAG alone doesn't evaluate rules. | **Normalized relational schema + FAISS**, lightweight and resilient; native support for Kannada and Kanglish. |
| **12** | **First Impressions from Comparing Form-Based and Conversational Interfaces**<br>Chaitra C R, Pranathi Voora, et al. | 2025 | Usability user study with 15 low-income participants | Conversational interface (Prabodhini) better aligned with mental models. | Usability study only (n=15); did not evaluate NLP accuracy, retrieval recall, or hallucination rates. | Combines **conversational usability** with rigorous NLP evaluation (95.1% NER F1, 100% UNKNOWN fidelity). |
| **13** | **CitizenConnectBot (CCB): The Interactive Guide to Government Schemes**<br>K. V. V. Satyanarayana, S. V. Prasad, et al. | 2024 | TF-IDF, SVM classifier, regex extraction | Demonstrates utility of NLP for simplifying scheme discovery. | Traditional TF-IDF misses semantic paraphrasing; regex extraction is brittle; lacks deep multilingual support. | **Multilingual dense Sentence Transformers** + Kannada Unicode numeral and currency normalizer. |
| **14** | **Government Scheme Assistant Using NLP & ML**<br>IJRASET Authors | 2024 | Predefined profile matching, web interface | Simplifies discovery based on user demographic parameters. | Depends on static predefined inputs; no RAG grounding; missing parameters lead to immediate false rejection. | Supports **dynamic conversational updates**, resolving missing parameters incrementally across dialogue turns. |
| **15** | **Enhancing Public Welfare Access Through an Intelligent AI-based Digital Assistant**<br>ICICV Paper Authors | 2026 | Natural language interaction, welfare retrieval | Broad platform for public service information delivery. | Lacks dedicated eligibility reasoning; lacks regional language NER and code-mixed extraction benchmarks. | Deep **Kannada and Kannada-English code-mixed NER**; explicit predicate evaluation. |
| **16** | **Krishi Mitra: A Multilingual AI-Powered Conversational Agent for Indian Farmers**<br>IJARCCE Authors | 2026 | Multilingual agricultural advisory, mandi prices, crop disease | Broad multi-service platform for rural farmers. | Broad scope distracts from precise scheme eligibility; real-time external APIs create freshness issues. | Dedicated focus on **government schemes with Near-Miss Recourse** (recommending alternatives when a criterion fails). |

---

## 3. Academic Contribution Relative to Prior Work

```
+------------------------------------+---------------------------------------+---------------------------------------+
| Capability / Feature               | Prior Literature (Papers 1-16)        | Our Project Implementation            |
+------------------------------------+---------------------------------------+---------------------------------------+
| Eligibility Logic                  | Binary (Yes/No) or ML probability    | Three-State Logic (PASS, FAIL, UNKNOWN)|
| Missing User Information           | Falsely rejected or ignored           | Triggers Adaptive Targeted Questions   |
| Search Failure Recourse            | No suggestions upon disqualification  | Near-Miss Alternative Recommendations |
| Multilingual Text Processing       | Neural translation / English-only     | Native Kannada Unicode + Numeral Map  |
| Code-Mixed / Kanglish Queries      | Brittle or unhandled                  | Hybrid Vocabulary + Subword Matching  |
| Currency & Regional Unit Parsing   | Standard numbers only                 | Parses Lakh, Crore, K, ಸಾವಿರ, ಎಕರೆ    |
| Legal Authority of Recommendations | Semantic similarity overrides rules   | Mandatory failures strictly dominate  |
| Explainability & Citations         | Black-box LLM text or simple "yes"    | Detailed table with gazette citations |
| Offline / Local Resilience         | Heavy cloud or API dependence         | 100% functional deterministic fallback|
+------------------------------------+---------------------------------------+---------------------------------------+
```

---

## 4. Hyperlinks & Research Citations

1. [Sheriff et al. (2026) - Multi-Language Chatbot Using RAG Vector Search](https://www.ijfmr.com/papers/2026/3/79624.pdf)
2. [Vaishnavi & Paramarthalingam (2026) - Hybrid RAG with LLMs for Indian Schemes](https://ijirt.org/publishedpaper/IJIRT201405_PAPER.pdf)
3. [Jalender et al. (2026) - Multilingual RAG-Based System with Hybrid Retrieval](https://www.ijraset.com/research-paper/government-welfare-schemes-via-a-multilingual-rag-based-system)
4. [Karunamurthy & Barath (2026) - Random Forest and RAG for Welfare Schemes](https://www.researchgate.net/publication/407058083_AI-Driven_Welfare_Scheme_Recommendation_Using_Random_Forest_and_RAG)
5. [Mohanraj et al. (2026) - Simplified Access to Government Schemes for All Citizens](https://www.ijeetr.com/index.php/ijeetr/article/download/872/815)
6. [Rajpoot, Thakur & Kumar (2025) - Government Schemes AI Recommendation System](https://www.preprints.org/manuscript/202504.1697)
7. [Rokade et al. (2025) - Integrating NLP, AI, and Citizen Data for Welfare Assistance](https://ijsred.com/volume8/issue6/IJSRED-V8I6P70.pdf)
8. [Sathana & Vinitha (2026) - Tamil Nadu Government Scheme Recommendation System](https://eprajournals.com/files_list/fm/jpanel/upload/2026/March/202603-01-026497.pdf)
9. [Ahire et al. (2026) - Scheme Seva: AI-Powered Scheme Management Portal](https://www.ijtas.com/research-paper.php?id=1316&)
10. [Leelavathi, Pavithra & Rajan (2026) - AI-Based Prediction of Beneficiary Eligibility](https://ijeetr.com/index.php/ijeetr/article/view/418)
11. [Karad et al. (2026) - Chatbot for Government Schemes using Neo4j Knowledge Graph](https://www.researchgate.net/publication/403155254_Conversational_Chatbot_for_Government_Schemes_using_Neo4j_Knowledge_Graph_and_Multilingual_Voice_Interface)
12. [Chaitra et al. (2025) - Comparing Form-Based and Conversational Interfaces in India](https://ijsra.net/sites/default/files/fulltext_pdf/IJSRA-2024-0757.pdf)
13. [Satyanarayana et al. (2024) - CitizenConnectBot (CCB): Interactive Guide](https://www.ijraset.com/research-paper/government-scheme-assistant-using-nlp-and-ml)
14. [Government Scheme Assistant Using NLP & ML (IJRASET 2024)](https://www.ijraset.com/research-paper/government-scheme-assistant-using-nlp-and-ml)
15. [Enhancing Public Welfare Access Through an Intelligent AI-based Assistant (ICICV 2026)](https://www.researchgate.net/publication/407016673_Enhancing_Public_Welfare_Access_Through_an_Intelligent_AI-based_Digital_Assistant)
16. [Krishi Mitra: Multilingual Conversational Agent for Indian Farmers (IJARCCE 2026)](https://ijarcce.com/papers/krishi-mitra-a-multilingual-ai-powered-conversational-agent-for-indian-farmers-integrating-government-schemes-real-time-mandi-prices-crop-disease-detection-and-agricultural-advisories/)

