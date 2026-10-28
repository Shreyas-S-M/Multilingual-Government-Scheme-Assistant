# Multilingual NLP Pipeline Specification

## 1. Multilingual Support Architecture

The Multilingual Government Scheme Assistant natively processes **English**, **Kannada (ಕನ್ನಡ)**, and **code-mixed Kannada-English (Kanglish)** queries.

### Script Recognition:
- Kannada Unicode Range: `\u0C80` to `\u0CFF`
- High density of native script ($\ge 25\%$) -> Categorized as Kannada (`kn`).
- Interspersed script ($\ge 5\%$) -> Categorized as Code-Mixed Kannada (`kn`, mixed).
- Latin script with frequent Kannada lexical markers (`nanna`, `beku`, `yavudu`, `yojane`, `raitha`, `kelsa`, `sigutthe`, etc.) -> Categorized as Code-Mixed Kannada (`kn`, mixed).
- Standard Latin -> Categorized as English (`en`).

---

## 2. Text Normalization Pipeline

### 2.1 Unicode NFC Standardization
All incoming queries are processed through standard Unicode Normalization Form C (`unicodedata.normalize("NFC", text)`), resolving variant glyph combinations.

### 2.2 Kannada Numeral Canonicalization
Kannada digits are normalized to standard Arabic numerals:
| Kannada Digit | ASCII Equivalent |
| :---: | :---: |
| ೦ | 0 |
| ೧ | 1 |
| ೨ | 2 |
| ೩ | 3 |
| ೪ | 4 |
| ೫ | 5 |
| ೬ | 6 |
| ೭ | 7 |
| ೮ | 8 |
| ೯ | 9 |

*Example:* `೨೫ ವರ್ಷ` -> `25 ವರ್ಷ` -> Extracted as `age: 25`.

### 2.3 Indian Currency & Multiplier Parsing
The normalizer decodes Indian numbering conventions:
- **Lakh (ಲಕ್ಷ, lacs, l):** Multiplied by $10^5$ (e.g. `2.5 lakh` -> `250000.0`, `೧.೫ ಲಕ್ಷ` -> `150000.0`).
- **Thousand (ಸಾವಿರ, k):** Multiplied by $10^3$ (e.g. `50 ಸಾವಿರ` -> `50000.0`).
- **Crore (ಕೋಟಿ, cr):** Multiplied by $10^7$ (e.g. `1 crore` -> `10000000.0`).

---

## 3. Named Entity Recognition (NER) & Non-Inference Rules

### Extracted Demographic & Socioeconomic Attributes
1. `age`: Integer (1-110)
2. `annual_income`: Float in INR
3. `state`: Normalized state (e.g. `Karnataka`, `Delhi`, etc.)
4. `occupation`: Canonical occupation (`farmer`, `student`, `artisan`, `street_vendor`, `unemployed`, `salaried`)
5. `education_level`: `10th_pass`, `12th_pass`, `graduate`, `diploma`, `postgraduate`
6. `is_student`: Boolean
7. `gender`: `female`, `male`, `transgender` (only when voluntarily mentioned)
8. `social_category`: `sc`, `st`, `obc`, `minority`, `ews`, `general` (word-boundary safe)
9. `has_bpl_card`: Boolean (based on BPL, Antyodaya, ration card mentions)
10. `land_ownership_ha`: Float in hectares (converts acres using factor 0.404686)

### Ethical Non-Inference Safeguards:
- Caste, religion, disability, and income are **never** inferred from a citizen's name, dialect, location, or writing style.
- If a query states `"My name is Ramesh from Mysore"`, the system extracts `state: Karnataka`, but records `social_category: None` and `annual_income: None`.
