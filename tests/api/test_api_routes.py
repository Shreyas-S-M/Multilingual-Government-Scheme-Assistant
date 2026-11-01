"""
Integration API Tests using FastAPI TestClient.
Tests health, schemes browsing, conversation endpoint, and standalone eligibility.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["components"]["database"]["status"] == "connected"


def test_schemes_list_and_detail(client):
    res = client.get("/api/v1/schemes?page=1&page_size=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 20
    assert len(data["items"]) == 10

    # Test scheme details
    first_id = data["items"][0]["scheme_id"]
    detail_res = client.get(f"/api/v1/schemes/{first_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["scheme_id"] == first_id
    assert "official_portal_url" in detail
    assert "rules" in detail


def test_chat_turn_english_farmer(client):
    payload = {
        "message": "I am a 28 year old farmer living in Karnataka with annual income of 1.5 lakh. What schemes can I get?",
        "language": "en",
    }
    res = client.post("/api/v1/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "reply" in data
    assert data["detected_language"] == "en"
    assert data["updated_profile"]["occupation"] == "farmer"
    assert data["updated_profile"]["age"] == 28
    assert len(data["recommended_schemes"]) > 0


def test_chat_turn_kannada_query(client):
    payload = {
        "message": "ನಾನು ಕರ್ನಾಟಕದ ಪದವೀಧರ, ಕೆಲಸವಿಲ್ಲದೆ 6 ತಿಂಗಳು ಕಳೆದಿದೆ. ಯಾವ ಯೋಜನೆ ಸಿಗುತ್ತದೆ?",
        "language": "kn",
    }
    res = client.post("/api/v1/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["detected_language"] == "kn"
    assert "ಯುವ" in data["reply"] or "ಯೋಜನೆ" in data["reply"]


def test_standalone_eligibility_check(client):
    payload = {
        "profile": {
            "age": 28,
            "annual_income": 150000.0,
            "state": "Karnataka",
            "occupation": "farmer",
        },
        "scheme_ids": ["pm-kisan", "raitha-siri-karnataka"],
    }
    res = client.post("/api/v1/eligibility/check", json=payload)
    assert res.status_code == 200
    results = res.json()
    assert len(results) == 2
    for r in results:
        assert r["overall_status"] == "PASS"
        assert len(r["criteria_results"]) > 0


def test_chat_reset_endpoint(client):
    """Verifies that /chat/reset deletes stored messages and conversation records (FAULT-05)."""
    conv_id = "test-reset-session-999"
    # 1. Post a message to create session and messages
    res1 = client.post("/api/v1/chat", json={
        "message": "I am a 30 year old teacher in Karnataka",
        "conversation_id": conv_id,
    })
    assert res1.status_code == 200

    # 2. Reset via JSON body
    res2 = client.post("/api/v1/chat/reset", json={"conversation_id": conv_id})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "success"
    assert data2["conversation_id"] == conv_id
    assert data2["messages_deleted"] >= 1

    # 3. Subsequent reset should safely report 0 deleted messages
    res3 = client.post(f"/api/v1/chat/reset?conversation_id={conv_id}")
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["status"] == "success"
    assert data3["messages_deleted"] == 0


def test_evaluation_metrics_dynamic(client):
    """Verifies that /evaluation/metrics computes live dynamic NLP and benchmark stats (FAULT-07)."""
    res = client.get("/api/v1/evaluation/metrics?dynamic=true")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["evaluation_mode"] == "dynamic_live_evaluation"
    bench = data["benchmark_results"]
    assert bench["language_detection"]["overall_accuracy"] == 1.0
    assert bench["nlp_extraction"]["micro_f1_score"] == 1.0
    assert "age" in bench["nlp_extraction"]["per_field_metrics"]


def test_sqlite_wal_pragmas(client):
    """Verifies SQLite WAL mode and busy timeout concurrency settings (FAULT-09)."""
    from backend.db.session import engine
    with engine.connect() as conn:
        journal_mode = conn.exec_driver_sql("PRAGMA journal_mode;").scalar()
        busy_timeout = conn.exec_driver_sql("PRAGMA busy_timeout;").scalar()
        assert str(journal_mode).lower() == "wal"
        assert int(busy_timeout) >= 5000

