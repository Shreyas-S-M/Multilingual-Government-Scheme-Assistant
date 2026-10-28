# System Architecture & Data Flow

## 1. High-Level Architecture Overview

The **Multilingual Government Scheme Assistant** is engineered using a decoupled, service-oriented architecture:
- **Presentation Layer:** Streamlit Web UI with custom CSS, interactive chat bubbles, status badges, and administrative portals.
- **API & Orchestration Layer:** FastAPI REST services exposing versioned endpoints (`/api/v1`) for health checks, catalog search, eligibility evaluation, and conversation state management.
- **Multilingual NLP Engine:** Language identification (English / Kannada / Code-mixed), Unicode normalization, Indian currency/numerals parsing, intent classification, and entity extraction.
- **Retrieval Engine:** FAISS dense vector search combined with BM25 lexical search using reciprocal rank fusion.
- **Eligibility Engine:** Independent three-state reasoning engine enforcing PASS, FAIL, UNKNOWN semantics, adaptive question selection, and near-miss alternatives.
- **Persistence Layer:** Normalized SQLAlchemy ORM with SQLite (local development default) and PostgreSQL compatibility.

```
+---------------------------------------------------------------------------------------+
|                                    Streamlit Frontend                                 |
|   (Chat Assistant | Scheme Explorer | Eligibility Assessment | Admin & Evaluation UI) |
+-------------------------------------------+-------------------------------------------+
                                            | HTTP REST API
                                            v
+---------------------------------------------------------------------------------------+
|                                  FastAPI Backend (/api/v1)                            |
|   [health.py]   [schemes.py]   [chat.py]   [eligibility.py]   [admin.py]   [eval.py]  |
+---------------------+---------------------+---------------------+---------------------+
                      |                     |                     |
                      v                     v                     v
          +-----------------------+ +-------------------+ +---------------------+
          | Multilingual NLP Core | | Retrieval Engine  | | Eligibility Engine  |
          | - Lang Detection      | | - FAISS Vectors   | | - PASS/FAIL/UNKNOWN |
          | - Text Normalization  | | - BM25 Lexical    | | - Predicate Rules   |
          | - Entity Extraction   | | - Hybrid Ranker   | | - Adaptive Qs       |
          | - Profile State       | | - Metadata Map    | | - Near-Miss Alts    |
          +-----------------------+ +-------------------+ +---------------------+
                      |                     |                     |
                      +---------------------+---------------------+
                                            |
                                            v
                            +-------------------------------+
                            |   Relational Database (ORM)   |
                            | - Verified Schemes & Rules    |
                            | - Sources & Provenance        |
                            | - Conversations & Audits      |
                            +-------------------------------+
```

## 2. End-to-End Conversational Data Flow

1. **User Query Input:** A citizen enters a natural-language query in English, Kannada, or code-mixed text.
2. **Language Detection & Normalization:** `LanguageDetector` classifies the script and code-mixing; `TextNormalizer` standardizes Unicode NFC, Kannada numerals (೦-೯ -> 0-9), and Indian currency (lakh/crore/ಸಾವಿರ).
3. **Intent & Entity Extraction:** `IntentClassifier` identifies the conversational goal; `EntityExtractor` extracts demographic and socioeconomic parameters into a typed `UserProfile`.
4. **State Accumulation:** Current session profile is updated; any contradictory statements are flagged for user clarification.
5. **Hybrid Retrieval:** `HybridRetriever` runs parallel FAISS dense vector similarity and BM25 lexical token matching over 22 verified schemes.
6. **Three-State Eligibility Evaluation:** `EligibilityEngine` evaluates every mandatory and optional criterion of top candidates, returning `PASS`, `FAIL`, or `UNKNOWN`.
7. **Adaptive Questioning:** If candidate schemes contain `UNKNOWN` mandatory conditions, `AdaptiveQuestioner` selects the single most impactful missing attribute.
8. **Near-Miss Alternatives:** If the applicant fails a desired scheme, `NearMissRecommender` discovers viable alternatives in the same domain.
9. **Grounded RAG Response Synthesis:** `ResponseGenerator` formats an evidence-grounded response in the target language citing official government sources.
10. **Persistence & Return:** Message and profile are saved to the relational database and displayed in Streamlit.
