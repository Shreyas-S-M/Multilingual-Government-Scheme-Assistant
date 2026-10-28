# Relational Database Schema Specification

The database is built using normalized **SQLAlchemy 2.0 ORM** models, avoiding single giant JSON dumps and preserving relational queryability, referential integrity, and indexing.

## Tables & Relationships

### 1. `schemes` (Core Scheme Entity)
| Column Name | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto-increment | Internal surrogate primary key |
| `scheme_id` | String(64) | Unique, Indexed, Not Null | Unique URL slug identifier (e.g. `pm-kisan`) |
| `name` | String(255) | Indexed, Not Null | Official English title |
| `name_kannada` | String(255) | Nullable | Official Kannada title |
| `aliases` | JSON | Default: `[]` | Aliases, acronyms, and alternative spellings |
| `level` | String(32) | Indexed, Not Null | `central` or `state` |
| `state` | String(64) | Indexed, Nullable | State restriction (e.g. `Karnataka`) |
| `department` | String(255) | Not Null | Nodal ministry or department |
| `category` | String(64) | Indexed, Not Null | Primary sector (Agriculture, Education, etc.) |
| `subcategory` | String(64) | Nullable | Sub-discipline |
| `short_description` | Text | Not Null | Concise overview |
| `detailed_description` | Text | Not Null | Full official guidelines description |
| `description_kannada` | Text | Nullable | Localized Kannada summary |
| `min_age` | Integer | Nullable | Minimum age limit |
| `max_age` | Integer | Nullable | Maximum age limit |
| `max_income` | Float | Nullable | Family income ceiling in INR |
| `eligible_genders` | JSON | Default: `["all"]` | Target gender categories |
| `eligible_categories` | JSON | Default: `["all"]` | Target social categories |
| `target_occupations` | JSON | Default: `["all"]` | Target occupation sectors |
| `benefits_summary` | Text | Not Null | Financial and non-financial benefit summary |
| `benefits_amount` | String(128) | Nullable | Formatted monetary benefit |
| `required_documents` | JSON | Default: `[]` | Mandatory document list |
| `application_process` | JSON | Default: `[]` | Step-by-step application instructions |
| `official_portal_url` | String(512) | Not Null | Official government website link |
| `application_url` | String(512) | Nullable | Direct online application URL |
| `source_title` | String(255) | Not Null | Official gazette or portal title |
| `source_excerpt` | Text | Not Null | Evidence excerpt establishing criteria |
| `effective_date` | String(32) | Nullable | Launch date (YYYY-MM-DD) |
| `last_verified_date` | String(32) | Not Null | Date of latest verification (YYYY-MM-DD) |
| `source_reliability` | String(64) | Default: `official_portal` | Authority level |
| `status` | String(32) | Indexed, Default: `active` | `active`, `inactive`, `verification_required` |
| `is_active` | Boolean | Indexed, Default: `True` | Soft-deletion flag |
| `created_at` | DateTime | Default: `utcnow` | Timestamp |
| `updated_at` | DateTime | On update: `utcnow` | Timestamp |

### 2. `criterion_rules` (Structured Machine-Checkable Eligibility Rules)
| Column Name | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto-increment | Primary key |
| `criterion_id` | String(64) | Indexed, Not Null | Unique rule identifier (e.g. `pmk_occupation`) |
| `scheme_id` | String(64) | FK -> `schemes.scheme_id`, CASCADE | Parent scheme reference |
| `name` | String(255) | Not Null | Descriptive rule title |
| `field` | String(64) | Indexed, Not Null | Profile field to inspect (`occupation`, `age`, etc.) |
| `operator` | String(32) | Not Null | Predicate operator (`equals`, `range`, `lte`, etc.) |
| `expected_value` | JSON | Not Null | Target scalar, range array, or category list |
| `is_mandatory` | Boolean | Not Null, Default: `True` | Strict requirement vs optional bonus |
| `source_citation` | Text | Not Null | Gazette order or portal clause citation |
| `description_kannada` | Text | Nullable | Localized Kannada rule translation |
| `clarification_question_en` | Text | Nullable | Targeted follow-up question in English |
| `clarification_question_kn` | Text | Nullable | Targeted follow-up question in Kannada |

### 3. `scheme_sources` (Official Provenance & Verification)
| Column Name | Type | Modifiers | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | PK, Auto-increment | Primary key |
| `scheme_id` | String(64) | FK -> `schemes.scheme_id`, CASCADE | Parent scheme |
| `source_url` | String(512) | Not Null | Verifiable official portal URL |
| `source_title` | String(255) | Not Null | Source name |
| `last_checked_date` | String(32) | Not Null | Date verified |
| `verification_status` | String(32) | Indexed | `verified`, `stale`, `flagged` |
| `verification_notes` | Text | Nullable | Auditor remarks |

### 4. `conversations` & `messages` (Conversational State Persistence)
- `conversations`: Stores `session_id`, `language`, `user_profile_snapshot`, `created_at`, `updated_at`.
- `messages`: Stores `conversation_id` (FK), `sender` (`user`/`assistant`), `message_text`, `extracted_entities`, `recommended_scheme_ids`, `created_at`.

### 5. `audit_logs` (Administrative Action Audit Trail)
- Stores `action`, `entity_type`, `entity_id`, `details` (JSON), and `timestamp`.
