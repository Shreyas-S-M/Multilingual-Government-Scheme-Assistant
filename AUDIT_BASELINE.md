# AUDIT BASELINE REPORT
## Multilingual Government Scheme Assistant — Initial State & Architecture Ledger

**Project Name:** Multilingual Government Scheme Assistant (Sahayaka / ಸಹಾಯಕ)  
**Audit Date:** November 2, 2026  
**Auditor:** Principal QA Software Engineer & Core Systems Test Architect (Google Engineering Standard)  
**Document Classification:** Architectural Baseline & Initial Forensic Audit  
**Workspace Path:** `d:\Multilingual-Government-Scheme-Assistant-main\Multilingual-Government-Scheme-Assistant-main`  
**Standard Compliance:** IEEE 830-1998 / DPDP Act 2023 / W3C WAI-ARIA 2.2  

---

## 1. Executive Summary

This document establishes the formal engineering baseline for the **Multilingual Government Scheme Assistant** prior to and during the comprehensive remediation cycle. 

The application is an end-to-end bilingual (English and Kannada) AI-driven public service delivery platform designed to assist Indian citizens in discovering, understanding, and evaluating their eligibility for Central and Karnataka State government welfare schemes. 

While the project established an ambitious architectural foundation combining a FastAPI REST backend, dense FAISS + sparse BM25 hybrid retrieval, a deterministic 3-state eligibility engine (PASS, FAIL, UNKNOWN), and dual frontends (Next.js 14 web application and Streamlit administration portal), an exhaustive initial audit revealed critical runtime collisions, missing package dependencies, lifespan initialization bugs, multilingual extraction vulnerabilities, and UI/proxy integration gaps that prevented stable deployment.

---

## 2. Repository Inventory & Architectural Mapping

The codebase is organized into four primary functional tiers: Backend Engine, Frontend Web (Next.js), Streamlit Admin Workbench, and Data/Verification Pipelines.

```
Multilingual-Government-Scheme-Assistant-main/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── admin.py          # Catalog curation, index rebuilds, health metrics
│   │   │   ├── chat.py           # Multi-turn conversational endpoint & reset handler
│   │   │   ├── eligibility.py    # Direct single-scheme eligibility assessment
│   │   │   ├── evaluation.py     # Benchmark retrieval & entity extraction metrics
│   │   │   └── schemes.py        # Scheme catalog search, filtering, and detail lookups
│   │   ├── deps.py               # Dependency injection (HybridRetriever, Database Session)
│   │   └── dependencies.py       # Authentication, database sessions, engine injection
│   ├── core/
│   │   ├── config.py             # Pydantic BaseSettings environment configuration
│   │   ├── logging.py            # Structured logging framework
│   │   └── security.py           # PBKDF2 hashing & constant-time API key verification
│   ├── db/
│   │   ├── models.py             # SQLAlchemy 2.0 ORM models (7 normalized tables)
│   │   └── session.py            # SQLite WAL configuration & PRAGMA management
│   ├── eligibility/
│   │   ├── adaptive_questioner.py# Maximum Information Gain next-question selector
│   │   ├── criterion_rules.py    # Verified statutory rules dictionary
│   │   ├── engine.py             # Deterministic 3-state logic (PASS, FAIL, UNKNOWN)
│   │   ├── near_miss.py          # Near-miss detection & threshold margin calculator
│   │   └── predicates.py         # Relational predicate evaluation operators
│   ├── nlp/
│   │   ├── entity_extractor.py   # Bilingual Regex + rule-based attribute parser
│   │   ├── intent_classifier.py  # Zero-shot query classification
│   │   ├── language_detector.py  # Script detection (Devanagari/Kannada/Latin Unicode)
│   │   └── text_normalizer.py    # Indic Unicode normalization & transliteration
│   ├── rag/
│   │   ├── bm25_retriever.py     # Sparse lexical BM25Okapi retriever
│   │   ├── generator.py          # Grounded LLM response synthesis (Gemini/Ollama/Fallback)
│   │   ├── hybrid_retriever.py   # Reciprocal Rank Fusion (RRF) vector + lexical search
│   │   └── vector_store.py       # FAISS IndexFlatIP dense vector store
│   ├── repositories/
│   │   └── scheme_repo.py        # Relational scheme queries, filters, and stats
│   ├── schemas/
│   │   ├── admin.py              # Pydantic models for admin stats & imports
│   │   ├── chat.py               # Pydantic schemas for multi-turn requests/responses
│   │   ├── eligibility.py        # Criterion result and assessment response schemas
│   │   ├── scheme.py             # Scheme schema, rules, and document requirements
│   │   └── user_profile.py       # Citizen profile attributes and confidence scores
│   ├── services/
│   │   └── chat_service.py       # End-to-end conversation orchestration service
│   └── main.py                   # FastAPI lifespan application entrypoint & CORS
├── frontend/                     # Streamlit Evaluation & Administration Portal
│   ├── app.py                    # Multi-page Streamlit portal entrypoint
│   ├── pages/                    # Multi-page routes (Explorer, Eligibility, Admin, Evaluation)
│   └── services/api_client.py    # Typed client connecting Streamlit to FastAPI REST API
├── frontend-web/                 # Next.js 14 Production Web Application
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat/route.ts     # Edge API route proxying /api/v1/chat
│   │   │   ├── chat/reset/       # Edge API route proxying /api/v1/chat/reset
│   │   │   └── health/route.ts   # Edge API route proxying /api/v1/health
│   │   ├── policies/page.tsx     # Comprehensive 57-Scheme Directory page
│   │   ├── globals.css           # Design tokens, typography scaling, responsive grid
│   │   ├── layout.tsx            # Root layout, metadata, and fonts
│   │   └── page.tsx              # Citizen intake chat UI & document checklist
│   ├── lib/
│   │   ├── policies.json         # Static 57-scheme dataset for client directory
│   │   └── types.ts              # TypeScript interfaces for schemes, chat, profiles
│   ├── package.json              # Next.js 14, React 18, Lucide-react
│   └── tsconfig.json             # TypeScript configuration
├── data/
│   ├── verified_schemes.json     # Master 57 verified Central & Karnataka scheme dataset
│   └── faiss_index/              # Serialized FAISS IndexFlatIP binary
├── scripts/
│   ├── build_index.py            # FAISS and BM25 index generation script
│   ├── clean_ports.py            # Windows TCP process reclamation tool
│   ├── evaluate_bilingual_nlp.py # 12-case gold standard bilingual evaluation runner
│   ├── generate_srs_pdf.py       # Authoritative IEEE 830 ReportLab PDF compiler
│   └── seed_data.py              # SQLite database seeder
├── tests/                        # 62-Test Pytest Verification Suite
└── RUN_SAHAYAKA_WINDOWS.bat      # One-click Windows launch automation
```

---

## 3. Initial Baseline Dependencies & Runtime Configuration

### 3.1 Python Runtime:
* **Interpreter:** Python 3.14.4 (Windows 64-bit)
* **Virtual Environment:** `.venv` or System Python with isolated local dependencies
* **Dependencies:** `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `faiss-cpu`, `rank-bm25`, `sentence-transformers`, `streamlit`, `reportlab`, `pytest`, `httpx`

### 3.2 Node.js & Web Runtime:
* **Node Version:** Node.js v20.18.0 / npm 10.8.2
* **Framework:** Next.js 14.2.33 (App Router)
* **Styling:** Vanilla CSS with custom design tokens, fluid clamp sizing, and `@media print` stylesheets

---

## 4. Initial Defect Findings (Pre-Remediation Baseline)

1. **Host PATH Collision:** Windows executed Python 3.11 shims when invoking `pytest` or `streamlit`, failing on missing modules.
2. **Missing Package Dependencies:** `pydantic-settings`, `faiss-cpu`, and `rank-bm25` were missing in the base Python 3.14 environment.
3. **Lifespan Startup Bug:** `retriever.embedder.encode()` raised `AttributeError` because `HybridRetriever` wraps the embedder inside `vector_store.embedder`.
4. **Kannada Agglutinative Regex Failure:** Word boundary `\b` prevented matching Kannada inflectional case suffixes (e.g. `'22 ವರ್ಷದ'`).
5. **Stub Chat Reset Handler:** `/api/v1/chat/reset` returned a static JSON string without clearing database conversation records or in-memory profile state.
6. **Frontend Compilation Failure:** `frontend-web` failed during `npm run build` because `@/lib/types` and `@/lib/policies.json` were omitted from version control.
7. **Cross-Workspace Port Collision:** Ports 8000 and 8501 were held by orphaned background processes from other workspaces.
8. **SQLite Concurrency Write-Locking:** Default SQLite database configuration raised `OperationalError: database is locked` during concurrent chat requests.

All baseline defects were cataloged for remediation in the subsequent engineering cycles.

