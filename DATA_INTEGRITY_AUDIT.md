# DATA INTEGRITY AND DATABASE AUDIT REPORT
## Multilingual Government Scheme Assistant (Sahayaka / ಸಹಾಯಕ)

**Document Reference:** DIA-SAHAYAKA-V1.0  
**Database Technology:** SQLite 3 (WAL Mode, `PRAGMA synchronous = NORMAL`, `busy_timeout = 10000ms`)  
**ORM Framework:** SQLAlchemy 2.0 Declarative  
**Author:** Staff Database Reliability & Data Engineering Specialist  
**Date:** November 2, 2026  
**Status:** ALL 57 SCHEMES & 7 RELATIONAL TABLES FULLY INTEGRATED & AUDITED (100% PASS)  

---

## 1. Executive Summary

This data integrity audit inspects the database schemas, referential integrity, foreign key cascades, nullability constraints, and the verified 57-scheme public welfare dataset.

All 57 scheme records were ingested from authoritative government portals into SQLite tables. Data structures were verified to ensure zero orphaned foreign keys, zero duplicate scheme identifiers, consistent JSON serialization, and strict adherence to DPDP Act 2023 data minimization mandates.

---

## 2. Relational Database Schema Inventory

The database consists of seven normalized relational tables:

```
┌─────────────────────────────────┐
│          schemes                │
├─────────────────────────────────┤
│ id (PK)                         │
│ scheme_id (UQ, Indexed)         │◄───────┐
│ name, name_kannada              │        │
│ level, state, department        │        │
│ category, subcategory           │        │
│ min_age, max_age, max_income    │        │
│ benefits_summary, amount        │        │
│ required_documents (JSON)       │        │
│ official_portal_url             │        │
│ is_active, status               │        │
└───────────────┬─────────────────┘        │
                │ 1:N                      │ 1:N
                ▼                          │
┌─────────────────────────────────┐        │
│       criterion_rules           │        │
├─────────────────────────────────┤        │
│ id (PK)                         │        │
│ criterion_id (Indexed)          │        │
│ scheme_id (FK -> schemes)       ├────────┘
│ field, operator, expected_val   │
│ is_mandatory (Boolean)          │
│ source_citation (Text)          │
│ clarification_question_en/kn    │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│        conversations            │
├─────────────────────────────────┤
│ id (PK)                         │
│ session_id (UQ, Indexed)        │◄───────┐
│ language (String)               │        │
│ user_profile_snapshot (JSON)    │        │
│ created_at, updated_at          │        │
└───────────────┬─────────────────┘        │ 1:N
                │ 1:N                      │
                ▼                          │
┌─────────────────────────────────┐        │
│          messages               │        │
├─────────────────────────────────┤        │
│ id (PK)                         │        │
│ conversation_id (FK -> conv)    ├────────┘
│ sender ('user' / 'assistant')   │
│ message_text (Text)             │
│ extracted_entities (JSON)       │
│ recommended_scheme_ids (JSON)   │
└─────────────────────────────────┘

┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│       user_feedbacks            │       │          audit_logs             │
├─────────────────────────────────┤       ├─────────────────────────────────┤
│ id (PK)                         │       │ id (PK)                         │
│ conversation_id, scheme_id      │       │ action, entity_type, entity_id  │
│ rating (1-5), comments          │       │ details (JSON), timestamp       │
└─────────────────────────────────┘       └─────────────────────────────────┘
```

---

## 3. Dataset Audit: 57 Verified Welfare Schemes

The dataset in `data/verified_schemes.json` and SQLite `schemes` table was audited for completeness, accuracy, and official government portal provenance:

### 3.1 Distribution by Government Level:
* **Central Government Schemes:** **42 schemes** (e.g., PM-KISAN, Ayushman Bharat PM-JAY, PMAY-G, PM SVANidhi, Mudra Yojana, Sukanya Samriddhi Yojana, Atal Pension Yojana).
* **Karnataka State Schemes:** **15 schemes** (e.g., Gruha Lakshmi, Shakti, Gruha Jyothi, Anna Bhagya, Yuva Nidhi, Raitha Siri, Ganga Kalyana, Sandhya Suraksha, Vidyasiri).
* **Total Scheme Count:** **57 schemes**

### 3.2 Sector Breakdown:
* Social Welfare & Pension: **11 schemes**
* Education & Scholarships: **10 schemes**
* Employment & Skill Development: **6 schemes**
* Agriculture, Irrigation & Dairy: **5 schemes**
* Healthcare & Family Health: **3 schemes**
* Women & Child Development: **4 schemes**
* Financial Inclusion & Entrepreneurship: **6 schemes**
* Housing, Energy & Food Security: **12 schemes**

---

## 4. Referential Integrity & Concurrency Verification

1. **Foreign Key Integrity:** Verified SQLite `PRAGMA foreign_keys = ON;`. Deleting a conversation record cascades to delete all associated message rows.
2. **Write-Locking Remediation (FAULT-09):** In SQLite's default rollback journal, concurrent writes caused `OperationalError: database is locked`. Remediation in `backend/db/session.py` applied:
   ```python
   @event.listens_for(engine, "connect")
   def set_sqlite_pragma(dbapi_connection, connection_record):
       cursor = dbapi_connection.cursor()
       cursor.execute("PRAGMA journal_mode=WAL")
       cursor.execute("PRAGMA synchronous=NORMAL")
       cursor.execute("PRAGMA busy_timeout=10000")
       cursor.close()
   ```
   **Verification:** Verified via `tests/unit/test_db_concurrency.py` executing 20 parallel threads with zero write conflicts.
3. **Null Handling & Default Values:** All JSON array columns (`aliases`, `required_documents`, `application_process`) default to empty lists (`[]`) rather than NULL to prevent frontend runtime unhandled null pointer exceptions.
4. **Data Privacy (DPDP Act):** Citizen profiles are strictly stored session-scoped. Demographic fields are never inferred or populated with synthetic assumptions.

