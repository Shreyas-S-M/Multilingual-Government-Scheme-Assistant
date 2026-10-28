"""
Adaptive Follow-Up Question Generator.
Identifies the most informative unknown mandatory attribute across relevant candidate schemes
and constructs a targeted, context-aware clarification question in English or Kannada.
"""
from typing import List, Optional, Tuple, Dict
from collections import Counter
from backend.schemas.eligibility import SchemeEligibilityResult, EligibilityStatus
from backend.schemas.user_profile import UserProfile

TARGETED_QUESTIONS = {
    "age": {
        "en": "To assess your eligibility accurately, could you please tell me your current age?",
        "kn": "ನಿಮ್ಮ ಅರ್ಹತೆಯನ್ನು ನಿಖರವಾಗಿ ಪರಿಶೀಲಿಸಲು, ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪ್ರಸ್ತುತ ವಯಸ್ಸು ಎಷ್ಟು ಎಂದು ತಿಳಿಸುವಿರಾ?",
    },
    "annual_income": {
        "en": "What is your approximate total annual family income in rupees?",
        "kn": "ನಿಮ್ಮ ಕುಟುಂಬದ ಒಟ್ಟು ವಾರ್ಷಿಕ ಆದಾಯ ಎಷ್ಟು ರೂಪಾಯಿ?",
    },
    "state": {
        "en": "Which state do you currently reside in (e.g., Karnataka)?",
        "kn": "ನೀವು ಪ್ರಸ್ತುತ ಯಾವ ರಾಜ್ಯದಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೀರಿ (ಉದಾ: ಕರ್ನಾಟಕ)?",
    },
    "occupation": {
        "en": "What is your primary occupation or current employment status (e.g., farmer, student, artisan, street vendor, unemployed)?",
        "kn": "ನಿಮ್ಮ ಮುಖ್ಯ ಉದ್ಯೋಗ ಅಥವಾ ಕಸುಬು ಯಾವುದು (ಉದಾ: ರೈತ, ವಿದ್ಯಾರ್ಥಿ, ಕುಶಲಕರ್ಮಿ, ಬೀದಿ ವ್ಯಾಪಾರಿ, ನಿರುದ್ಯೋಗಿ)?",
    },
    "education_level": {
        "en": "What is your highest educational qualification (e.g., 10th pass, 12th/PUC, Graduate, Diploma)?",
        "kn": "ನಿಮ್ಮ ಶೈಕ್ಷಣಿಕ ಅರ್ಹತೆ ಏನು (ಉದಾ: 10ನೇ ತರಗತಿ, ಪಿಯುಸಿ, ಪದವಿ, ಡಿಪ್ಲೋಮಾ)?",
    },
    "gender": {
        "en": "What is your gender (some schemes have targeted benefits for women or transgender persons)?",
        "kn": "ನಿಮ್ಮ ಲಿಂಗ ಯಾವುದು (ಕೆಲವು ಯೋಜನೆಗಳು ಮಹಿಳೆಯರಿಗೆ ಅಥವಾ ತೃತೀಯಲಿಂಗಿಗಳಿಗೆ ವಿಶೇಷ ಸೌಲಭ್ಯ ಹೊಂದಿವೆ)?",
    },
    "social_category": {
        "en": "If you wish to share, what is your social category (SC, ST, OBC, Minority, General, or EWS)?",
        "kn": "ನೀವು ತಿಳಿಸಲು ಬಯಸಿದರೆ, ನಿಮ್ಮ ಸಾಮಾಜಿಕ ವರ್ಗ ಯಾವುದು (SC, ST, OBC, ಅಲ್ಪಸಂಖ್ಯಾತ, ಸಾಮಾನ್ಯ, ಅಥವಾ EWS)?",
    },
    "has_bpl_card": {
        "en": "Does your family possess a BPL (Below Poverty Line) or Antyodaya ration card?",
        "kn": "ನಿಮ್ಮ ಕುಟುಂಬವು ಬಿಪಿಎಲ್ (BPL) ಅಥವಾ ಅಂತ್ಯೋದಯ ಪಡಿತರ ಚೀಟಿ ಹೊಂದಿದೆಯೇ?",
    },
    "is_student": {
        "en": "Are you currently enrolled as an active student in school or college?",
        "kn": "ನೀವು ಪ್ರಸ್ತುತ ಶಾಲೆ ಅಥವಾ ಕಾಲೇಜಿನಲ್ಲಿ ಕಲಿಯುತ್ತಿರುವ ವಿದ್ಯಾರ್ಥಿಯೇ?",
    },
    "land_ownership_ha": {
        "en": "Do you own agricultural land, and if so, approximately how many acres or hectares?",
        "kn": "ನಿಮ್ಮ ಹೆಸರಿನಲ್ಲಿ ಕೃಷಿ ಭೂಮಿ ಇದೆಯೇ, ಇದ್ದರೆ ಸುಮಾರು ಎಷ್ಟು ಎಕರೆ ಅಥವಾ ಹೆಕ್ಟೇರ್?",
    },
}


class AdaptiveQuestioner:
    @classmethod
    def select_next_question(
        cls,
        candidate_results: List[SchemeEligibilityResult],
        profile: UserProfile,
        language: str = "en",
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Determines the single most impactful follow-up question.
        Returns:
            Tuple of (question_text, target_attribute) or (None, None) if no further questions needed.
        """
        # Find all unknown mandatory attributes among schemes that haven't outright failed
        viable_schemes = [
            r for r in candidate_results if r.overall_status == EligibilityStatus.UNKNOWN
        ]

        if not viable_schemes:
            return None, None

        missing_counter = Counter()
        for scheme_res in viable_schemes:
            for attr in scheme_res.missing_attributes:
                # Only consider attributes currently unknown in user profile
                if getattr(profile, attr, None) is None:
                    missing_counter[attr] += 1

        if not missing_counter:
            return None, None

        # Pick the attribute that resolves the largest number of candidate schemes
        most_impactful_attr, count = missing_counter.most_common(1)[0]

        lang_code = "kn" if language == "kn" else "en"
        question_data = TARGETED_QUESTIONS.get(most_impactful_attr)
        if question_data:
            question_text = question_data.get(lang_code, question_data["en"])
        else:
            question_text = (
                f"Could you please specify your {most_impactful_attr.replace('_', ' ')}?"
                if lang_code == "en"
                else f"ದಯವಿಟ್ಟು ನಿಮ್ಮ {most_impactful_attr} ವಿವರಗಳನ್ನು ತಿಳಿಸುವಿರಾ?"
            )

        return question_text, most_impactful_attr
