"""
Adaptive Follow-Up Question Generator.
Identifies the most informative unknown mandatory attribute across relevant candidate schemes
and constructs a targeted, context-aware clarification question in English, Kannada, Telugu, Tamil, or Malayalam.
"""
from typing import List, Optional, Tuple, Dict
from collections import Counter
from backend.schemas.eligibility import SchemeEligibilityResult, EligibilityStatus
from backend.schemas.user_profile import UserProfile

TARGETED_QUESTIONS = {
    "age": {
        "en": "To assess your eligibility accurately, could you please tell me your current age?",
        "kn": "ನಿಮ್ಮ ಅರ್ಹತೆಯನ್ನು ನಿಖರವಾಗಿ ಪರಿಶೀಲಿಸಲು, ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪ್ರಸ್ತುತ ವಯಸ್ಸು ಎಷ್ಟು ಎಂದು ತಿಳಿಸುವಿರಾ?",
        "te": "మీ అర్హతను ఖచ్చితంగా పరిశీలించడానికి, దయచేసి మీ ప్రస్తుత వయస్సు ఎంతనో తెలియజేస్తారా?",
        "ta": "உங்கள் தகுதியைத் துல்லியமாக மதிப்பிட, தயவுசெய்து உங்கள் தற்போதைய வயதைக் கூற முடியுமா?",
        "ml": "നിങ്ങളുടെ അർഹത കൃത്യമായി പരിശോധിക്കാൻ, ദയവായി നിങ്ങളുടെ നിലവിലെ പ്രായം എത്രയെന്ന് വ്യക്തമാക്കാമോ?",
    },
    "annual_income": {
        "en": "What is your approximate total annual family income in rupees?",
        "kn": "ನಿಮ್ಮ ಕುಟುಂಬದ ಒಟ್ಟು ವಾರ್ಷಿಕ ಆದಾಯ ಎಷ್ಟು ರೂಪಾಯಿ?",
        "te": "మీ కుటుంబ వార్షిక ఆదాయం సుమారుగా ఎన్ని రూపాయలు?",
        "ta": "உங்கள் குடும்பத்தின் தோராயமான ஆண்டு வருமானம் எத்தனை ரூபாய்?",
        "ml": "നിങ്ങളുടെ കുടുംബത്തിന്റെ ഏകദേശ വാർഷിക വരുമാനം എത്ര രൂപയാണ്?",
    },
    "state": {
        "en": "Which state do you currently reside in (e.g., Karnataka, Andhra Pradesh, Tamil Nadu, Kerala)?",
        "kn": "ನೀವು ಪ್ರಸ್ತುತ ಯಾವ ರಾಜ್ಯದಲ್ಲಿ ವಾಸಿಸುತ್ತಿದ್ದೀರಿ (ಉದಾ: ಕರ್ನಾಟಕ)?",
        "te": "మీరు ప్రస్తుతం ఏ రాష్ట్రంలో నివసిస్తున్నారు (ఉదా: ఆంధ్రప్రదేశ్, కర్ణాటక, తెలంగాణ)?",
        "ta": "நீங்கள் தற்போது எந்த மாநிலத்தில் வசிக்கிறீர்கள் (எ.கா. தமிழ்நாடு)?",
        "ml": "നിങ്ങൾ ഇപ്പോൾ ഏത് സംസ്ഥാനത്താണ് താമസിക്കുന്നത് (ഉദാ: കേരളം)?",
    },
    "occupation": {
        "en": "What is your primary occupation or current employment status (e.g., farmer, student, artisan, street vendor, unemployed)?",
        "kn": "ನಿಮ್ಮ ಮುಖ್ಯ ಉದ್ಯೋಗ ಅಥವಾ ಕಸುಬು ಯಾವುದು (ಉದಾ: ರೈತ, ವಿದ್ಯಾರ್ಥಿ, ಕುಶಲಕರ್ಮಿ, ಬೀದಿ ವ್ಯಾಪಾರಿ, ನಿರುದ್ಯೋಗಿ)?",
        "te": "మీ ప్రధాన వృత్తి లేదా ప్రస్తుత ఉద్యోగ స్థితి ఏమిటి (ఉదా: రైతు, విద్యార్థి, చేనేత/చేతివృత్తి, నిరుద్యోగి)?",
        "ta": "உங்கள் முதன்மை தொழில் அல்லது தற்போதைய வேலைவாய்ப்பு நிலை என்ன (எ.கா. விவசாயி, மாணவர், கைவினைஞர், வேலையில்லாதவர்)?",
        "ml": "നിങ്ങളുടെ പ്രധാന തൊഴിൽ അല്ലെങ്കിൽ നിലവിലെ തൊഴിൽ നില എന്താണ് (ഉദാ: കർഷകൻ, വിദ്യാർത്ഥി, കൈത്തൊഴിലാളി, തൊഴിൽരഹിതൻ)?",
    },
    "education_level": {
        "en": "What is your highest educational qualification (e.g., 10th pass, 12th/PUC, Graduate, Diploma)?",
        "kn": "ನಿಮ್ಮ ಶೈಕ್ಷಣಿಕ ಅರ್ಹತೆ ಏನು (ಉದಾ: 10ನೇ ತರಗತಿ, ಪಿಯುಸಿ, ಪದವಿ, ಡಿಪ್ಲೋಮಾ)?",
        "te": "మీ అత్యుನ್ನత విద್ಯಾ అర్హత ఏమిటి (ఉదా: 10వ తరగతి, ఇంటర్మీడియట్, డిగ్రీ, డిప్లొమా)?",
        "ta": "உங்கள் உச்சபட்ச கல்வித் தகுதி என்ன (எ.கா. 10 ஆம் வகுப்பு, 12 ஆம் வகுப்பு, பட்டப்படிப்பு, டிப்ளமோ)?",
        "ml": "നിങ്ങളുടെ ഉയർന്ന വിദ്യാഭ്യാസ യോഗ്യത എന്താണ് (ഉദാ: പത്താം ക്ലാസ്, പ്ലസ് ടു, ബിരുദം, ഡിപ്ലോമ)?",
    },
    "gender": {
        "en": "What is your gender (some schemes have targeted benefits for women or transgender persons)?",
        "kn": "ನಿಮ್ಮ ಲಿಂಗ ಯಾವುದು (ಕೆಲವು ಯೋಜನೆಗಳು ಮಹಿಳೆಯರಿಗೆ ಅಥವಾ ತೃತೀಯಲಿಂಗಿಗಳಿಗೆ ವಿಶೇಷ ಸೌಲಭ್ಯ ಹೊಂದಿವೆ)?",
        "te": "మీ లింగం ఏమిటి (కొన్ని పథకాలు మహిళలు లేదా ట్రాన్స్‌జెండర్లకు ప్రత్యేక ప్రయోజనాలు కలిగి ఉన్నాయి)?",
        "ta": "உங்கள் பாலினம் என்ன (சில திட்டங்கள் பெண்களுக்கு அல்லது திருநங்கைகளுக்கு சிறப்புப் பலன்களைக் கொண்டுள்ளன)?",
        "ml": "നിങ്ങളുടെ ലിംഗം ഏതാണ് (ചില പദ്ധതികൾ സ്ത്രീകൾക്കോ ട്രാൻസ്‌ജെൻഡർ വ്യക്തികൾക്കോ പ്രത്യേക ആനുകൂല്യങ്ങൾ നൽകുന്നു)?",
    },
    "social_category": {
        "en": "If you wish to share, what is your social category (SC, ST, OBC, Minority, General, or EWS)?",
        "kn": "ನೀವು ತಿಳಿಸಲು ಬಯಸಿದರೆ, ನಿಮ್ಮ ಸಾಮಾಜಿಕ ವರ್ಗ ಯಾವುದು (SC, ST, OBC, ಅಲ್ಪಸಂಖ್ಯಾತ, ಸಾಮಾನ್ಯ, ಅಥವಾ EWS)?",
        "te": "మీరు పంచుకోవాలనుకుంటే, మీ సామాజిక వర్గం ఏమిటి (SC, ST, BC, మైనారిటీ, జనరల్ లేదా EWS)?",
        "ta": "நீங்கள் தெரிவிக்க விரும்பினால், உங்கள் சமூகப் பிரிவு என்ன (SC, ST, BC/OBC, சிறுபான்மையினர், பொது அல்லது EWS)?",
        "ml": "നിങ്ങൾ വ്യക്തമാക്കാൻ ആഗ്രഹിക്കുന്നുവെങ്കിൽ, നിങ്ങളുടെ സാമൂഹിക വിഭാഗം ഏതാണ് (SC, ST, OBC, ന്യൂനപക്ഷം, ജനറൽ അല്ലെങ്കിൽ EWS)?",
    },
    "has_bpl_card": {
        "en": "Does your family possess a BPL (Below Poverty Line) or Antyodaya ration card?",
        "kn": "ನಿಮ್ಮ ಕುಟುಂಬವು ಬಿಪಿಎಲ್ (BPL) ಅಥವಾ ಅಂತ್ಯೋದಯ ಪಡಿತರ ಚೀಟಿ ಹೊಂದಿದೆಯೇ?",
        "te": "మీ కుటుంబానికి బిపిఎల్ (BPL), రైస్ కార్డ్ లేదా అంత్యోదయ రేషన్ కార్డు ఉందా?",
        "ta": "உங்கள் குடும்பத்தில் BPL (வறுமைக் கோட்டிற்கு கீழ்) அல்லது அந்தியோதயா குடும்ப அட்டை உள்ளதா?",
        "ml": "നിങ്ങളുടെ കുടുംബത്തിന് ബിപിഎൽ (BPL) അല്ലെങ്കിൽ അന്ത്യോദയ റേഷൻ കാർഡ് ഉണ്ടോ?",
    },
    "is_student": {
        "en": "Are you currently enrolled as an active student in school or college?",
        "kn": "ನೀವು ಪ್ರಸ್ತುತ ಶಾಲೆ ಅಥವಾ ಕಾಲೇಜಿನಲ್ಲಿ ಕಲಿಯುತ್ತಿರುವ ವಿದ್ಯಾರ್ಥಿಯೇ?",
        "te": "మీరు ప్రస్తుతం పాఠశాల లేదా కళಾಶాలలో విద్యార్థిగా చదువుతున్నారా?",
        "ta": "நீங்கள் தற்போது பள்ளி அல்லது கல்லூரியில் படிக்கும் மாணவரா?",
        "ml": "നിങ്ങൾ ഇപ്പോൾ സ്കൂളിലോ കോളേജിലോ പഠിക്കുന്ന വിദ്യാർത്ഥിയാണോ?",
    },
    "land_ownership_ha": {
        "en": "Do you own agricultural land, and if so, approximately how many acres or hectares?",
        "kn": "ನಿಮ್ಮ ಹೆಸರಿನಲ್ಲಿ ಕೃಷಿ ಭೂಮಿ ಇದೆಯೇ, ಇದ್ದರೆ ಸುಮಾರು ಎಷ್ಟು ಎಕರೆ ಅಥವಾ ಹೆಕ್ಟೇರ್?",
        "te": "మీ పేరున వ్యవసాయ భూమి ఉందా, ఉంటే సుమారు ఎన్ని ఎకరాలు లేదా హెక్టార్లు?",
        "ta": "உங்கள் பெயரில் விவசாய நிலம் உள்ளதா, இருந்தால் தோராயமாக எத்தனை ஏக்கர் அல்லது ஹெக்டேர்?",
        "ml": "നിങ്ങളുടെ പേരിൽ കൃഷിഭൂമിയുണ്ടോ, ഉണ്ടെങ്കിൽ ഏകദേശം എത്ര ഏക്കർ അല്ലെങ്കിൽ ഹെക്ടർ?",
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

        lang_code = language if language in ["kn", "te", "ta", "ml"] else "en"
        question_data = TARGETED_QUESTIONS.get(most_impactful_attr)
        if question_data:
            question_text = question_data.get(lang_code, question_data["en"])
        else:
            fallback_prompts = {
                "en": f"Could you please specify your {most_impactful_attr.replace('_', ' ')}?",
                "kn": f"ದಯವಿಟ್ಟು ನಿಮ್ಮ {most_impactful_attr} ವಿವರಗಳನ್ನು ತಿಳಿಸುವಿರಾ?",
                "te": f"దయచేసి మీ {most_impactful_attr} వివరాలను తెలియజేస్తారా?",
                "ta": f"தயவுசெய்து உங்கள் {most_impactful_attr} விவரங்களைக் குறிப்பிட முடியுமா?",
                "ml": f"ദയവായി നിങ്ങളുടെ {most_impactful_attr} വിവരങ്ങൾ വ്യക്തമാക്കാമോ?",
            }
            question_text = fallback_prompts.get(lang_code, fallback_prompts["en"])

        return question_text, most_impactful_attr
