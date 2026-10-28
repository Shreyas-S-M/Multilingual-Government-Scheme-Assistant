# REST API Contracts & Endpoint Specifications

All endpoints are versioned under the base prefix `/api/v1`.
Interactive OpenAPI documentation is accessible at `/api/v1/docs`.

---

## 1. Health & Diagnostics

### `GET /api/v1/health`
Checks backend server, relational database, vector index, and active LLM provider.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "app_name": "Multilingual Government Scheme Assistant",
  "app_version": "1.0.0",
  "environment": "development",
  "components": {
    "database": {
      "status": "connected",
      "engine": "sqlite"
    },
    "vector_search": {
      "status": "ready",
      "indexed_records": 22,
      "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    },
    "llm_provider": {
      "status": "active",
      "provider": "deterministic",
      "model": "gemini-1.5-flash"
    }
  }
}
```

---

## 2. Scheme Catalog & Discovery

### `GET /api/v1/schemes`
Filter and paginate verified government schemes.

**Query Parameters:**
- `category` (optional): Filter by sector (`Agriculture`, `Education`, etc.)
- `level` (optional): `central` or `state`
- `state` (optional): e.g. `Karnataka`
- `search` (optional): Keyword search over title, aliases, and description
- `page` (default: 1)
- `page_size` (default: 10)

**Response (200 OK):**
```json
{
  "total": 22,
  "page": 1,
  "page_size": 10,
  "total_pages": 3,
  "items": [
    {
      "scheme_id": "pm-kisan",
      "name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
      "name_kannada": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ (ಪಿಎಂ-ಕಿಸಾನ್)",
      "level": "central",
      "category": "Agriculture",
      "benefits_summary": "Rs. 6,000 annual direct benefit transfer in 3 installments...",
      "official_portal_url": "https://pmkisan.gov.in/",
      "rules_count": 2
    }
  ]
}
```

### `GET /api/v1/schemes/{scheme_id}`
Returns full verified scheme schema including structured criteria rules, required documents, application process, and source citations.

---

## 3. Conversational Assistant

### `POST /api/v1/chat`
Processes conversational queries with profile extraction, three-state evaluation, and adaptive question generation.

**Request Payload:**
```json
{
  "message": "I am a 25 year old farmer living in Karnataka with annual income of 1.5 lakh.",
  "conversation_id": "optional-uuid",
  "language": "en",
  "current_profile": null
}
```

**Response (200 OK):**
```json
{
  "reply": "### Personalized Government Scheme Assessment\n...",
  "language": "en",
  "detected_language": "en",
  "intent": "check_eligibility",
  "conversation_id": "a47bdbe6-434a-43ec-893f-2c054d80a657",
  "extracted_entities": {
    "age": 25,
    "annual_income": 150000.0,
    "state": "Karnataka",
    "occupation": "farmer"
  },
  "updated_profile": {
    "age": 25,
    "annual_income": 150000.0,
    "state": "Karnataka",
    "occupation": "farmer"
  },
  "recommended_schemes": [
    {
      "scheme_id": "pm-kisan",
      "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
      "overall_status": "PASS",
      "mandatory_passed_count": 2,
      "mandatory_failed_count": 0,
      "mandatory_unknown_count": 0,
      "benefits_summary": "Rs. 6,000 annual direct benefit transfer in 3 installments...",
      "official_portal_url": "https://pmkisan.gov.in/"
    }
  ],
  "near_miss_schemes": [],
  "follow_up_question": null,
  "follow_up_target_attribute": null
}
```

---

## 4. Standalone Eligibility Check

### `POST /api/v1/eligibility/check`
Directly evaluates an applicant profile against rules without conversational state.

**Request Payload:**
```json
{
  "profile": {
    "age": 24,
    "annual_income": 120000.0,
    "state": "Karnataka",
    "occupation": "farmer"
  },
  "scheme_ids": ["pm-kisan", "raitha-siri-karnataka"]
}
```

**Response (200 OK):** Array of `SchemeEligibilityResult` objects with granular criterion breakdowns.

---

## 5. Administrative Endpoints (Protected by `X-Admin-API-Key`)

- `GET /api/v1/admin/stats`: Summary counts of total schemes, active records, and indexed vectors.
- `POST /api/v1/admin/schemes`: Create a new verified government scheme.
- `PUT /api/v1/admin/schemes/{scheme_id}`: Update scheme metadata or active status.
- `POST /api/v1/admin/index/rebuild`: Rebuilds FAISS dense vector store and BM25 index.
- `POST /api/v1/admin/schemes/import`: Bulk import verified scheme JSON records.
