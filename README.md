# 🇮🇳 Multilingual Government Scheme Assistant

**Institution:** School of Computer Science and Engineering, RV University, Bengaluru  
**Faculty Guide:** Dr. Roopesh  
**Project Team:**  
- Shreyas Kamath D (`1RUA24CSE0444`)  
- Shreyas S M (`1RUA24CSE0446`)  
- Shreyash Annegowda (`1RUA24CSE0447`)  
- Skanda C H (`1RUA24CSE0463`)  

An intelligent, full-stack, multilingual natural language assistant engineered to discover Indian Central and Karnataka State government welfare schemes with **transparent three-state eligibility reasoning (`PASS`, `FAIL`, `UNKNOWN`)**, adaptive clarification questioning, and evidence-grounded recommendations.

Built natively in Python using **Streamlit**, **FastAPI**, **SQLAlchemy 2.0**, **FAISS**, and **Multilingual Sentence Transformers / BM25**.

---

## 🌟 Academic Innovation Highlights

Unlike generic chatbots or naive RAG pipelines that hallucinate or falsely reject citizens when information is missing:
1. **Three-State Eligibility Reasoning Engine (`PASS`, `FAIL`, `UNKNOWN`):**
   - **`PASS`**: Citizen meets all mandatory conditions.
   - **`FAIL`**: Citizen explicitly violates a mandatory requirement.
   - **`UNKNOWN`**: Incomplete data yields `UNKNOWN` with actionable clarification prompts instead of false rejections.
2. **Authoritative Rule Boundary:**
   - Semantic similarity vectors **never** override a confirmed mandatory eligibility failure.
3. **Adaptive Clarification Questioning:**
   - When candidate schemes contain `UNKNOWN` mandatory conditions, the system dynamically identifies and prompts for the single missing attribute that resolves uncertainty for the most schemes.
4. **Near-Miss Scheme Recommendations:**
   - When an applicant fails a desired scheme (e.g. income limit exceeded for a scholarship), the assistant identifies viable alternative programs in the same sector and provides comparative justifications.
5. **Multilingual Entity Normalization:**
   - Robust parsing of English, native Kannada Unicode (`\u0C80-\u0CFF`), and code-mixed Kanglish.
   - Normalizes Indian currency expressions (`lakh`, `crore`, `ಸಾವಿರ`, `₹`) and Kannada numerals (`೦-೯`).
6. **Strict Ethical Non-Inference:**
   - Sensitive citizen attributes (caste, religion, disability, income) are **never** guessed or inferred from names, dialects, or geographical locations.

---

## 🏗️ System Architecture

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
                            | - 22 Verified Schemes & Rules |
                            | - Sources & Provenance        |
                            | - SQLite / PostgreSQL         |
                            +-------------------------------+
```

---

## 📁 Repository Structure

```
multilingual-government-scheme-assistant/
├── frontend/
│   ├── app.py                     # Main Streamlit Chat Application
│   ├── pages/
│   │   ├── 1_Scheme_Explorer.py   # Scheme browsing, filters, and guidelines
│   │   ├── 2_Eligibility_Assessment.py # Standalone predicate testing
│   │   ├── 3_Admin_Dashboard.py   # Protected catalog & index management
│   │   ├── 4_Evaluation_Dashboard.py   # Academic benchmark metrics
│   │   └── 5_About_and_Privacy.py # Ethical NLP & citizen privacy notice
│   ├── components/                # Reusable UI cards and tables
│   ├── services/api_client.py     # HTTP client for FastAPI communication
│   └── styles/main.css            # Custom CSS for badges, cards, and layouts
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── api/routes/                # Modular REST route handlers
│   ├── core/                      # Config, logging, and security
│   ├── models/database.py         # Normalized SQLAlchemy 2.0 ORM models
│   ├── schemas/                   # Pydantic validation schemas
│   ├── db/session.py              # Database engine & session lifecycle
│   ├── repositories/              # Scheme & Conversation CRUD
│   ├── services/chat_service.py   # Turn orchestrator
│   ├── nlp/                       # Multilingual detector, normalizer, NER
│   ├── retrieval/                 # FAISS vector store, BM25, hybrid search
│   ├── eligibility/               # 3-State engine, adaptive Qs, near-miss
│   └── rag/                       # Grounded generator & context builder
├── data/
│   ├── schemes/                   # 22 Individual verified scheme JSON records
│   ├── seed/verified_schemes.json # Consolidated seed dataset
│   └── processed/                 # SQLite database and FAISS index binary
├── scripts/
│   ├── seed_data.py               # Seeds schemes into database
│   ├── build_index.py             # Rebuilds FAISS and BM25 index
│   └── generate_schemes_seed.py   # Generates verified schemes data
├── tests/
│   ├── unit/                      # Unit tests for NLP and Eligibility
│   ├── api/                       # API route integration tests
│   └── evaluation/                # 20 End-to-end evaluation scenarios
├── docs/                          # Architecture, DB schema, API contracts
├── Dockerfile                     # Multi-stage production container
├── docker-compose.yml             # Orchestration for frontend & backend
├── requirements.txt               # Pinned Python dependencies
├── pytest.ini                     # Pytest configuration
└── README.md                      # Complete system documentation
```

---

## ⚡ Quick Start Guide (Windows PowerShell)

### 1. Prerequisites
- Python 3.11 or 3.12 installed on your machine.
- Git (optional).

### 2. Environment Configuration
Clone or navigate to the project directory, then copy the example environment file:
```powershell
Copy-Item .env.example .env
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Initialize Database & Seed Verified Schemes
Run the seed script to create all normalized tables and insert the 22 verified Central and Karnataka State schemes:
```powershell
python -m scripts.seed_data
```

### 5. Build FAISS Vector Index
Generate the multilingual dense vector index and BM25 index:
```powershell
python -m scripts.build_index
```

### 6. Start the Backend API Server
In a PowerShell terminal, start the FastAPI server on port 8000:
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive API Docs: `http://127.0.0.1:8000/api/v1/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

### 7. Start the Streamlit Web Application
In a **new** PowerShell terminal, start the Streamlit frontend:
```powershell
streamlit run frontend/app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full automated test suite (53 tests covering unit, API, and the 20 academic evaluation scenarios):
```powershell
pytest -v
```

All 53 tests run and pass in ~12 seconds.

---

## 🏛️ Knowledge Base of Verified Government Schemes

The catalog includes 22 authentic schemes verified against official portals:

| Scheme ID | Scheme Title | Level | Category | Key Benefit | Official Source |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `pm-kisan` | PM Kisan Samman Nidhi | Central | Agriculture | Rs. 6,000 / year DBT | [pmkisan.gov.in](https://pmkisan.gov.in/) |
| `ayushman-bharat-pmjay` | Ayushman Bharat PM-JAY | Central | Healthcare | Rs. 5 Lakh cashless cover | [pmjay.gov.in](https://pmjay.gov.in/) |
| `pm-mudra-yojana` | PM Mudra Yojana (PMMY) | Central | Employment | Loans up to Rs. 10 Lakh | [mudra.org.in](https://www.mudra.org.in/) |
| `pmay-g` | PM Awas Yojana - Gramin | Central | Housing | Rs. 1.20 Lakh housing grant | [pmayg.nic.in](https://pmayg.nic.in/) |
| `post-matric-sc` | Post Matric Scholarship SC | Central | Education | 100% Fees + Maintenance | [scholarships.gov.in](https://scholarships.gov.in/) |
| `gruha-lakshmi-karnataka`| Gruha Lakshmi Scheme | Karnataka | Social Welfare | Rs. 2,000 / month to women | [sevasindhu.karnataka.gov.in](https://sevasindhu.karnataka.gov.in/) |
| `yuva-nidhi-karnataka` | Yuva Nidhi Scheme | Karnataka | Employment | Rs. 3,000/mo (graduates) | [sevasindhu.karnataka.gov.in](https://sevasindhu.karnataka.gov.in/) |
| `anna-bhagya-karnataka` | Anna Bhagya Scheme | Karnataka | Food Security | 10 kg grains + DBT cash | [ahara.kar.nic.in](https://ahara.kar.nic.in/) |
| `gruha-jyothi-karnataka`| Gruha Jyothi Scheme | Karnataka | Power | Up to 200 units free power | [sevasindhu.karnataka.gov.in](https://sevasindhu.karnataka.gov.in/) |
| `shakti-scheme-karnataka`| Shakti Scheme | Karnataka | Transport | Free RTC bus travel for women | [ksrtc.karnataka.gov.in](https://ksrtc.karnataka.gov.in/) |
| `raitha-siri-karnataka` | Raitha Siri Scheme | Karnataka | Agriculture | Rs. 10,000/ha for millets | [raitamitra.karnataka.gov.in](https://raitamitra.karnataka.gov.in/) |
| `vidyasiri-karnataka` | Vidyasiri Student Stipend | Karnataka | Education | Rs. 1,500/mo living grant | [bcwd.karnataka.gov.in](https://bcwd.karnataka.gov.in/) |
| `pm-svanidhi` | PM SVANidhi (Street Vendors)| Central | Employment | Rs. 10,000-50,000 loan + subsidy | [pmsvanidhi.mohua.gov.in](https://pmsvanidhi.mohua.gov.in/) |
| `pm-vishwakarma` | PM Vishwakarma Scheme | Central | Employment | Rs. 15,000 toolkit + Rs. 3L loan | [pmvishwakarma.gov.in](https://pmvishwakarma.gov.in/) |
| `ganga-kalyana-karnataka`| Ganga Kalyana Scheme | Karnataka | Agriculture | Free borewell drilling & pump | [karnataka.gov.in](https://karnataka.gov.in/) |
| `atal-pension-yojana` | Atal Pension Yojana (APY) | Central | Social Security | Rs. 1,000-5,000 monthly pension | [npscra.nsdl.co.in](https://www.npscra.nsdl.co.in/) |
| `sukanya-samriddhi-yojana`| Sukanya Samriddhi Yojana | Central | Girl Child | 8.2% p.a. tax-free savings | [indiapost.gov.in](https://www.indiapost.gov.in/) |
| `nmmss` | National Means-cum-Merit | Central | Education | Rs. 12,000 / year (Class 9-12)| [scholarships.gov.in](https://scholarships.gov.in/) |
| `pmfby` | PM Fasal Bima Yojana | Central | Agriculture | Crop damage insurance cover | [pmfby.gov.in](https://pmfby.gov.in/) |
| `stand-up-india` | Stand-Up India Scheme | Central | Entrepreneurship| Rs. 10 Lakh - 1 Cr bank credit | [standupmitra.in](https://www.standupmitra.in/) |
| `pre-matric-minority` | Pre-Matric Minority Scholar.| Central | Education | Up to Rs. 9,000 / year | [scholarships.gov.in](https://scholarships.gov.in/) |
| `arundhati-karnataka` | Karnataka Arundhati Scheme | Karnataka | Social Welfare | Rs. 25,000 marriage grant | [sevasindhu.karnataka.gov.in](https://sevasindhu.karnataka.gov.in/) |

---

## 🔒 Security & Citizen Privacy Principles

1. **Zero Data Harvesting:** No citizen account registration is required to search schemes.
2. **Explicit Consent & Non-Inference:** Sensitive attributes such as Caste, Religion, and Income are **never** inferred from names or locations.
3. **Deterministic Local Execution:** The system functions completely without external API calls in deterministic mode, ensuring data privacy.

---

## 🐳 Docker Deployment

To launch the full stack with Docker Compose:
```bash
docker-compose up --build
```
- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000/api/v1/docs`

---

## 📄 License & Academic Attribution
Developed as an Academic NLP Capstone Project. Official government guidelines are referenced under Fair Dealing for informational and non-commercial educational purposes.
