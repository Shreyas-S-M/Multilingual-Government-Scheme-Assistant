# Academic Project Feature Checklist

**Institution:** School of Computer Science and Engineering, RV University, Bengaluru  
**Project Title:** Multilingual Government Scheme Assistant  
**Team Members:** Shreyas Kamath D (1RUA24CSE0444), Shreyas S M (1RUA24CSE0446), Shreyash Annegowda (1RUA24CSE0447), Skanda C H (1RUA24CSE0463)  
**Faculty Guide:** Dr. Roopesh  
**Literature Survey Reference:** [`docs/literature_survey.md`](./literature_survey.md) (16 Research Papers Analyzed)

---

## 1. Academic Innovation Points

- [x] **Three-State Eligibility Reasoning Engine (`PASS`, `FAIL`, `UNKNOWN`):**
  - Fully implemented in `backend/eligibility/predicates.py` and `backend/eligibility/engine.py`.
  - Missing information explicitly yields `UNKNOWN` with documented missing attributes.
  - Mandatory failures dominate; `UNKNOWN` is never treated as `FAIL`.
  - Tested in `tests/unit/test_eligibility_engine.py` (all tests passing).

- [x] **Adaptive Clarification Questioning:**
  - Implemented in `backend/eligibility/adaptive_questioner.py`.
  - When candidate schemes contain `UNKNOWN` mandatory attributes, the engine computes attribute frequency across candidate schemes and selects the single most impactful question.
  - Generates clear, targeted questions in English and Kannada.
  - Tested in `tests/unit/test_adaptive_questions.py` and Scenarios 04, 15.

- [x] **Near-Miss Scheme Recommendations:**
  - Implemented in `backend/eligibility/near_miss.py`.
  - When an applicant fails mandatory conditions for a scheme, viable alternative programs in the same sector with zero confirmed failures are discovered and explained.
  - Tested in `tests/unit/test_adaptive_questions.py` and Scenario 16.

- [x] **Multilingual Eligibility Understanding (English + Kannada + Code-Mixed):**
  - Implemented in `backend/nlp/language_detector.py`, `backend/nlp/text_normalizer.py`, and `backend/nlp/entity_extractor.py`.
  - Preserves Kannada Unicode block `\u0C80-\u0CFF`.
  - Handles Kannada numerals (೦-೯) and Indian numbering expressions (lakh, crore, thousand, ಸಾವಿರ).
  - Handles transliterated Kannada / Kanglish without crashing.
  - Tested in `tests/unit/test_nlp.py` and Scenarios 01, 02, 03.

- [x] **Evidence-Based Explanations Linking User Attributes to Official Requirements:**
  - Implemented in `backend/rag/context_builder.py` and `backend/rag/generator.py`.
  - Explicitly links applicant attributes to official scheme clauses, citing gazette notifications and official URLs.
  - Zero hallucination rate under deterministic fallback mode.

---

## 2. Technical Stack Audit

- [x] **Frontend:** Streamlit with custom CSS, responsive layout, multi-page routing (`frontend/app.py`, `frontend/pages/`).
- [x] **Backend:** Python 3.12, FastAPI REST API with Pydantic validation, Uvicorn server (`backend/main.py`).
- [x] **Database:** SQLAlchemy 2.0 ORM with normalized models (`backend/models/database.py`), SQLite zero-setup default with PostgreSQL compatibility.
- [x] **Vector Store:** FAISS dense vector index with persistent vector-to-scheme mappings (`backend/retrieval/vector_store.py`).
- [x] **Lexical Retrieval:** BM25Okapi keyword search over tokenized multilingual corpus (`backend/retrieval/bm25_search.py`).
- [x] **Hybrid Retrieval:** Ensemble score fusion combining FAISS and BM25 (`backend/retrieval/hybrid_search.py`).
- [x] **Testing:** Automated test suite with 53 pytest cases covering unit, integration, and 20 end-to-end evaluation scenarios (`tests/`).
- [x] **Containerization:** Production Dockerfile and docker-compose.yml configuration.

---

## 3. Knowledge Base Audit

- [x] **Verified Schemes:** 22 real, verified Central and Karnataka state government schemes (`data/seed/verified_schemes.json` and `data/schemes/*.json`).
- [x] **No Fabricated URLs:** Every scheme contains authentic official portal URLs (`pmkisan.gov.in`, `pmjay.gov.in`, `sevasindhu.karnataka.gov.in`, `scholarships.gov.in`, etc.).
- [x] **Machine-Checkable Rules:** Formally defined predicates with operators, expected values, and gazette citations.
- [x] **Audit Provenance:** All schemes record last verified date and source reliability tier.
