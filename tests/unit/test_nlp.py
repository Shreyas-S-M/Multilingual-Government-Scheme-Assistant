"""
Unit Tests for Multilingual NLP Pipeline.
Covers text normalization, Kannada numerals, Indian currency parsing,
language detection, intent classification, and entity extraction.
"""
import pytest
from backend.nlp.text_normalizer import TextNormalizer
from backend.nlp.language_detector import LanguageDetector
from backend.nlp.intent_classifier import IntentClassifier
from backend.nlp.entity_extractor import EntityExtractor
from backend.schemas.user_profile import UserProfile


class TestTextNormalizer:
    def test_unicode_and_whitespace_normalization(self):
        raw = "  ಪ್ರಧಾನ   ಮಂತ್ರಿ   ಕಿಸಾನ್  \t\n  "
        normalized = TextNormalizer.normalize_unicode(raw)
        assert normalized == "ಪ್ರಧಾನ ಮಂತ್ರಿ ಕಿಸಾನ್"

    def test_kannada_digit_normalization(self):
        # ೨೫ = 25, ೧೫೦೦೦೦ = 150000
        text = "ನನ್ನ ವಯಸ್ಸು ೨೫, ಆದಾಯ ೧೫೦೦೦೦"
        digits_fixed = TextNormalizer.normalize_digits(text)
        assert "25" in digits_fixed
        assert "150000" in digits_fixed

    def test_indian_number_and_currency_parsing(self):
        assert TextNormalizer.parse_indian_number("2.5 lakh") == 250000.0
        assert TextNormalizer.parse_indian_number("₹ 1,50,000") == 150000.0
        assert TextNormalizer.parse_indian_number("50 thousand") == 50000.0
        assert TextNormalizer.parse_indian_number("30 ಸಾವಿರ") == 30000.0
        assert TextNormalizer.parse_indian_number("1.2 cr") == 12000000.0
        assert TextNormalizer.parse_indian_number("invalid") is None

    def test_state_normalization(self):
        assert TextNormalizer.normalize_state("I live in Bengaluru, Karnataka") == "Karnataka"
        assert TextNormalizer.normalize_state("ಕರ್ನಾಟಕ ರಾಜ್ಯ") == "Karnataka"
        assert TextNormalizer.normalize_state("New Delhi capital") == "Delhi"
        assert TextNormalizer.normalize_state("Unknown place") is None

    def test_occupation_normalization(self):
        assert TextNormalizer.normalize_occupation("I do agriculture and farming") == "farmer"
        assert TextNormalizer.normalize_occupation("ನಾನು ರೈತ") == "farmer"
        assert TextNormalizer.normalize_occupation("street food vendor") == "street_vendor"
        assert TextNormalizer.normalize_occupation("carpenter and wood worker") == "artisan"
        assert TextNormalizer.normalize_occupation("looking for job, unemployed") == "unemployed"

    def test_category_word_boundary_safety(self):
        # Crucial test: 'schemes' must not trigger 'sc'
        assert TextNormalizer.normalize_category("government schemes list") is None
        assert TextNormalizer.normalize_category("I belong to SC community") == "sc"
        assert TextNormalizer.normalize_category("ಪರಿಶಿಷ್ಟ ಜಾತಿ") == "sc"
        assert TextNormalizer.normalize_category("OBC backward class") == "obc"
        assert TextNormalizer.normalize_category("Muslim minority candidate") == "minority"


class TestLanguageDetector:
    def test_english_detection(self):
        text = "What government schemes are available for unemployed graduates?"
        lang, conf, is_mixed = LanguageDetector.detect(text)
        assert lang == "en"
        assert conf >= 0.8
        assert not is_mixed

    def test_kannada_detection(self):
        text = "ಕರ್ನಾಟಕದ ರೈತರಿಗೆ ಸಿಗುವ ಸಹಾಯಧನ ಯೋಜನೆಗಳು ಯಾವುವು?"
        lang, conf, is_mixed = LanguageDetector.detect(text)
        assert lang == "kn"
        assert conf >= 0.7

    def test_code_mixed_detection(self):
        text = "Nanna age 24, graduate pass out, yava scheme sigutthe?"
        lang, conf, is_mixed = LanguageDetector.detect(text)
        assert is_mixed is True


class TestIntentClassifier:
    def test_eligibility_intent(self):
        intent, conf = IntentClassifier.classify("Am I eligible for PM Kisan scheme?")
        assert intent == "check_eligibility"

    def test_benefits_intent(self):
        intent, conf = IntentClassifier.classify("What are the benefits of Gruha Lakshmi?")
        assert intent == "query_benefits"

    def test_documents_intent(self):
        intent, conf = IntentClassifier.classify("Which documents are needed for Ayushman card?")
        assert intent == "query_documents"

    def test_kannada_intent(self):
        intent, conf = IntentClassifier.classify("ಯುವನಿಧಿ ಯೋಜನೆಗೆ ಹೇಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಬೇಕು?")
        assert intent == "query_application_process"


class TestEntityExtractor:
    def test_bilingual_entity_extraction(self):
        q_en = "I am a 26 year old farmer in Karnataka with annual income of 1.8 lakh."
        entities_en = EntityExtractor.extract_entities(q_en)
        assert entities_en["age"]["value"] == 26
        assert entities_en["annual_income"]["value"] == 180000.0
        assert entities_en["state"]["value"] == "Karnataka"
        assert entities_en["occupation"]["value"] == "farmer"

        q_kn = "ವಯಸ್ಸು 22 ವರ್ಷ, ಕರ್ನಾಟಕ ನಿವಾಸಿ, ವಿದ್ಯಾರ್ಥಿ, ಆದಾಯ 1 ಲಕ್ಷ."
        entities_kn = EntityExtractor.extract_entities(q_kn)
        assert entities_kn["age"]["value"] == 22
        assert entities_kn["annual_income"]["value"] == 100000.0
        assert entities_kn["state"]["value"] == "Karnataka"
        assert entities_kn["is_student"]["value"] is True

    def test_profile_conflict_handling(self):
        profile = UserProfile(age=25, annual_income=100000.0)
        # Update with new conflicting age 30
        new_profile = UserProfile(age=30, state="Karnataka")
        conflicts = profile.merge_profile(new_profile)
        assert "age" in conflicts
        assert profile.field_status["age"] == "conflict"
        assert profile.state == "Karnataka"
