"""
Text Normalization & Entity Canonicalization.
Handles Unicode normalization, Kannada digit mapping, Indian currency & number formats,
and canonical ontology mapping for state, occupation, category, and education.
"""
import re
import unicodedata
from typing import Optional, Tuple

# Mapping of Kannada numerals to standard Arabic digits
KANNADA_DIGITS_MAP = {
    "೦": "0",
    "೧": "1",
    "೨": "2",
    "೩": "3",
    "೪": "4",
    "೫": "5",
    "೬": "6",
    "೭": "7",
    "೮": "8",
    "೯": "9",
}

# Currency regexes
CURRENCY_PREFIX = re.compile(r"(?:rs\.?|inr|₹|ರೂ\.?|ರೂಪಾಯಿ)\s*", re.IGNORECASE)

# Indian numeric multipliers
MULTIPLIERS = {
    "k": 1_000.0,
    "thousand": 1_000.0,
    "ಸಾವಿರ": 1_000.0,
    "savira": 1_000.0,
    "l": 100_000.0,
    "lac": 100_000.0,
    "lakh": 100_000.0,
    "lakhs": 100_000.0,
    "ಲಕ್ಷ": 100_000.0,
    "laksha": 100_000.0,
    "cr": 10_000_000.0,
    "crore": 10_000_000.0,
    "crores": 10_000_000.0,
    "ಕೋಟಿ": 10_000_000.0,
    "koti": 10_000_000.0,
}


class TextNormalizer:
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Applies NFC Unicode normalization and cleans spurious control characters."""
        if not text:
            return ""
        text = unicodedata.normalize("NFC", text)
        # Collapse excessive whitespace while preserving newlines
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    @staticmethod
    def normalize_digits(text: str) -> str:
        """Translates Kannada numerals (೦-೯) into standard ASCII digits (0-9)."""
        for kn_digit, ascii_digit in KANNADA_DIGITS_MAP.items():
            text = text.replace(kn_digit, ascii_digit)
        return text

    @classmethod
    def parse_indian_number(cls, raw: str) -> Optional[float]:
        """
        Parses numbers with Indian formatting, commas, or words:
        e.g. '2.5 lakh', '1,50,000', '50 ಸಾವಿರ', '2.5L', '₹3,00,000' -> float
        """
        if not raw:
            return None

        text = cls.normalize_digits(raw.strip().lower())
        # Strip currency symbols
        text = CURRENCY_PREFIX.sub("", text).strip()
        # Remove commas
        clean_text = text.replace(",", "")

        # Check for multiplier pattern: e.g. 2.5 lakh or 2 lakh
        pattern = re.compile(
            r"^([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z\u0C80-\u0CFF]+)?$", re.IGNORECASE
        )
        match = pattern.match(clean_text)
        if match:
            base_str, mult_str = match.groups()
            base_val = float(base_str)
            if mult_str:
                mult_key = mult_str.lower().strip()
                if mult_key in MULTIPLIERS:
                    return base_val * MULTIPLIERS[mult_key]
            return base_val

        # Plain number fallback
        try:
            return float(clean_text)
        except ValueError:
            return None

    @staticmethod
    def normalize_state(text: str) -> Optional[str]:
        """Normalizes state names, aliases, and major cities."""
        if not text:
            return None
        t = text.lower()
        if any(
            x in t
            for x in [
                "karnataka",
                "ಕರ್ನಾಟಕ",
                "bangalore",
                "bengaluru",
                "ಬೆಂಗಳೂರು",
                "mysore",
                "mysuru",
                "ಮೈಸೂರು",
                "hubli",
                "dharwad",
                "belagavi",
                "mangaluru",
                "mangalore",
                "gulbarga",
                "kalaburagi",
                "ka state",
            ]
        ):
            return "Karnataka"
        if "delhi" in t or "ದೆಹಲಿ" in t:
            return "Delhi"
        if "tamil nadu" in t or "ತಮಿಳುನಾಡು" in t:
            return "Tamil Nadu"
        if "maharashtra" in t or "ಮಹಾರಾಷ್ಟ್ರ" in t:
            return "Maharashtra"
        if "andhra" in t or "ಆಂಧ್ರ" in t:
            return "Andhra Pradesh"
        if "telangana" in t or "ತೆಲಂಗಾಣ" in t:
            return "Telangana"
        if "kerala" in t or "ಕೇರಳ" in t:
            return "Kerala"
        return None

    @staticmethod
    def normalize_gender(text: str) -> Optional[str]:
        """Maps user statements to canonical genders: 'female', 'male', 'transgender'."""
        if not text:
            return None
        t = text.lower()
        if any(
            x in t
            for x in [
                "female",
                "woman",
                "women",
                "girl",
                "mother",
                "lady",
                "ಮಹಿಳೆ",
                "ಹೆಣ್ಣು",
                "ಹುಡುಗಿ",
                "ತಾಯಿ",
                "ಸ್ತ್ರೀ",
            ]
        ):
            return "female"
        if any(
            x in t
            for x in [
                "transgender",
                "trans",
                "third gender",
                "ತೃತೀಯಲಿಂಗಿ",
                "ಮಂಗಳಮುಖಿ",
            ]
        ):
            return "transgender"
        if any(
            x in t
            for x in [
                "male",
                "man",
                "boy",
                "father",
                "gentleman",
                "ಪುರುಷ",
                "ಗಂಡು",
                "ಹುಡುಗ",
                "ತಂದೆ",
            ]
        ):
            return "male"
        return None

    @staticmethod
    def normalize_occupation(text: str) -> Optional[str]:
        """Normalizes occupation phrases into schema categories."""
        if not text:
            return None
        t = text.lower()
        # Farmer
        if any(
            x in t
            for x in [
                "farmer",
                "farming",
                "agriculture",
                "cultivator",
                "grower",
                "raitha",
                "krishika",
                "ರೈತ",
                "ಕೃಷಿಕ",
                "ಕೃಷಿ",
                "ವ್ಯವಸಾಯ",
            ]
        ):
            return "farmer"
        # Street vendor
        if any(
            x in t
            for x in [
                "street vendor",
                "vendor",
                "hawker",
                "cart",
                "beedi vyapari",
                "ಬೀದಿ ವ್ಯಾಪಾರಿ",
                "ತಳ್ಳುವ ಗಾಡಿ",
            ]
        ):
            return "street_vendor"
        # Artisan / craftsman
        if any(
            x in t
            for x in [
                "artisan",
                "craftsman",
                "carpenter",
                "potter",
                "blacksmith",
                "goldsmith",
                "weaver",
                "cobbler",
                "tailor",
                "sculptor",
                "ಕುಶಲಕರ್ಮಿ",
                "ಬಡಗಿ",
                "ಕುಂಬಾರ",
                "ಕಮ್ಮಾರ",
                "ದರ್ಜಿ",
                "ನೇಕಾರ",
            ]
        ):
            return "artisan"
        # Student
        if any(
            x in t
            for x in [
                "student",
                "studying",
                "school",
                "college",
                "university",
                "vidyarthi",
                "ವಿದ್ಯಾರ್ಥಿ",
                "ಓದುತ್ತಿದ್ದೇನೆ",
                "ಕಾಲೇಜು",
            ]
        ):
            return "student"
        # Unemployed
        if any(
            x in t
            for x in [
                "unemployed",
                "jobless",
                "looking for job",
                "no job",
                "graduated",
                "nirudyogi",
                "ನಿರುದ್ಯೋಗಿ",
                "ಕೆಲಸವಿಲ್ಲ",
            ]
        ):
            return "unemployed"
        # Salaried / Employed
        if any(
            x in t
            for x in [
                "salaried",
                "employee",
                "private job",
                "company",
                "ಕೆಲಸಗಾರ",
                "ಉದ್ಯೋಗಿ",
            ]
        ):
            return "salaried"
        # Self employed
        if any(
            x in t
            for x in [
                "self employed",
                "business",
                "shop",
                "shopkeeper",
                "ಸ್ವಂತ ಉದ್ಯೋಗ",
                "ವ್ಯಾಪಾರ",
            ]
        ):
            return "self_employed"
        return None

    @staticmethod
    def normalize_category(text: str) -> Optional[str]:
        """Maps social category phrases into canonical identifiers with word boundary safety."""
        if not text:
            return None
        t = text.lower()
        if (
            re.search(r"\b(?:sc|scheduled caste|dalit)\b", t)
            or "ಪರಿಶಿಷ್ಟ ಜಾತಿ" in t
            or "ದಲಿತ" in t
        ):
            return "sc"
        if (
            re.search(r"\b(?:st|scheduled tribe|adivasi)\b", t)
            or "ಪರಿಶಿಷ್ಟ ಪಂಗಡ" in t
            or "ಆದಿವಾಸಿ" in t
        ):
            return "st"
        if (
            re.search(r"\b(?:obc|backward class|backward caste)\b", t)
            or "ಹಿಂದುಳಿದ ವರ್ಗ" in t
        ):
            return "obc"
        if (
            re.search(
                r"\b(?:minority|muslim|christian|jain|sikh|parsi|buddhist)\b", t
            )
            or "ಅಲ್ಪಸಂಖ್ಯಾತ" in t
            or "ಮುಸ್ಲಿಂ" in t
            or "ಕ್ರಿಶ್ಚಿಯನ್" in t
        ):
            return "minority"
        if (
            re.search(r"\b(?:ews|economically weaker)\b", t)
            or "ಆರ್ಥಿಕವಾಗಿ ದುರ್ಬಲ" in t
        ):
            return "ews"
        if (
            re.search(r"\b(?:general|general category|open category)\b", t)
            or "ಸಾಮಾನ್ಯ ವರ್ಗ" in t
        ):
            return "general"
        return None
