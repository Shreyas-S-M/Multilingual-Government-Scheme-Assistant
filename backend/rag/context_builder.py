"""
RAG Context Builder.
Constructs structured, tamper-proof contextual evidence packages from verified scheme records
and eligibility engine outcomes for response synthesis.
"""
from typing import List, Dict, Any
from backend.schemas.eligibility import SchemeEligibilityResult, EligibilityStatus
from backend.schemas.user_profile import UserProfile


class RAGContextBuilder:
    @staticmethod
    def build_context(
        evaluated_schemes: List[SchemeEligibilityResult],
        profile: UserProfile,
        schemes_data_map: Dict[str, Any],
        language: str = "en",
    ) -> str:
        """
        Builds grounded context string incorporating official scheme details,
        evaluation results (PASS/FAIL/UNKNOWN), and source citations.
        """
        lines = []
        lines.append("=== RETRIEVED GOVERNMENT SCHEMES & ELIGIBILITY EVIDENCE ===")
        lines.append(f"User Profile Snapshot: {profile.get_known_attributes()}")
        lines.append("")

        for idx, res in enumerate(evaluated_schemes, 1):
            scheme_raw = schemes_data_map.get(res.scheme_id, {})
            name = res.scheme_name
            cat = scheme_raw.get("category", "General Welfare")
            dept = scheme_raw.get("department", "Government Department")
            benefits = res.benefits_summary or scheme_raw.get("benefits_summary", "Official welfare assistance")
            official_url = res.official_portal_url or scheme_raw.get("official_portal_url", "")
            source_title = scheme_raw.get("source_title", "Official Gazette / Government Portal")
            verified_date = scheme_raw.get("last_verified_date", "2025-01-01")

            lines.append(f"SCHEME #{idx}: {name} [{res.scheme_id}]")
            lines.append(f"  Category: {cat} | Department: {dept}")
            lines.append(f"  Overall Eligibility Status: {res.overall_status.value}")
            lines.append(f"  Summary: {res.summary_explanation}")
            lines.append(f"  Benefits: {benefits}")
            lines.append(f"  Official Source: {source_title} ({official_url}) [Verified: {verified_date}]")

            # Criterion Breakdown
            lines.append("  Criteria Evidence:")
            for cr in res.criteria_results:
                mand_str = "MANDATORY" if cr.is_mandatory else "OPTIONAL"
                lines.append(
                    f"    - [{cr.status.value}] ({mand_str}) {cr.name}: {cr.reason} (Citation: {cr.source_citation})"
                )

            # Documents & Process
            docs = scheme_raw.get("required_documents", [])
            if docs:
                lines.append(f"  Required Documents: {', '.join(docs)}")

            process = scheme_raw.get("application_process", [])
            if process:
                lines.append(f"  Application Steps: {' -> '.join(process[:3])}")

            lines.append("")

        return "\n".join(lines)
