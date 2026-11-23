"""
Multilingual Language Detection Module.
Identifies English, Kannada, Telugu, Tamil, Malayalam, and code-mixed queries using Unicode script
analysis and vocabulary matching, providing confidence scores and graceful fallback.
"""
import re
from typing import Tuple

# Unicode regexes for Dravidian scripts
SCRIPTS_MAP = {
    "kn": re.compile(r"[\u0C80-\u0CFF]"),  # Kannada
    "te": re.compile(r"[\u0C00-\u0C7F]"),  # Telugu
    "ta": re.compile(r"[\u0B80-\u0BFF]"),  # Tamil
    "ml": re.compile(r"[\u0D00-\u0D7F]"),  # Malayalam
}

# Distinctive transliterated / grammatical keywords
LATIN_KEYWORDS = {
    "kn": {
        "yojane", "yojana", "raitha", "vidyarthi", "karnatakadalli", "alli",
        "salada", "arji", "sarakara", "sarkara", "sahaya",
        "duddu", "hana", "nimma", "nanna", "beku", "ide", "illa", "ellinda",
        "yavudu", "yava", "houdu", "aadaaya", "vayassu", "kelsa", "nirudyogi",
        "sigutthe", "sigatte", "namaskara", "hege", "enu", "idu", "adu", "ge"
    },
    "te": {
        "padhakam", "padhakalu", "rythu", "raithu", "vidyarthi", "andhra", "telangana",
        "aadaayam", "aadhayam", "vayassu", "naaku", "nenu", "maaku", "kaavali",
        "dabbulu", "dabbu", "sahayam", "lekapothe", "undi", "ledu", "ela", "emi",
        "darakhasthu", "namaskaram", "unnaru", "unnadi", "yojana"
    },
    "ta": {
        "thittam", "thittangal", "ulavar", "vivasayi", "maanavar", "maanavi", "tamilnadu",
        "varumaanam", "vayathu", "vayasu", "naan", "enakku", "engalukku", "vendum", "venum",
        "udhavi", "panam", "kaasu", "illai", "irukku", "irukka", "irukkirathu", "eppadi", "enna",
        "vanakkam", "solleenga", "tamil", "nadu"
    },
    "ml": {
        "padhathi", "padhadhi", "karshakan", "vidyarthi", "keralathil", "keralam",
        "varumaanam", "vayassu", "vayas", "njan", "enikku", "njangal", "venam", "sahayam",
        "panam", "kaashu", "illa", "undu", "kittum", "enganeyanu", "enthanu", "namaskaram",
        "parayu", "kerala"
    }
}

# English stop words to disambiguate primarily English sentences
COMMON_ENGLISH_WORDS = {
    "i", "am", "a", "an", "the", "in", "of", "from", "and", "have", "with",
    "year", "old", "woman", "man", "annual", "income", "card", "family",
    "farmer", "student", "scheme", "apply", "eligible", "pension"
}


class LanguageDetector:
    @staticmethod
    def detect(text: str) -> Tuple[str, float, bool]:
        """
        Detects primary language of text.
        Returns:
            Tuple of (language_code ['en', 'kn', 'te', 'ta', 'ml'], confidence [0.0 - 1.0], is_code_mixed [bool])
        """
        if not text or not text.strip():
            return "en", 0.5, False

        clean_text = text.strip()
        total_chars = len(clean_text)
        words = re.findall(r"\b[a-zA-Z]+\b", clean_text.lower())
        latin_word_count = len(words)

        # 1. Check Native Indic Unicode Scripts
        script_counts = {}
        for lang_code, pattern in SCRIPTS_MAP.items():
            count = len(pattern.findall(clean_text))
            if count > 0:
                script_counts[lang_code] = count

        if script_counts:
            dominant_lang, dominant_count = max(script_counts.items(), key=lambda x: x[1])
            ratio = dominant_count / total_chars if total_chars > 0 else 0.0

            if ratio > 0.20:
                is_mixed = latin_word_count > 1
                confidence = min(1.0, 0.70 + ratio * 0.30)
                return dominant_lang, confidence, is_mixed

            if ratio > 0.04:
                return dominant_lang, 0.65, True

        # 2. Check for Latin / Transliterated Keywords
        english_matches = sum(1 for w in words if w in COMMON_ENGLISH_WORDS)

        best_latin_lang = None
        best_latin_matches = 0

        for lang_code, kw_set in LATIN_KEYWORDS.items():
            matches = sum(1 for w in words if w in kw_set)
            if matches > best_latin_matches:
                best_latin_matches = matches
                best_latin_lang = lang_code

        # If predominantly English
        if english_matches >= 3 and best_latin_matches < 2:
            return "en", 0.92, False

        if latin_word_count > 0 and best_latin_lang:
            ratio = best_latin_matches / latin_word_count
            if (best_latin_matches >= 2 and ratio >= 0.15) or ratio >= 0.25:
                return best_latin_lang, 0.65, True

        # Default to English
        return "en", 0.90, False
