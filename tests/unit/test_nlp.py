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

    def test_south_indian_indic_digit_normalization(self):
        # Telugu: ౨౫ = 25, ౧౫౦౦౦౦ = 150000
        te_text = "నా వయస్సు ౨౫, ఆదాయం ౧౫౦౦౦౦"
        te_fixed = TextNormalizer.normalize_digits(te_text)
        assert "25" in te_fixed
        assert "150000" in te_fixed

        # Tamil: ௨௫ = 25, ௧௫௦௦௦௦ = 150000
        ta_text = "என் வயது ௨௫, வருமானம் ௧௫௦௦௦௦"
        ta_fixed = TextNormalizer.normalize_digits(ta_text)
        assert "25" in ta_fixed
        assert "150000" in ta_fixed

        # Malayalam: ൨൫ = 25, ൧൫൦൦൦൦ = 150000
        ml_text = "എന്റെ പ്രായം ൨൫, വരുമാനം ൧൫൦൦൦൦"
        ml_fixed = TextNormalizer.normalize_digits(ml_text)
        assert "25" in ml_fixed
        assert "150000" in ml_fixed

    def test_indian_number_and_currency_parsing(self):
        assert TextNormalizer.parse_indian_number("2.5 lakh") == 250000.0
        assert TextNormalizer.parse_indian_number("₹ 1,50,000") == 150000.0
        assert TextNormalizer.parse_indian_number("50 thousand") == 50000.0
        assert TextNormalizer.parse_indian_number("30 ಸಾವಿರ") == 30000.0
        assert TextNormalizer.parse_indian_number("50 వేలు") == 50000.0
        assert TextNormalizer.parse_indian_number("2.5 లక్ష") == 250000.0
        assert TextNormalizer.parse_indian_number("50 ஆயிரம்") == 50000.0
        assert TextNormalizer.parse_indian_number("2.5 லட்சம்") == 250000.0
        assert TextNormalizer.parse_indian_number("50 ആയിരം") == 50000.0
        assert TextNormalizer.parse_indian_number("2.5 ലക്ഷം") == 250000.0
        assert TextNormalizer.parse_indian_number("1.2 cr") == 12000000.0
        assert TextNormalizer.parse_indian_number("invalid") is None

    def test_state_normalization(self):
        assert TextNormalizer.normalize_state("I live in Bengaluru, Karnataka") == "Karnataka"
        assert TextNormalizer.normalize_state("ಕರ್ನಾಟಕ ರಾಜ್ಯ") == "Karnataka"
        assert TextNormalizer.normalize_state("New Delhi capital") == "Delhi"
        assert TextNormalizer.normalize_state("ఆంధ్ర ప్రదేశ్ రైతు") == "Andhra Pradesh"
        assert TextNormalizer.normalize_state("I live in Vijayawada, Andhra Pradesh") == "Andhra Pradesh"
        assert TextNormalizer.normalize_state("தமிழ்நாடு மாணவர்") == "Tamil Nadu"
        assert TextNormalizer.normalize_state("I live in Madurai, Tamil Nadu") == "Tamil Nadu"
        assert TextNormalizer.normalize_state("കേരളത്തിലെ കർഷകൻ") == "Kerala"
        assert TextNormalizer.normalize_state("I live in Kochi, Kerala") == "Kerala"
        assert TextNormalizer.normalize_state("Unknown place") is None

    def test_occupation_normalization(self):
        assert TextNormalizer.normalize_occupation("I do agriculture and farming") == "farmer"
        assert TextNormalizer.normalize_occupation("ನಾನು ರೈತ") == "farmer"
        assert TextNormalizer.normalize_occupation("నేను రైతు") == "farmer"
        assert TextNormalizer.normalize_occupation("நான் விவசாயி") == "farmer"
        assert TextNormalizer.normalize_occupation("ഞാൻ കർഷകൻ") == "farmer"
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

    def test_telugu_detection(self):
        text = "ఆంధ్రప్రదేశ్ రైతులకు లభించే సబ్సిడీ పథకాలు ఏమిటి?"
        lang, conf, is_mixed = LanguageDetector.detect(text)
        assert lang == "te"
        assert conf >= 0.7

    def test_tamil_detection(self):
        text = "தமிழ்நாடு விவசாயிகளுக்கு கிடைக்கும் அரசு நலத்திட்டங்கள் என்ன?"
        lang, conf, is_mixed = LanguageDetector.detect(text)
        assert lang == "ta"
        assert conf >= 0.7

    def test_malayalam_detection(self):
        text = "കേരളത്തിലെ കർഷകർക്ക് ലഭിക്കുന്ന ആനുകൂല്യങ്ങൾ ഏതെല്ലാമാണ്?"
        lang, conf, is_mixed = LanguageDetector.detect(text)
        assert lang == "ml"
        assert conf >= 0.7

    def test_code_mixed_detection(self):
        text = "Nanna age 24, graduate pass out, yava scheme sigutthe?"
        lang, conf, is_mixed = LanguageDetector.detect(text)
        assert is_mixed is True

    def test_south_indian_code_mixed_detection(self):
        te_mixed = "Naa age 25, Andhra farmer, em scheme undi?"
        _, _, is_te_mixed = LanguageDetector.detect(te_mixed)
        assert is_te_mixed is True

        ta_mixed = "Enakku 22 vayasu, Tamil Nadu student, scholarship irukka?"
        _, _, is_ta_mixed = LanguageDetector.detect(ta_mixed)
        assert is_ta_mixed is True

        ml_mixed = "Enikku 26 vayas, Kerala unemployed graduate, ethu scheme kittum?"
        _, _, is_ml_mixed = LanguageDetector.detect(ml_mixed)
        assert is_ml_mixed is True


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

    def test_south_indian_entity_extraction(self):
        # Telugu
        q_te = "వయస్సు 25 సంవత్సరాలు, ఆంధ్ర ప్రదేశ్ నివాసి, రైతు, వార్షిక ఆదాయం 1.5 లక్ష."
        entities_te = EntityExtractor.extract_entities(q_te)
        assert entities_te["age"]["value"] == 25
        assert entities_te["annual_income"]["value"] == 150000.0
        assert entities_te["state"]["value"] == "Andhra Pradesh"
        assert entities_te["occupation"]["value"] == "farmer"

        # Tamil
        q_ta = "வயது 24 ஆண்டுகள், தமிழ்நாடு, விவசாயி, வருமானம் 2 லட்சம்."
        entities_ta = EntityExtractor.extract_entities(q_ta)
        assert entities_ta["age"]["value"] == 24
        assert entities_ta["annual_income"]["value"] == 200000.0
        assert entities_ta["state"]["value"] == "Tamil Nadu"
        assert entities_ta["occupation"]["value"] == "farmer"

        # Malayalam
        q_ml = "വയസ്സ് 23, കേരളം, വിദ്യാർത്ഥി, വരുമാനം 1.2 ലക്ഷം."
        entities_ml = EntityExtractor.extract_entities(q_ml)
        assert entities_ml["age"]["value"] == 23
        assert entities_ml["annual_income"]["value"] == 120000.0
        assert entities_ml["state"]["value"] == "Kerala"
        assert entities_ml["is_student"]["value"] is True

    def test_kannada_agglutinative_age_extraction(self):
        """Verifies Dravidian case inflections attach to numbers without whitespace (FAULT-04)."""
        cases = [
            ("ನನಗೆ 22 ವರ್ಷ", 22),
            ("ನನಗೆ 22 ವರ್ಷದ", 22),
            ("ನನ್ನ ವಯಸ್ಸು 22", 22),
            ("22 ವಯಸ್ಸಿನ ಯುವಕ", 22),
            ("22 ವರ್ಷಕ್ಕೆ", 22),
            ("22 ವರ್ಷಗಳು", 22),
            ("22ವರ್ಷ", 22),
            ("೨೨ ವರ್ಷದ", 22),
            ("nanna vayassu 22", 22),
            ("22 varsha", 22),
        ]
        for text, expected in cases:
            res = EntityExtractor.extract_entities(text)
            assert "age" in res, f"Expected 'age' in {text}"
            assert res["age"]["value"] == expected

    def test_kannada_postfix_income_extraction(self):
        """Verifies Kannada income postfix notations and currency symbols (FAULT-04)."""
        cases = [
            ("ಆದಾಯ 1.5 ಲಕ್ಷ", 150000.0),
            ("ಆದಾಯ 50 ಸಾವಿರ", 50000.0),
            ("1.5 ಲಕ್ಷ ಆದಾಯ", 150000.0),
            ("50 ಸಾವಿರ ರೂಪಾಯಿ ಆದಾಯ", 50000.0),
            ("ರೂ 50000", 50000.0),
            ("1.5 lakh income", 150000.0),
            ("earning 2.5 lac", 250000.0),
        ]
        for text, expected in cases:
            res = EntityExtractor.extract_entities(text)
            assert "annual_income" in res, f"Expected 'annual_income' in {text}"
            assert res["annual_income"]["value"] == expected

    def test_profile_conflict_handling(self):
        profile = UserProfile(age=25, annual_income=100000.0)
        # Update with new conflicting age 30
        new_profile = UserProfile(age=30, state="Karnataka")
        conflicts = profile.merge_profile(new_profile)
        assert "age" in conflicts
        assert profile.field_status["age"] == "conflict"
        assert profile.state == "Karnataka"
