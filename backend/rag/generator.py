"""
Grounded Response Generation Service.
Implements provider-independent generation with an authoritative, deterministic template fallback.
Enforces that eligibility statuses (PASS, FAIL, UNKNOWN) are strictly preserved from the rule engine.
Supports English, Kannada, Telugu, Tamil, and Malayalam.
"""
from typing import List, Dict, Any, Optional
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from backend.core.config import settings
from backend.schemas.eligibility import SchemeEligibilityResult, EligibilityStatus
from backend.schemas.user_profile import UserProfile
from backend.rag.context_builder import RAGContextBuilder
from backend.core.logging import logger

LANGUAGE_NAMES = {
    "en": "English",
    "kn": "Kannada",
    "te": "Telugu",
    "ta": "Tamil",
    "ml": "Malayalam",
}

LOCALIZED_TEXTS = {
    "en": {
        "intro_title": "### Personalized Government Scheme Assessment\n",
        "intro_desc": "Based on the details provided in your query, here is your transparent eligibility evaluation:\n",
        "no_match": "No specific schemes matched your exact profile yet. Please provide more details such as your occupation, annual family income, or state of residence.",
        "eligible_title": "#### ✅ Schemes You Appear Eligible For",
        "unknown_title": "#### ℹ️ Schemes Requiring More Information",
        "failed_title": "#### ❌ Schemes You Do Not Currently Qualify For",
        "near_miss_title": "#### 💡 Alternative Scheme Options (Near-Miss Recommendations)",
        "benefits_label": "Benefits",
        "reason_label": "Reason",
        "docs_label": "Required Documents",
        "portal_label": "Official Portal",
        "missing_label": "Missing Attributes",
        "why_alt_label": "Why this alternative?",
        "follow_up_header": "\n> **🎯 Targeted Follow-Up Question:**",
        "disclaimer": "\n*Note: Scheme recommendations are for informational discovery only. Official eligibility determinations and benefit approvals are made solely by the respective government authorities.*",
    },
    "kn": {
        "intro_title": "### ನಿಮ್ಮ ವಿವರಗಳಿಗೆ ಸಂಬಂಧಿಸಿದ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ವಿಶ್ಲೇಷಣೆ\n",
        "intro_desc": "ನೀವು ಒದಗಿಸಿದ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ಕೆಳಗಿನ ಯೋಜನೆಗಳ ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಲಾಗಿದೆ:\n",
        "no_match": "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಹೊಂದಿಕೆಯಾಗುವ ಯಾವುದೇ ನೇರ ಯೋಜನೆಗಳು ಸದ್ಯಕ್ಕೆ ಪತ್ತೆಯಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಯಸ್ಸು, ವೃತ್ತಿ, ಅಥವಾ ಆದಾಯದ ಬಗ್ಗೆ ಹೆಚ್ಚಿನ ವಿವರಗಳನ್ನು ನೀಡಿ.",
        "eligible_title": "#### ✅ ನೀವು ಅರ್ಹತೆ ಹೊಂದಿರುವ ಯೋಜನೆಗಳು (Appears Eligible)",
        "unknown_title": "#### ℹ️ ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಅಗತ್ಯವಿರುವ ಯೋಜನೆಗಳು (Information Needed)",
        "failed_title": "#### ❌ ಪ್ರಸ್ತುತ ಅರ್ಹತೆ ಹೊಂದಿರದ ಯೋಜನೆಗಳು (Ineligible)",
        "near_miss_title": "#### 💡 ಪರ್ಯಾಯ ಯೋಜನೆಗಳ ಶಿಫಾರಸು (Alternative Scheme Options)",
        "benefits_label": "ಪ್ರಯೋಜನಗಳು",
        "reason_label": "ಕಾರಣ",
        "docs_label": "ಅಗತ್ಯ ದಾಖಲೆಗಳು",
        "portal_label": "ಅಧಿಕೃತ ಪೋರ್ಟಲ್",
        "missing_label": "ಅಪೂರ್ಣ ವಿವರಗಳು",
        "why_alt_label": "ಈ ಪರ್ಯಾಯ ಏಕೆ?",
        "follow_up_header": "\n> **🎯 ಮುಂದುವರಿದ ಪ್ರಶ್ನೆ (Follow-Up Question):**",
        "disclaimer": "\n*ಗಮನಿಸಿ: ಈ ಶಿಫಾರಸುಗಳು ಮಾಹಿತಿ ಉದ್ದೇಶಗಳಿಗಾಗಿ ಮಾತ್ರ. ಅಂತಿಮ ಅರ್ಹತೆ ಮತ್ತು ಅರ್ಜಿ ಅನುಮೋದನೆಯನ್ನು ಸಂಬಂಧಪಟ್ಟ ಸರ್ಕಾರಿ ಪ್ರಾಧಿಕಾರವೇ ನಿರ್ಧರಿಸುತ್ತದೆ.*",
    },
    "te": {
        "intro_title": "### మీ వివరాల ఆధారంగా ప్రభుత్వ పథకాల మూల్యాంకనం\n",
        "intro_desc": "మీరు అందించిన సమాచారం ఆధారంగా క్రింది పథకాల అర్హతను పరిశీలించడమైనది:\n",
        "no_match": "మీ ప్రొఫైల్‌కు సరిపోలే నిర్దిష్ట పథకాలు ఏవీ ఇంకా కనుగొనబడలేదు. దయచేసి మీ వయస్సు, వృత్తి లేదా వార్షిక ఆదాయం వంటి మరిన్ని వివరాలను అందించండి.",
        "eligible_title": "#### ✅ మీరు అర్హత కలిగిన పథకాలు (Appears Eligible)",
        "unknown_title": "#### ℹ️ మరింత సమాచారం అవసరమైన పథకాలు (Information Needed)",
        "failed_title": "#### ❌ ప్రస్తుతం మీకు అర్హత లేని పథకాలు (Ineligible)",
        "near_miss_title": "#### 💡 ప్రత్యామ్నాయ పథకాల సిఫార్సు (Alternative Scheme Options)",
        "benefits_label": "ప్రయోజనాలు",
        "reason_label": "కారణం",
        "docs_label": "కావలసిన పత్రాలు",
        "portal_label": "అధికారిక పోర్టల్",
        "missing_label": "అసంపూర్ణ వివరాలు",
        "why_alt_label": "ఈ ప్రత్యామ్నాయం ఎందుకు?",
        "follow_up_header": "\n> **🎯 తదుపరి ప్రశ్న (Follow-Up Question):**",
        "disclaimer": "\n*గమనిక: పథకాల సిఫార్సులు కేవలం సమాచార అవగాహన కోసం మాత్రమే. తుది అర్హత మరియు దరఖాస్తు ఆమోదం సంబంధిత ప్రభుత్వ విభాగం ద్వారానే నిర్ణయించబడుతుంది.*",
    },
    "ta": {
        "intro_title": "### உங்கள் விவரங்களின் அடிப்படையிலான அரசு நலத்திட்ட மதிப்பீடு\n",
        "intro_desc": "நீங்கள் வழங்கிய தகவல்களின் அடிப்படையில் கீழ்வரும் திட்டங்களுக்கான தகுதி மதிப்பீடு செய்யப்பட்டுள்ளது:\n",
        "no_match": "உங்கள் விவரங்களுடன் பொருந்தும் திட்டங்கள் எதுவும் தற்போது கண்டறியப்படவில்லை. தயவுசெய்து உங்கள் வயது, தொழில் அல்லது குடும்ப வருமானம் பற்றிய கூடுதல் விவரங்களை வழங்கவும்.",
        "eligible_title": "#### ✅ நீங்கள் தகுதி பெற்றுள்ள திட்டங்கள் (Appears Eligible)",
        "unknown_title": "#### ℹ️ கூடுதல் தகவல் தேவைப்படும் திட்டங்கள் (Information Needed)",
        "failed_title": "#### ❌ நீங்கள் தற்போது தகுதி பெறாத திட்டங்கள் (Ineligible)",
        "near_miss_title": "#### 💡 மாற்றுத் திட்டப் பரிந்துரைகள் (Alternative Scheme Options)",
        "benefits_label": "நன்மைகள்",
        "reason_label": "காரணம்",
        "docs_label": "தேவையான ஆவணங்கள்",
        "portal_label": "அதிகாரப்பூர்வ தளம்",
        "missing_label": "விடுபட்ட விவரங்கள்",
        "why_alt_label": "இந்த மாற்று ஏன்?",
        "follow_up_header": "\n> **🎯 தொடர் கேள்வி (Follow-Up Question):**",
        "disclaimer": "\n*குறிப்பு: இந்தத் திட்டப் பரிந்துரைகள் தகவல் அறிவதற்காக மட்டுமே. அதிகாரப்பூர்வ தகுதி மற்றும் விண்ணப்ப ஒப்புதல் சம்பந்தப்பட்ட அரசுத் துறையினரால் மட்டுமே தீர்மானிக்கப்படும்.*",
    },
    "ml": {
        "intro_title": "### നിങ്ങളുടെ വിവരങ്ങളെ അടിസ്ഥാനമാക്കിയുള്ള സർക്കാർ പദ്ധതി വിലയിരുത്തൽ\n",
        "intro_desc": "നിങ്ങൾ നൽകിയ വിവരങ്ങളുടെ അടിസ്ഥാനത്തിൽ താഴെ പറയുന്ന പദ്ധതികളുടെ അർഹത പരിശോധിച്ചിരിക്കുന്നു:\n",
        "no_match": "നിങ്ങളുടെ പ്രൊഫൈലുമായി പൊരുത്തപ്പെടുന്ന നിർദ്ദിഷ്ട പദ്ധതികളൊന്നും ഇതുവരെ കണ്ടെത്തിയില്ല. ദയവായി നിങ്ങളുടെ പ്രായം, തൊഴിൽ അല്ലെങ്കിൽ വാർഷിക വരുമാനം എന്നിവ വ്യക്തമാക്കുക.",
        "eligible_title": "#### ✅ നിങ്ങൾക്ക് അർഹതയുള്ള പദ്ധതികൾ (Appears Eligible)",
        "unknown_title": "#### ℹ️ കൂടുതൽ വിവരങ്ങൾ ആവശ്യമുള്ള പദ്ധതികൾ (Information Needed)",
        "failed_title": "#### ❌ നിലവിൽ നിങ്ങൾക്ക് അർഹതയില്ലാത്ത പദ്ധതികൾ (Ineligible)",
        "near_miss_title": "#### 💡 ഇതര പദ്ധതി നിർദ്ദേശങ്ങൾ (Alternative Scheme Options)",
        "benefits_label": "ആനുകൂല്യങ്ങൾ",
        "reason_label": "കാരണം",
        "docs_label": "ആവശ്യമായ രേഖകൾ",
        "portal_label": "ഔദ്യോഗിക പോർട്ടൽ",
        "missing_label": "ലഭ്യമല്ലാത്ത വിവരങ്ങൾ",
        "why_alt_label": "എന്തുകൊണ്ട് ഈ ഇതരമാർഗ്ഗം?",
        "follow_up_header": "\n> **🎯 തുടർ ചോദ്യം (Follow-Up Question):**",
        "disclaimer": "\n*ശ്രദ്ധിക്കുക: ഈ പദ്ധതി നിർദ്ദേശങ്ങൾ വിവര ആവശ്യങ്ങൾക്ക് മാത്രമുള്ളതാണ്. ഔദ്യോഗിക അർഹതയും അപേക്ഷാ അംഗീകാരവും ബന്ധപ്പെട്ട സർക്കാർ അധികാരികൾ മാത്രമാണ് തീരുമാനിക്കുന്നത്.*",
    },
}


class ResponseGenerator:
    def __init__(self, provider: str = None):
        self.provider = provider or settings.LLM_PROVIDER
        self.last_used_llm = False

    def generate_response(
        self,
        query: str,
        profile: UserProfile,
        recommended_schemes: List[SchemeEligibilityResult],
        schemes_data_map: Dict[str, Any],
        language: str = "en",
        follow_up_question: Optional[str] = None,
        near_misses: Optional[List[SchemeEligibilityResult]] = None,
    ) -> str:
        """
        Synthesizes grounded conversational response in English, Kannada, Telugu, Tamil, or Malayalam.
        Uses deterministic generation by default or if external LLM provider fails/is unconfigured.
        """
        self.last_used_llm = False
        lang_code = language if language in LOCALIZED_TEXTS else "en"

        if self.provider == "ollama":
            try:
                answer = self._generate_ollama(
                    query, profile, recommended_schemes, schemes_data_map, lang_code, follow_up_question, near_misses
                )
                self.last_used_llm = True
                return answer
            except Exception as e:
                logger.warning(f"Ollama generation failed ({e}), falling back to deterministic response.")

        elif self.provider == "gemini" and settings.LLM_API_KEY:
            try:
                answer = self._generate_gemini(
                    query, profile, recommended_schemes, schemes_data_map, lang_code, follow_up_question, near_misses
                )
                self.last_used_llm = True
                return answer
            except Exception as e:
                logger.warning(f"Gemini generation failed ({e}), falling back to deterministic response.")

        # Authoritative deterministic generation
        return self._generate_deterministic(
            query, profile, recommended_schemes, schemes_data_map, lang_code, follow_up_question, near_misses
        )

    def _generate_deterministic(
        self,
        query: str,
        profile: UserProfile,
        recommended_schemes: List[SchemeEligibilityResult],
        schemes_data_map: Dict[str, Any],
        language: str = "en",
        follow_up_question: Optional[str] = None,
        near_misses: Optional[List[SchemeEligibilityResult]] = None,
    ) -> str:
        """Assembles structured, verifiable markdown response from verified records in the requested language."""
        lang_code = language if language in LOCALIZED_TEXTS else "en"
        loc = LOCALIZED_TEXTS[lang_code]
        lines = []

        # Intro
        lines.append(loc["intro_title"])
        lines.append(loc["intro_desc"])

        if not recommended_schemes:
            lines.append(loc["no_match"])
            return "\n".join(lines)

        # 1. Eligible schemes (PASS)
        eligible = [r for r in recommended_schemes if r.overall_status == EligibilityStatus.PASS]
        # 2. Needs more info (UNKNOWN)
        unknown = [r for r in recommended_schemes if r.overall_status == EligibilityStatus.UNKNOWN]
        # 3. Ineligible (FAIL)
        failed = [r for r in recommended_schemes if r.overall_status == EligibilityStatus.FAIL]

        # Render Confirmed Matches
        if eligible:
            lines.append(loc["eligible_title"])
            for res in eligible:
                s_data = schemes_data_map.get(res.scheme_id, {})
                scheme_name = s_data.get("name_kannada") if lang_code == "kn" and s_data.get("name_kannada") else res.scheme_name
                level_str = s_data.get("level", "Central").capitalize()
                lines.append(f"**{scheme_name}** ({level_str})")
                lines.append(f"- **{loc['benefits_label']}:** {res.benefits_summary or s_data.get('benefits_summary')}")
                lines.append(f"- **{loc['reason_label']}:** {res.summary_explanation}")
                if s_data.get("required_documents"):
                    docs_str = ", ".join(s_data["required_documents"][:4])
                    lines.append(f"- **{loc['docs_label']}:** {docs_str}")
                if s_data.get("official_portal_url"):
                    lines.append(f"- **{loc['portal_label']}:** [{s_data.get('source_title', 'Official Link')}]({s_data['official_portal_url']})")
                lines.append("")

        # Render Potential Matches requiring more info
        if unknown:
            lines.append(loc["unknown_title"])
            for res in unknown:
                s_data = schemes_data_map.get(res.scheme_id, {})
                scheme_name = s_data.get("name_kannada") if lang_code == "kn" and s_data.get("name_kannada") else res.scheme_name
                lines.append(f"**{scheme_name}**")
                lines.append(f"- **Status:** ⏳ UNKNOWN — {res.summary_explanation}")
                lines.append(f"- **{loc['missing_label']}:** `{', '.join(res.missing_attributes)}`")
                lines.append(f"- **{loc['benefits_label']}:** {res.benefits_summary or s_data.get('benefits_summary')}")
                if s_data.get("official_portal_url"):
                    lines.append(f"- **{loc['portal_label']}:** [{s_data.get('source_title', 'Official Link')}]({s_data['official_portal_url']})")
                lines.append("")

        # Render Ineligible schemes (with reasons)
        if failed and not eligible:
            lines.append(loc["failed_title"])
            for res in failed:
                s_data = schemes_data_map.get(res.scheme_id, {})
                lines.append(f"**{res.scheme_name}**")
                for fc in res.failed_criteria:
                    lines.append(f"- ❌ *{fc.name}*: {fc.reason} *(Source: {fc.source_citation})*")
                lines.append("")

        # Render Near-Miss Alternatives if user failed
        if near_misses:
            lines.append(loc["near_miss_title"])
            for alt in near_misses:
                s_data = schemes_data_map.get(alt.scheme_id, {})
                lines.append(f"**{alt.scheme_name}**")
                lines.append(f"- **{loc['why_alt_label']}** {alt.near_miss_reason}")
                lines.append(f"- **{loc['benefits_label']}:** {alt.benefits_summary or s_data.get('benefits_summary')}")
                if s_data.get("official_portal_url"):
                    lines.append(f"- **{loc['portal_label']}:** [{s_data.get('source_title', 'Official Link')}]({s_data['official_portal_url']})")
                lines.append("")

        # Adaptive Follow-up question callout
        if follow_up_question:
            lines.append(f"{loc['follow_up_header']}\n> {follow_up_question}\n")

        # Official Disclaimer
        lines.append(loc["disclaimer"])

        return "\n".join(lines)

    def _generate_ollama(
        self, query, profile, recommended_schemes, schemes_data_map, language, follow_up_question, near_misses
    ) -> str:
        """Generate conversational response via local Ollama instance with strict evidence grounding."""
        context = RAGContextBuilder.build_context(
            recommended_schemes, profile, schemes_data_map, language
        )
        lang_name = LANGUAGE_NAMES.get(language, "English")
        prompt = f"""You are Sahayaka, an official multilingual Indian government scheme discovery assistant.
Reply in {lang_name}. Be warm, concise, and easy to understand.

USER MESSAGE:
{query}

VERIFIED BACKEND EVIDENCE (scheme details, citations and eligibility statuses):
{context}

FOLLOW-UP QUESTION TO INCLUDE:
{follow_up_question or 'None'}

INSTRUCTIONS:
1. Base your answer strictly on the provided evidence.
2. Preserve every PASS, FAIL, and UNKNOWN status exactly as provided; never make a different eligibility decision.
3. Do not invent any benefits or conditions.
4. End with an informational disclaimer.
"""
        payload = {
            "model": settings.LLM_MODEL_NAME or "llama3.2:3b",
            "messages": [
                {"role": "system", "content": "You generate grounded explanations. Never override structured eligibility evidence."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"temperature": 0.2},
        }
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        req = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        timeout = getattr(settings, "OLLAMA_TIMEOUT_SECONDS", 90)
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("message", {}) or {}
            content = msg.get("content", "")
            if not content:
                content = data.get("response", "")
            return content.strip()

    def _generate_gemini(
        self, query, profile, recommended_schemes, schemes_data_map, language, follow_up_question, near_misses
    ) -> str:
        """Invokes Gemini API with strict grounding instructions."""
        context = RAGContextBuilder.build_context(recommended_schemes, profile, schemes_data_map, language)
        lang_name = LANGUAGE_NAMES.get(language, "English")
        prompt = f"""
You are an official Multilingual Government Scheme Assistant for India, Karnataka, Andhra Pradesh, Tamil Nadu, and Kerala.
Language: {lang_name}

User Query: {query}

EVIDENCE & ELIGIBILITY VERIFICATION:
{context}

Follow-up Question to include if applicable: {follow_up_question or 'None'}

INSTRUCTIONS:
1. Base your answer strictly on the provided evidence.
2. Preserve all PASS, FAIL, UNKNOWN eligibility statuses determined by the rule engine. Never contradict them.
3. Include official portal URLs and citations.
4. Do not invent any benefits, income limits, or deadlines.
5. End with the official disclaimer.
"""
        try:
            from google import genai
            client = genai.Client(api_key=settings.LLM_API_KEY)
            response = client.models.generate_content(
                model=settings.LLM_MODEL_NAME or "gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except ImportError:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=settings.LLM_API_KEY)
            model = legacy_genai.GenerativeModel(settings.LLM_MODEL_NAME)
            response = model.generate_content(prompt)
            return response.text
