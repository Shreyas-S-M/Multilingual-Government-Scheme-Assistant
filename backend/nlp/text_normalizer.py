"""
Text Normalization & Entity Canonicalization.
Handles Unicode normalization, Kannada digit mapping, Indian currency & number formats,
and canonical ontology mapping for state, occupation, category, and education.
"""
import re
import unicodedata
from typing import Optional, Tuple

# Mapping of Indic numerals (Kannada, Telugu, Tamil, Malayalam) to standard Arabic digits
INDIC_DIGITS_MAP = {
    # Kannada
    "೦": "0", "೧": "1", "೨": "2", "೩": "3", "೪": "4", "೫": "5", "೬": "6", "೭": "7", "೮": "8", "೯": "9",
    # Telugu
    "౦": "0", "౧": "1", "౨": "2", "౩": "3", "౪": "4", "౫": "5", "౬": "6", "౭": "7", "౮": "8", "౯": "9",
    # Tamil
    "௦": "0", "௧": "1", "௨": "2", "௩": "3", "௪": "4", "௫": "5", "௬": "6", "௭": "7", "௮": "8", "௯": "9",
    # Malayalam
    "൦": "0", "൧": "1", "൨": "2", "൩": "3", "൪": "4", "൫": "5", "൬": "6", "൭": "7", "൮": "8", "൯": "9",
}
KANNADA_DIGITS_MAP = INDIC_DIGITS_MAP

# Currency regexes for South Indian languages and standard terms
CURRENCY_PREFIX = re.compile(r"(?:rs\.?|inr|₹|ರೂ\.?|ರೂಪಾಯಿ|రూ\.?|రూపాయలు|ரூ\.?|ரூபாய்|രൂപ|രൂ\.?)\s*", re.IGNORECASE)

# Indian numeric multipliers across English, Kannada, Telugu, Tamil, Malayalam
MULTIPLIERS = {
    "k": 1_000.0,
    "thousand": 1_000.0,
    "ಸಾವಿರ": 1_000.0,
    "savira": 1_000.0,
    "వేలు": 1_000.0,
    "velu": 1_000.0,
    "ஆயிரம்": 1_000.0,
    "aayiram": 1_000.0,
    "ആയിരം": 1_000.0,
    "l": 100_000.0,
    "lac": 100_000.0,
    "lakh": 100_000.0,
    "lakhs": 100_000.0,
    "ಲಕ್ಷ": 100_000.0,
    "laksha": 100_000.0,
    "లక్ష": 100_000.0,
    "లక్షలు": 100_000.0,
    "லட்சம்": 100_000.0,
    "latcham": 100_000.0,
    "ലക്ഷം": 100_000.0,
    "laksham": 100_000.0,
    "cr": 10_000_000.0,
    "crore": 10_000_000.0,
    "crores": 10_000_000.0,
    "ಕೋಟಿ": 10_000_000.0,
    "koti": 10_000_000.0,
    "కోటి": 10_000_000.0,
    "கோடி": 10_000_000.0,
    "kodi": 10_000_000.0,
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

        # Check for multiplier pattern: e.g. 2.5 lakh or 2 lakh or 50 thousand
        pattern = re.compile(
            r"^([0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z\u0B80-\u0D7F\s]+)?$", re.IGNORECASE
        )
        match = pattern.match(clean_text)
        if match:
            base_str, mult_str = match.groups()
            base_val = float(base_str)
            if mult_str:
                mult_key = mult_str.lower().strip()
                if mult_key in MULTIPLIERS:
                    return base_val * MULTIPLIERS[mult_key]
                first_word = mult_key.split()[0] if mult_key.split() else ""
                if first_word in MULTIPLIERS:
                    return base_val * MULTIPLIERS[first_word]
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
        if "delhi" in t or "ದೆಹಲಿ" in t or "ఢిల్లీ" in t or "டெல்லி" in t or "ഡൽഹി" in t:
            return "Delhi"
        if any(x in t for x in ["tamil nadu", "tamilnadu", "ತಮಿಳುನಾಡು", "తమిళనాడు", "தமிழ்நாடு", "தமிழகம்", "chennai", "சென்னை"]):
            return "Tamil Nadu"
        if "maharashtra" in t or "ಮಹಾರಾಷ್ಟ್ರ" in t or "మహారాష్ట్ర" in t:
            return "Maharashtra"
        if any(x in t for x in ["andhra", "andhra pradesh", "ಆಂಧ್ರ", "ಆಂಧ್ರಪ್ರದೇಶ", "ఆంధ్రప్రదేశ్", "ఆంధ్ర", "amaravati", "visakhapatnam", "vijayawada"]):
            return "Andhra Pradesh"
        if any(x in t for x in ["telangana", "ತೆಲಂಗಾಣ", "తెలంగాణ", "hyderabad", "హైదరాబాద్"]):
            return "Telangana"
        if any(x in t for x in ["kerala", "ಕೇರಳ", "కేరళ", "കേരളം", "കേരള", "thiruvananthapuram", "kochi"]):
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
                # Kannada
                "ಮಹಿಳೆ",
                "ಹೆಣ್ಣು",
                "ಹುಡುಗಿ",
                "ತಾಯಿ",
                "ಸ್ತ್ರೀ",
                # Telugu
                "మహిళ",
                "స్త్రీ",
                "అమ్మాయి",
                "తల్లి",
                # Tamil
                "பெண்",
                "மகளிர்",
                "தாய்",
                "அம்மா",
                # Malayalam
                "സ്ത്രീ",
                "വനിത",
                "പെൺകുട്ടി",
                "അമ്മ",
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
                "ట్రాన్స్‌జెండర్",
                "திருநங்கை",
                "ഭിന്നലിംഗം",
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
                # Kannada
                "ಪುರುಷ",
                "ಗಂಡು",
                "ಹುಡುಗ",
                "ತಂದೆ",
                # Telugu
                "పురుషుడు",
                "మగ",
                "అబ్బాయి",
                "తండ్రి",
                # Tamil
                "ஆண்",
                "தந்தை",
                "அப்பா",
                # Malayalam
                "പുരുഷൻ",
                "ആൺ",
                "പിതാവ്",
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
                "rythu",
                "vivasayi",
                "karshakan",
                "ರೈತ",
                "ಕೃಷಿಕ",
                "ಕೃಷಿ",
                "ವ್ಯವಸಾಯ",
                "రైతు",
                "రైతులు",
                "వ్యవసాయం",
                "விவசாயி",
                "உழவர்",
                "കർഷകൻ",
                "കർഷക",
                "കൃഷി",
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
                "వీధి వ్యాపారి",
                "தெருவோர வியாபாரி",
                "തെരുവ് കച്ചവടക്കാരൻ",
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
                "చేనేత",
                "దర్జీ",
                "நெசவாளர்",
                "தையல்காரர்",
                "നെയ്ത്തുകാരൻ",
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
                "maanavar",
                "ವಿದ್ಯಾರ್ಥಿ",
                "ಓದುತ್ತಿದ್ದೇನೆ",
                "ಕಾಲೇಜು",
                "విద్యార్థి",
                "చదువుతున్నాను",
                "மாணவர்",
                "மாணவி",
                "படிக்கிறேன்",
                "വിദ്യാർത്ഥി",
                "പഠിക്കുന്നു",
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
                "నిరుద్యోగి",
                "ఉద్యోగం లేదు",
                "வேலையில்லாத",
                "வேலையின்மை",
                "തൊഴിൽരഹിതൻ",
                "തൊഴിലില്ലാത്ത",
            ]
        ):
            return "unemployed"
        # Senior Citizen / Retired / Pensioner
        if any(
            x in t
            for x in [
                "senior citizen",
                "elderly",
                "pensioner",
                "retired",
                "old age",
                "ಹಿರಿಯ ನಾಗರಿಕ",
                "ನಿವೃತ್ತ",
                "ಪಿಂಚಣಿದಾರ",
                "ವೃದ್ಧ",
                "వృద్ధులు",
                "సీనియర్ సిటిజన్",
                "ముதியோர்",
                "ஓய்வூதியம்",
                "മുതിർന്ന പൗരൻ",
            ]
        ):
            return "senior_citizen"
        # Homemaker / Housewife
        if any(
            x in t
            for x in [
                "homemaker",
                "housewife",
                "home maker",
                "ಗೃಹಿಣಿ",
                "ಮನೆಗೆಲಸ",
                "గృహిణి",
                "இல்லத்தரசி",
                "வீട്ടമ്മ",
            ]
        ):
            return "homemaker"
        # Daily Wager / Laborer
        if any(
            x in t
            for x in [
                "daily wage",
                "daily wager",
                "coolie",
                "laborer",
                "labourer",
                "construction worker",
                "manual laborer",
                "ಕೂಲಿ",
                "ದಿನಗೂಲಿ",
                "ಕಾರ್ಮಿಕ",
            ]
        ):
            return "daily_wager"
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
