"""
Grounded Response Generation Service.
Implements provider-independent generation with an authoritative, deterministic template fallback.
Enforces that eligibility statuses (PASS, FAIL, UNKNOWN) are strictly preserved from the rule engine.
"""
from typing import List, Dict, Any, Optional
from backend.core.config import settings
from backend.schemas.eligibility import SchemeEligibilityResult, EligibilityStatus
from backend.schemas.user_profile import UserProfile
from backend.rag.context_builder import RAGContextBuilder
from backend.core.logging import logger


class ResponseGenerator:
    def __init__(self, provider: str = None):
        self.provider = provider or settings.LLM_PROVIDER

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
        Synthesizes grounded conversational response.
        Uses deterministic generation by default or if external LLM provider fails/is unconfigured.
        """
        if self.provider == "gemini" and settings.LLM_API_KEY:
            try:
                return self._generate_gemini(
                    query, profile, recommended_schemes, schemes_data_map, language, follow_up_question, near_misses
                )
            except Exception as e:
                logger.warning(f"Gemini generation failed ({e}), falling back to deterministic response.")

        # Authoritative deterministic generation
        return self._generate_deterministic(
            query, profile, recommended_schemes, schemes_data_map, language, follow_up_question, near_misses
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
        """Assembles structured, verifiable markdown response from verified records."""
        is_kannada = language == "kn"
        lines = []

        # Intro
        if is_kannada:
            lines.append("### ನಿಮ್ಮ ವಿವರಗಳಿಗೆ ಸಂಬಂಧಿಸಿದ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ವಿಶ್ಲೇಷಣೆ\n")
            lines.append("ನೀವು ಒದಗಿಸಿದ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ಕೆಳಗಿನ ಯೋಜನೆಗಳ ಅರ್ಹತೆಯನ್ನು ಪರಿಶೀಲಿಸಲಾಗಿದೆ:\n")
        else:
            lines.append("### Personalized Government Scheme Assessment\n")
            lines.append("Based on the details provided in your query, here is your transparent eligibility evaluation:\n")

        if not recommended_schemes:
            if is_kannada:
                lines.append("ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಹೊಂದಿಕೆಯಾಗುವ ಯಾವುದೇ ನೇರ ಯೋಜನೆಗಳು ಸದ್ಯಕ್ಕೆ ಪತ್ತೆಯಾಗಿಲ್ಲ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ವಯಸ್ಸು, ವೃತ್ತಿ, ಅಥವಾ ಆದಾಯದ ಬಗ್ಗೆ ಹೆಚ್ಚಿನ ವಿವರಗಳನ್ನು ನೀಡಿ.")
            else:
                lines.append("No specific schemes matched your exact profile yet. Please provide more details such as your occupation, annual family income, or state of residence.")
            return "\n".join(lines)

        # 1. Eligible schemes (PASS)
        eligible = [r for r in recommended_schemes if r.overall_status == EligibilityStatus.PASS]
        # 2. Needs more info (UNKNOWN)
        unknown = [r for r in recommended_schemes if r.overall_status == EligibilityStatus.UNKNOWN]
        # 3. Ineligible (FAIL)
        failed = [r for r in recommended_schemes if r.overall_status == EligibilityStatus.FAIL]

        # Render Confirmed Matches
        if eligible:
            header = "#### ✅ ನೀವು ಅರ್ಹತೆ ಹೊಂದಿರುವ ಯೋಜನೆಗಳು (Appears Eligible)" if is_kannada else "#### ✅ Schemes You Appear Eligible For"
            lines.append(header)
            for res in eligible:
                s_data = schemes_data_map.get(res.scheme_id, {})
                scheme_name = s_data.get("name_kannada") if is_kannada and s_data.get("name_kannada") else res.scheme_name
                lines.append(f"**{scheme_name}** ({s_data.get('level', 'Central').capitalize()})")
                lines.append(f"- **Benefits:** {res.benefits_summary or s_data.get('benefits_summary')}")
                lines.append(f"- **Reason:** {res.summary_explanation}")
                if s_data.get("required_documents"):
                    docs_str = ", ".join(s_data["required_documents"][:4])
                    lines.append(f"- **Required Documents:** {docs_str}")
                if s_data.get("official_portal_url"):
                    lines.append(f"- **Official Portal:** [{s_data.get('source_title', 'Official Link')}]({s_data['official_portal_url']})")
                lines.append("")

        # Render Potential Matches requiring more info
        if unknown:
            header = "#### ℹ️ ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಅಗತ್ಯವಿರುವ ಯೋಜನೆಗಳು (Information Needed)" if is_kannada else "#### ℹ️ Schemes Requiring More Information"
            lines.append(header)
            for res in unknown:
                s_data = schemes_data_map.get(res.scheme_id, {})
                scheme_name = s_data.get("name_kannada") if is_kannada and s_data.get("name_kannada") else res.scheme_name
                lines.append(f"**{scheme_name}**")
                lines.append(f"- **Status:** ⏳ UNKNOWN — {res.summary_explanation}")
                lines.append(f"- **Missing Attributes:** `{', '.join(res.missing_attributes)}`")
                lines.append(f"- **Expected Benefits:** {res.benefits_summary or s_data.get('benefits_summary')}")
                if s_data.get("official_portal_url"):
                    lines.append(f"- **Official Portal:** [{s_data.get('source_title', 'Official Link')}]({s_data['official_portal_url']})")
                lines.append("")

        # Render Ineligible schemes (with reasons)
        if failed and not eligible:
            header = "#### ❌ ಪ್ರಸ್ತುತ ಅರ್ಹತೆ ಹೊಂದಿರದ ಯೋಜನೆಗಳು (Ineligible)" if is_kannada else "#### ❌ Schemes You Do Not Currently Qualify For"
            lines.append(header)
            for res in failed:
                s_data = schemes_data_map.get(res.scheme_id, {})
                lines.append(f"**{res.scheme_name}**")
                for fc in res.failed_criteria:
                    lines.append(f"- ❌ *{fc.name}*: {fc.reason} *(Source: {fc.source_citation})*")
                lines.append("")

        # Render Near-Miss Alternatives if user failed
        if near_misses:
            header = "#### 💡 ಪರ್ಯಾಯ ಯೋಜನೆಗಳ ಶಿಫಾರಸು (Alternative Scheme Options)" if is_kannada else "#### 💡 Alternative Scheme Options (Near-Miss Recommendations)"
            lines.append(header)
            for alt in near_misses:
                s_data = schemes_data_map.get(alt.scheme_id, {})
                lines.append(f"**{alt.scheme_name}**")
                lines.append(f"- **Why this alternative?** {alt.near_miss_reason}")
                lines.append(f"- **Benefits:** {alt.benefits_summary or s_data.get('benefits_summary')}")
                if s_data.get("official_portal_url"):
                    lines.append(f"- **Official Portal:** [{s_data.get('source_title', 'Official Link')}]({s_data['official_portal_url']})")
                lines.append("")

        # Adaptive Follow-up question callout
        if follow_up_question:
            q_header = "\n> **🎯 ಮುಂದುವರಿದ ಪ್ರಶ್ನೆ (Follow-Up Question):**" if is_kannada else "\n> **🎯 Targeted Follow-Up Question:**"
            lines.append(f"{q_header}\n> {follow_up_question}\n")

        # Official Disclaimer
        disclaimer = (
            "\n*ಗಮನಿಸಿ: ಈ ಶಿಫಾರಸುಗಳು ಮಾಹಿತಿ ಉದ್ದೇಶಗಳಿಗಾಗಿ ಮಾತ್ರ. ಅಂತಿಮ ಅರ್ಹತೆ ಮತ್ತು ಅರ್ಜಿ ಅನುಮೋದನೆಯನ್ನು ಸಂಬಂಧಪಟ್ಟ ಸರ್ಕಾರಿ ಪ್ರಾಧಿಕಾರವೇ ನಿರ್ಧರಿಸುತ್ತದೆ.*"
            if is_kannada
            else "\n*Note: Scheme recommendations are for informational discovery only. Official eligibility determinations and benefit approvals are made solely by the respective government authorities.*"
        )
        lines.append(disclaimer)

        return "\n".join(lines)

    def _generate_gemini(self, query, profile, recommended_schemes, schemes_data_map, language, follow_up_question, near_misses) -> str:
        """Invokes Gemini API with strict grounding instructions."""
        import google.generativeai as genai
        genai.configure(api_key=settings.LLM_API_KEY)
        model = genai.GenerativeModel(settings.LLM_MODEL_NAME)

        context = RAGContextBuilder.build_context(recommended_schemes, profile, schemes_data_map, language)
        prompt = f"""
You are an official Multilingual Government Scheme Assistant for India and Karnataka.
Language: {'Kannada' if language == 'kn' else 'English'}

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
        response = model.generate_content(prompt)
        return response.text
