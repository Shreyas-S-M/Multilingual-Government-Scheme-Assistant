"""
Multilingual Language Detection Module.
Identifies English, Kannada, and code-mixed Kannada-English queries using Unicode script
analysis and vocabulary matching, providing confidence scores and graceful fallback.
"""
import re
from typing import Tuple

# Unicode range for Kannada script: U+0C80 to U+0CFF
KANNADA_REGEX = re.compile(r"[\u0C80-\u0CFF]")

# Distinctive Kannada transliterated / grammatical keywords
KANNADA_LATIN_KEYWORDS = {
    "yojane", "yojana", "raitha", "vidyarthi", "karnatakadalli", "alli",
    "salada", "arji", "sarakara", "sarkara", "sahaya",
    "duddu", "hana", "nimma", "nanna", "beku", "ide", "illa", "ellinda",
    "yavudu", "yava", "houdu", "aadaaya", "vayassu", "kelsa", "nirudyogi",
    "sigutthe", "sigatte", "namaskara", "hege", "enu", "idu", "adu", "ge"
}

# English stop words to disambiguate primarily English sentences
COMMON_ENGLISH_WORDS = {
    "i", "am", "a", "an", "the", "in", "of", "from", "and", "have", "with",
    "year", "old", "woman", "man", "annual", "income", "card", "family"
}


class LanguageDetector:
    @staticmethod
    def detect(text: str) -> Tuple[str, float, bool]:
        """
        Detects primary language of text.
        Returns:
            Tuple of (language_code ['en', 'kn'], confidence [0.0 - 1.0], is_code_mixed [bool])
        """
        if not text or not text.strip():
            return "en", 0.5, False

        clean_text = text.strip()
        total_chars = len(clean_text)
        
        # Count Kannada Unicode characters
        kannada_chars = len(KANNADA_REGEX.findall(clean_text))
        kannada_char_ratio = kannada_chars / total_chars if total_chars > 0 else 0.0

        # Check for Latin Kannada words
        words = re.findall(r"\b[a-zA-Z]+\b", clean_text.lower())
        latin_word_count = len(words)
        kannada_latin_matches = sum(1 for w in words if w in KANNADA_LATIN_KEYWORDS)
        english_matches = sum(1 for w in words if w in COMMON_ENGLISH_WORDS)

        # Decision Logic
        if kannada_char_ratio > 0.25:
            # Significant native Kannada script
            is_mixed = latin_word_count > 1
            confidence = min(1.0, 0.7 + kannada_char_ratio * 0.3)
            return "kn", confidence, is_mixed

        if kannada_char_ratio > 0.05:
            # Contains some Kannada script interspersed with English
            return "kn", 0.65, True

        # Check if predominantly English
        if english_matches >= 3 and kannada_latin_matches < 2:
            return "en", 0.92, False

        if latin_word_count > 0:
            ratio = kannada_latin_matches / latin_word_count
            if (kannada_latin_matches >= 2 and ratio >= 0.15) or ratio >= 0.25:
                # Transliterated Kannada / code-mixed
                return "kn", 0.65, True

        # Default to English
        return "en", 0.90, False
