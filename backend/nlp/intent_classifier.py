"""
Intent Classification Module.
Classifies user queries into core conversational intents for both English and Kannada,
using robust rule-based pattern matching with confidence scoring.
"""
import re
from typing import Tuple, Dict, Any

INTENT_PATTERNS = {
    "query_application_process": [
        r"\bhow (?:can i|do i|to) apply\b",
        r"\bwhere (?:can i|to) apply\b",
        r"\bapplication process\b",
        r"\bprocedure\b",
        r"\bregistration steps\b",
        r"ಹೇಗೆ ಅರ್ಜಿ",
        r"ಎಲ್ಲಿ ಅರ್ಜಿ",
        r"ವಿಧಾನ",
        r"ನೋಂದಣಿ ಹೇಗೆ",
    ],
    "query_benefits": [
        r"\bbenefit[s]?\b",
        r"\bhow much (?:money|amount|pension|grant)\b",
        r"\bwhat do i get\b",
        r"\bassistance\b",
        r"ಲಾಭಗಳು",
        r"ಪ್ರಯೋಜನ",
        r"ಎಷ್ಟು ಹಣ",
        r"ಸಹಾಯಧನ",
        r"ಖಾತೆಗೆ ಎಷ್ಟು",
    ],
    "query_documents": [
        r"\bdocument[s]?\b",
        r"\bdoc[s]?\b",
        r"\bpapers\b",
        r"\bcertificate[s]?\b",
        r"\bwhat (?:is|are) needed\b",
        r"ದಾಖಲೆಗಳು",
        r"ದಾಖಲಾತಿ",
        r"ಸರ್ಟಿಫಿಕೇಟ್",
        r"ಏನು ಬೇಕು",
    ],
    "check_eligibility": [
        r"\beligib(?:le|ility)\b",
        r"\bam i eligible\b",
        r"\bcan i (?:get|apply|avail)\b",
        r"\bqualif(?:y|ication)\b",
        r"ಅರ್ಹತೆ",
        r"ಅರ್ಹನೇ",
        r"ಸಿಗುತ್ತದೆಯೇ",
        r"ಪಡೆಯಬಹುದೇ",
        r"ಅರ್ಜಿ ಸಲ್ಲಿಸಬಹುದೇ",
    ],
    "query_official_link": [
        r"\bwebsite\b",
        r"\blink\b",
        r"\bportal\b",
        r"\bofficial site\b",
        r"\burl\b",
        r"ವೆಬ್‌ಸೈಟ್",
        r"ಲಿಂಕ್",
        r"ಪೋರ್ಟಲ್",
    ],
    "compare_schemes": [
        r"\bcompare\b",
        r"\bdifference between\b",
        r"\bvs\b",
        r"\bwhich is better\b",
        r"ಹೋಲಿಕೆ",
        r"ವ್ಯತ್ಯಾಸ",
    ],
    "find_alternatives": [
        r"\balternative[s]?\b",
        r"\bnot eligible\b",
        r"\brejected\b",
        r"\bfailed\b",
        r"\bany other scheme\b",
        r"\bwhat else\b",
        r"ಬೇರೆ ಯೋಜನೆ",
        r"ಪರ್ಯಾಯ",
        r"ಅರ್ಹನಲ್ಲದಿದ್ದರೆ",
        r"ಬೇರೆ ಏನು",
    ],
    "answer_follow_up": [
        r"^(?:my age is|age|i am|income|salary|caste|category|state|yes|no|houdu|illa)\b",
        r"^\d+\s*(?:years?|yrs?|ವಯಸ್ಸು|ವರ್ಷ)?$",
        r"^[0-9.]+\s*(?:lakh|thousand|cr|rs|inr|₹|ಸಾವಿರ|ಲಕ್ಷ)?$",
        r"^(?:karnataka|delhi|farmer|student|female|male|sc|st|obc|general)$",
    ],
    "recommend_schemes": [
        r"\brecommend\b",
        r"\bsuggest\b",
        r"\bfind schemes\b",
        r"\bwhat schemes\b",
        r"\bgovernment scheme[s]?\b",
        r"\bwelfare\b",
        r"ಯೋಜನೆಗಳು",
        r"ಯಾವ ಯೋಜನೆ",
        r"ಸರ್ಕಾರಿ ಯೋಜನೆ",
        r"ತಿಳಿಸಿ",
    ],
}


class IntentClassifier:
    @classmethod
    def classify(cls, text: str) -> Tuple[str, float]:
        """
        Classifies user query into an intent.
        Returns:
            Tuple of (intent_name, confidence)
        """
        if not text or not text.strip():
            return "recommend_schemes", 0.5

        t = text.strip().lower()

        # Check each pattern set
        for intent, patterns in INTENT_PATTERNS.items():
            for p in patterns:
                if re.search(p, t, re.IGNORECASE):
                    return intent, 0.85

        # Default fallback: recommend schemes
        return "recommend_schemes", 0.60
