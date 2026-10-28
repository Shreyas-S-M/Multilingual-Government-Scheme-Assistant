# Requirements Traceability Matrix

This matrix maps every foundational requirement from the **Master Build Prompt** directly to the implementation file and automated test cases.

| Req ID | Requirement Description | Implementation File | Verification Test File | Test Status |
| :---: | :--- | :--- | :--- | :---: |
| **REQ-01** | English and Kannada Natural Language Understanding | `backend/nlp/language_detector.py`, `backend/nlp/text_normalizer.py` | `tests/unit/test_nlp.py` | **PASSED** |
| **REQ-02** | Kannada-English Code-Mixed Query Handling | `backend/nlp/language_detector.py`, `backend/nlp/text_normalizer.py` | `tests/unit/test_nlp.py`, Scenario 03 | **PASSED** |
| **REQ-03** | Indian Currency (Lakh, Crore) & Numeral Normalization | `backend/nlp/text_normalizer.py` | `tests/unit/test_nlp.py` | **PASSED** |
| **REQ-04** | Intent Classification (10 intents + fallback) | `backend/nlp/intent_classifier.py` | `tests/unit/test_nlp.py`, Scenarios 13, 14 | **PASSED** |
| **REQ-05** | NER & Profile Extraction with Confidence & Provenance | `backend/nlp/entity_extractor.py`, `backend/schemas/user_profile.py` | `tests/unit/test_nlp.py`, Scenarios 01, 02 | **PASSED** |
| **REQ-06** | Conversational Profile Memory & Conflict Resolution | `backend/schemas/user_profile.py`, `backend/services/chat_service.py` | `tests/unit/test_nlp.py`, Scenario 07, 15 | **PASSED** |
| **REQ-07** | Multilingual Embeddings & FAISS Vector Store | `backend/retrieval/embeddings.py`, `backend/retrieval/vector_store.py` | `scripts/build_index.py`, Scenario 20 | **PASSED** |
| **REQ-08** | Hybrid Retrieval (FAISS + BM25 Ensemble) | `backend/retrieval/bm25_search.py`, `backend/retrieval/hybrid_search.py` | `tests/api/test_api_routes.py`, `scripts/build_index.py` | **PASSED** |
| **REQ-09** | Three-State Eligibility Semantics (PASS, FAIL, UNKNOWN) | `backend/eligibility/predicates.py`, `backend/eligibility/engine.py` | `tests/unit/test_eligibility_engine.py` | **PASSED** |
| **REQ-10** | Mandatory Failure Dominance (Similarity never overrides FAIL) | `backend/eligibility/engine.py`, `backend/retrieval/hybrid_search.py` | `tests/unit/test_eligibility_engine.py`, Scenario 09, 10 | **PASSED** |
| **REQ-11** | Zero UNKNOWN-to-FAIL Leaks (Missing data triggers question) | `backend/eligibility/predicates.py`, `backend/eligibility/engine.py` | `tests/unit/test_eligibility_engine.py`, Scenario 04, 05, 06 | **PASSED** |
| **REQ-12** | Adaptive Clarification Question Selection | `backend/eligibility/adaptive_questioner.py` | `tests/unit/test_adaptive_questions.py`, Scenario 04 | **PASSED** |
| **REQ-13** | Near-Miss Alternative Scheme Recommendations | `backend/eligibility/near_miss.py` | `tests/unit/test_adaptive_questions.py`, Scenario 16 | **PASSED** |
| **REQ-14** | Grounded RAG with Deterministic Fallback Mode | `backend/rag/context_builder.py`, `backend/rag/generator.py` | Scenario 19, `tests/api/test_api_routes.py` | **PASSED** |
| **REQ-15** | Official Source URLs, Citations, & Verification Dates | `data/seed/verified_schemes.json`, `backend/models/database.py` | Scenario 18, `tests/api/test_api_routes.py` | **PASSED** |
| **REQ-16** | Relational Database Schema & Idempotent Seeding | `backend/models/database.py`, `backend/repositories/scheme_repo.py` | `tests/api/test_api_routes.py`, `scripts/seed_data.py` | **PASSED** |
| **REQ-17** | FastAPI REST Endpoints & Pydantic Validation | `backend/main.py`, `backend/api/routes/*.py` | `tests/api/test_api_routes.py` | **PASSED** |
| **REQ-18** | Role-Protected Administrative API & Index Rebuilding | `backend/api/routes/admin.py`, `backend/core/security.py` | `tests/api/test_admin_api.py` | **PASSED** |
| **REQ-19** | Complete Streamlit Multi-Page Web Interface | `frontend/app.py`, `frontend/pages/*.py`, `frontend/components/*.py` | Manual UI verification | **READY** |
| **REQ-20** | 20 End-to-End Automated Test Scenarios | `tests/evaluation/test_evaluation_suite.py` | `pytest tests/evaluation/` | **PASSED (20/20)** |
