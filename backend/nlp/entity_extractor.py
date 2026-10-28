"""
Entity Extraction & Profile Parsing Module.
Extracts structured citizen eligibility attributes from English, Kannada, and code-mixed
free-text queries with provenance tracking and strict non-inference of unmentioned sensitive attributes.
"""
import re
from typing import Dict, Any, Tuple
from backend.nlp.text_normalizer import TextNormalizer
from backend.schemas.user_profile import UserProfile


class EntityExtractor:
    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        """
        Extracts structured attributes from input text.
        Returns a dictionary of extracted fields, each containing {value, span, confidence}.
        """
        if not text:
            return {}

        results: Dict[str, Any] = {}
        normalized_text = TextNormalizer.normalize_unicode(text)
        digits_normalized = TextNormalizer.normalize_digits(normalized_text)

        # 1. Age extraction
        age_patterns = [
            r"\b(?:i am|age is|age|ವಯಸ್ಸು|ವರ್ಷ)\s*[:=]?\s*([0-9]{1,2})\b",
            r"\b([0-9]{1,2})\s*(?:years?|yrs?|ವಯಸ್ಸು|ವರ್ಷ)\s*(?:old|ಆಗಿದೆ)?\b",
        ]
        for pat in age_patterns:
            m = re.search(pat, digits_normalized, re.IGNORECASE)
            if m:
                val = int(m.group(1))
                if 1 <= val <= 110:
                    results["age"] = {
                        "value": val,
                        "span": m.group(0),
                        "confidence": 0.95,
                    }
                    break

        # Standalone digit when answering an age follow-up question
        if "age" not in results and re.fullmatch(r"^\s*([0-9]{1,2})\s*$", digits_normalized):
            val = int(digits_normalized.strip())
            if 5 <= val <= 95:
                results["age"] = {
                    "value": val,
                    "span": digits_normalized.strip(),
                    "confidence": 0.85,
                }

        # 2. Annual Income extraction
        income_patterns = [
            r"(?:income|salary|earning|annual income|ಆದಾಯ|ಸಂಬಳ)\s*(?:is|of|around)?\s*[:=]?\s*(?:rs\.?|inr|₹|ರೂ\.?)?\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?\s*(?:lakh|lakhs|lac|thousand|cr|crore|k|ಸಾವಿರ|ಲಕ್ಷ|ಕೋಟಿ)?)\b",
            r"(?:rs\.?|inr|₹|ರೂ\.?)\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?\s*(?:lakh|lakhs|lac|thousand|cr|crore|k|ಸಾವಿರ|ಲಕ್ಷ|ಕೋಟಿ)?)\s*(?:per annum|per year|annual|ವಾರ್ಷಿಕ|ಆದಾಯ)",
        ]
        for pat in income_patterns:
            m = re.search(pat, digits_normalized, re.IGNORECASE)
            if m:
                raw_num = m.group(1)
                parsed = TextNormalizer.parse_indian_number(raw_num)
                if parsed is not None:
                    results["annual_income"] = {
                        "value": parsed,
                        "span": m.group(0),
                        "confidence": 0.90,
                    }
                    break

        # Check standalone income answering follow-up
        if "annual_income" not in results:
            standalone_income_pat = r"^\s*(?:rs\.?|inr|₹|ರೂ\.?)?\s*([0-9]+(?:,[0-9]+)*(?:\.[0-9]+)?\s*(?:lakh|lakhs|lac|thousand|cr|crore|k|ಸಾವಿರ|ಲಕ್ಷ|ಕೋಟಿ)?)\s*$"
            m = re.match(standalone_income_pat, digits_normalized, re.IGNORECASE)
            if m:
                parsed = TextNormalizer.parse_indian_number(m.group(1))
                if parsed and parsed > 500:  # Avoid single digit age confusion
                    results["annual_income"] = {
                        "value": parsed,
                        "span": m.group(0).strip(),
                        "confidence": 0.85,
                    }

        # 3. State extraction
        state = TextNormalizer.normalize_state(digits_normalized)
        if state:
            results["state"] = {
                "value": state,
                "span": state,
                "confidence": 0.95,
            }

        # 4. Residence Type (rural vs urban)
        lower_t = digits_normalized.lower()
        if any(w in lower_t for w in ["rural", "village", "grama", "ಗ್ರಾಮ", "ಹಳ್ಳಿ"]):
            results["residence_type"] = {
                "value": "rural",
                "span": "rural",
                "confidence": 0.90,
            }
        elif any(w in lower_t for w in ["urban", "city", "town", "ನಗರ", "ಪಟ್ಟಣ"]):
            results["residence_type"] = {
                "value": "urban",
                "span": "urban",
                "confidence": 0.90,
            }

        # 5. Occupation extraction
        occ = TextNormalizer.normalize_occupation(digits_normalized)
        if occ:
            results["occupation"] = {
                "value": occ,
                "span": occ,
                "confidence": 0.90,
            }
            if occ == "student":
                results["is_student"] = {
                    "value": True,
                    "span": "student",
                    "confidence": 0.95,
                }

        # Student status explicit
        if "is_student" not in results:
            if any(w in lower_t for w in ["student", "studying", "college", "school", "ವಿದ್ಯಾರ್ಥಿ", "ಓದುತ್ತಿದ್ದೇನೆ"]):
                results["is_student"] = {
                    "value": True,
                    "span": "student",
                    "confidence": 0.90,
                }

        # 6. Education Level
        if any(w in lower_t for w in ["degree", "bachelor", "graduate", "b.a", "b.sc", "b.com", "b.e", "btech", "ಪದವಿ"]):
            results["education_level"] = {"value": "graduate", "span": "graduate", "confidence": 0.90}
        elif any(w in lower_t for w in ["diploma", "ಡಿಪ್ಲೋಮಾ"]):
            results["education_level"] = {"value": "diploma", "span": "diploma", "confidence": 0.90}
        elif any(w in lower_t for w in ["postgraduate", "master", "m.a", "m.sc", "m.com", "mtech", "ಸ್ನಾತಕೋತ್ತರ"]):
            results["education_level"] = {"value": "postgraduate", "span": "postgraduate", "confidence": 0.90}
        elif any(w in lower_t for w in ["12th", "puc", "12th pass", "ಪಿಯುಸಿ", "ದ್ವಿತೀಯ ಪಿಯು"]):
            results["education_level"] = {"value": "12th_pass", "span": "12th", "confidence": 0.90}
        elif any(w in lower_t for w in ["10th", "sslc", "10th pass", "ಎಸ್‍ಎಸ್‍ಎಲ್‍ಸಿ"]):
            results["education_level"] = {"value": "10th_pass", "span": "10th", "confidence": 0.90}

        # 7. Gender extraction (only if voluntarily mentioned)
        gender = TextNormalizer.normalize_gender(digits_normalized)
        if gender:
            results["gender"] = {
                "value": gender,
                "span": gender,
                "confidence": 0.90,
            }

        # 8. Social Category (only if explicit)
        cat = TextNormalizer.normalize_category(digits_normalized)
        if cat:
            results["social_category"] = {
                "value": cat,
                "span": cat,
                "confidence": 0.90,
            }

        # 9. Ration card / BPL
        if any(w in lower_t for w in ["bpl", "antyodaya", "priority household", "ಬಿಪಿಎಲ್", "ಅಂತ್ಯೋದಯ"]):
            results["has_bpl_card"] = {
                "value": True,
                "span": "bpl",
                "confidence": 0.95,
            }

        # 10. Landholding (e.g. 2 acres, 1.5 hectares)
        land_pat = r"([0-9]+(?:\.[0-9]+)?)\s*(?:acres?|acre|ಹೆಕ್ಟೇರ್|ಎಕರೆ|hectares?|ha)\b"
        m_land = re.search(land_pat, digits_normalized, re.IGNORECASE)
        if m_land:
            val = float(m_land.group(1))
            # Convert acres to hectares if specified in acres (~0.4046 ha/acre)
            if "acre" in m_land.group(0).lower() or "ಎಕರೆ" in m_land.group(0):
                val = round(val * 0.404686, 2)
            results["land_ownership_ha"] = {
                "value": val,
                "span": m_land.group(0),
                "confidence": 0.85,
            }

        return results

    @classmethod
    def apply_to_profile(
        cls, profile: UserProfile, extracted: Dict[str, Any]
    ) -> UserProfile:
        """Applies newly extracted entities to an existing profile with provenance."""
        for field, data in extracted.items():
            profile.update_field(
                field_name=field,
                value=data["value"],
                span=data["span"],
                confidence=data["confidence"],
                status="provided",
            )
        return profile
