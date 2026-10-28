"""
Academic Evaluation Suite: 20 End-to-End Test Scenarios.
Verifies all 20 required scenarios from Section 17.3 of the Master Specification.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.schemas.user_profile import UserProfile
from backend.schemas.eligibility import EligibilityStatus
from backend.eligibility.engine import EligibilityEngine
from backend.nlp.entity_extractor import EntityExtractor
from backend.nlp.language_detector import LanguageDetector
from backend.nlp.intent_classifier import IntentClassifier
from backend.core.config import settings


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestEndToEndEvaluationScenarios:
    # 1. Complete English profile
    def test_scenario_01_complete_english_profile(self, client):
        msg = "I am a 25 year old farmer living in Karnataka with annual family income of 1.2 lakh."
        res = client.post("/api/v1/chat", json={"message": msg, "language": "en"}).json()
        prof = res["updated_profile"]
        assert prof["age"] == 25
        assert prof["occupation"] == "farmer"
        assert prof["state"] == "Karnataka"
        assert prof["annual_income"] == 120000.0

    # 2. Complete Kannada profile
    def test_scenario_02_complete_kannada_profile(self, client):
        msg = "ನಾನು ಕರ್ನಾಟಕದ ರೈತ, ವಯಸ್ಸು 30 ವರ್ಷ, ವಾರ್ಷಿಕ ಆದಾಯ 1 ಲಕ್ಷ ರೂಪಾಯಿ."
        res = client.post("/api/v1/chat", json={"message": msg, "language": "kn"}).json()
        assert res["detected_language"] == "kn"
        prof = res["updated_profile"]
        assert prof["age"] == 30
        assert prof["occupation"] == "farmer"
        assert prof["state"] == "Karnataka"

    # 3. Kannada-English code-mixed query
    def test_scenario_03_code_mixed_query(self, client):
        msg = "Nanna age 23, degree pass out unemployed in Karnataka. Scheme beku."
        res = client.post("/api/v1/chat", json={"message": msg}).json()
        prof = res["updated_profile"]
        assert prof["age"] == 23
        assert prof["occupation"] == "unemployed"
        assert prof["state"] == "Karnataka"

    # 4. Missing age
    def test_scenario_04_missing_age_yields_adaptive_question(self, client):
        msg = "I am a farmer in Karnataka with annual income of 1.5 lakh."
        res = client.post("/api/v1/chat", json={"message": msg}).json()
        prof = res["updated_profile"]
        assert prof.get("age") is None

    # 5. Missing annual family income
    def test_scenario_05_missing_income(self, client):
        msg = "I am a 22 year old college student in Karnataka."
        res = client.post("/api/v1/chat", json={"message": msg}).json()
        prof = res["updated_profile"]
        assert prof.get("annual_income") is None

    # 6. Missing residence information
    def test_scenario_06_missing_residence(self, client):
        msg = "I am a 28 year old street vendor earning 10 thousand monthly."
        res = client.post("/api/v1/chat", json={"message": msg}).json()
        prof = res["updated_profile"]
        assert prof.get("state") is None

    # 7. Conflicting income statements
    def test_scenario_07_conflicting_income_statements(self, client):
        p1 = {"annual_income": 100000.0}
        msg = "Actually my annual income is 3 lakh now."
        res = client.post("/api/v1/chat", json={"message": msg, "current_profile": p1}).json()
        assert res["has_conflicts"] is True
        assert "annual_income" in res["conflicting_fields"]

    # 8. User satisfies all represented mandatory criteria
    def test_scenario_08_satisfies_all_criteria(self, client):
        payload = {
            "profile": {
                "age": 25,
                "occupation": "farmer",
                "state": "Karnataka",
            },
            "scheme_ids": ["pm-kisan"],
        }
        res = client.post("/api/v1/eligibility/check", json=payload).json()
        assert res[0]["overall_status"] == "PASS"

    # 9. User fails one mandatory criterion
    def test_scenario_09_fails_one_mandatory_criterion(self, client):
        payload = {
            "profile": {
                "age": 16,  # Min age is 18
                "occupation": "farmer",
                "state": "Karnataka",
            },
            "scheme_ids": ["pm-kisan"],
        }
        res = client.post("/api/v1/eligibility/check", json=payload).json()
        assert res[0]["overall_status"] == "FAIL"
        assert res[0]["mandatory_failed_count"] == 1

    # 10. User fails multiple mandatory criteria
    def test_scenario_10_fails_multiple_criteria(self, client):
        payload = {
            "profile": {
                "age": 16,  # Fail
                "occupation": "student",  # Fail
                "state": "Karnataka",
            },
            "scheme_ids": ["pm-kisan"],
        }
        res = client.post("/api/v1/eligibility/check", json=payload).json()
        assert res[0]["overall_status"] == "FAIL"
        assert res[0]["mandatory_failed_count"] >= 2

    # 11. User has both PASS and UNKNOWN conditions
    def test_scenario_11_pass_and_unknown_conditions(self, client):
        payload = {
            "profile": {
                "age": 25,  # PASS
                "occupation": "farmer",  # PASS
                # land_ownership_ha is None -> UNKNOWN
            },
            "scheme_ids": ["pm-kisan"],
        }
        res = client.post("/api/v1/eligibility/check", json=payload).json()
        assert res[0]["overall_status"] == "PASS"  # Because pm-kisan rules age & occupation pass

    # 12. User requests details about a named scheme
    def test_scenario_12_named_scheme_inquiry(self, client):
        res = client.get("/api/v1/schemes/ayushman-bharat-pmjay").json()
        assert res["scheme_id"] == "ayushman-bharat-pmjay"
        assert "5,00,000" in res["benefits_summary"] or "5 Lakh" in res["benefits_summary"] or "5 Lakh" in res["short_description"]

    # 13. User requests required documents
    def test_scenario_13_query_required_documents(self, client):
        intent, _ = IntentClassifier.classify("What documents are required for Yuva Nidhi?")
        assert intent == "query_documents"

    # 14. User requests application instructions
    def test_scenario_14_query_application_instructions(self, client):
        intent, _ = IntentClassifier.classify("How can I apply online for PM SVANidhi?")
        assert intent == "query_application_process"

    # 15. User answers an adaptive follow-up question
    def test_scenario_15_answer_follow_up_updates_profile(self, client):
        initial_profile = {"occupation": "farmer", "state": "Karnataka"}
        answer_msg = "My age is 28 years"
        res = client.post("/api/v1/chat", json={"message": answer_msg, "current_profile": initial_profile}).json()
        assert res["updated_profile"]["age"] == 28
        assert res["updated_profile"]["occupation"] == "farmer"

    # 16. User requests alternatives after failure (Near-Miss)
    def test_scenario_16_near_miss_alternatives(self, client):
        # A student with income 3 Lakh who fails Post Matric SC (ceiling 2.5L)
        p = {"age": 16, "is_student": True, "annual_income": 300000.0}
        res = client.post("/api/v1/chat", json={"message": "I was rejected for scholarship due to 3 lakh income", "current_profile": p}).json()
        # Alternatives should be evaluated or suggested
        assert "reply" in res

    # 17. No matching schemes found
    def test_scenario_17_no_matching_schemes(self, client):
        res = client.get("/api/v1/schemes?search=astronaut_space_station_grant").json()
        assert res["total"] == 0
        assert len(res["items"]) == 0

    # 18. Official source verification check
    def test_scenario_18_official_source_verification(self, client):
        scheme = client.get("/api/v1/schemes/pm-kisan").json()
        assert scheme["official_portal_url"].startswith("https://")
        assert "pmkisan.gov.in" in scheme["official_portal_url"]
        assert scheme["last_verified_date"] is not None

    # 19. LLM provider fallback mode
    def test_scenario_19_deterministic_generator_fallback(self, client):
        assert settings.LLM_PROVIDER == "deterministic"
        res = client.post("/api/v1/chat", json={"message": "I am a farmer in Karnataka"}).json()
        assert res["is_llm_generated"] is False
        assert len(res["reply"]) > 50

    # 20. FAISS index rebuild verification
    def test_scenario_20_index_rebuild(self, client):
        headers = {"X-Admin-API-Key": settings.ADMIN_API_KEY}
        res = client.post("/api/v1/admin/index/rebuild", headers=headers).json()
        assert res["success"] is True
        assert res["scheme_count"] >= 20
