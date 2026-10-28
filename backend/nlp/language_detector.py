"""
Multilingual Language Detection Module.
Identifies English, Kannada, and code-mixed Kannada-English queries using Unicode script
analysis and vocabulary matching, providing confidence scores and graceful fallback.
"""
import re
from typing import Tuple

# Unicode range for Kannada script: U+0C80 to U+0CFF
KANNADA_REGEX = re.compile(r"[\u0C80-\u0CFF]")

# Common Kannada transliterated / code-mixed keywords
KANNADA_LATIN_KEYWORDS = {
    "yojane", "yojana", "raitha", "vidyarthi", "karnatakadalli", "karnataka",
    "bpl", "ration", "salada", "arji", "sarakara", "sarkara", "sahaya",
    "duddu", "hana", "nimma", "nanna", "beku", "ide", "illa", "ellinda",
    "yavudu", "yava", "houdu", "aadaaya", "vayassu", "kelsa", "unemployed",
    "sigutthe", "sigatte", "namaskara", "hege", "enu", "idu", "adu", "ge"
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
        kannada_latin_matches = sum(1 for w in words if w in KANNADA_LATIN_KEYWORDS)
        latin_word_count = len(words)

        # Decision Logic
        if kannada_char_ratio > 0.25:
            # Significant native Kannada script
            is_mixed = latin_word_count > 1
            confidence = min(1.0, 0.7 + kannada_char_ratio * 0.3)
            return "kn", confidence, is_mixed

        if kannada_char_ratio > 0.05:
            # Contains some Kannada script interspersed with English
            return "kn", 0.65, True

        if latin_word_count > 0 and (kannada_latin_matches >= 2 or (kannada_latin_matches / latin_word_count) >= 0.15):
            # Transliterated Kannada / code-mixed
            return "kn", 0.65, True

        # Default to English
        return "en", 0.90, False
