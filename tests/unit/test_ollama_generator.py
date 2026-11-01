import json
from unittest.mock import patch

from backend.core.config import settings
from backend.rag.generator import ResponseGenerator
from backend.schemas.user_profile import UserProfile


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def test_ollama_generator_sends_local_chat_request_and_returns_text(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse({"message": {"content": "Here are the relevant schemes."}})

    monkeypatch.setattr("backend.rag.generator.urlopen", fake_urlopen)
    monkeypatch.setattr(settings, "OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setattr(settings, "OLLAMA_TIMEOUT_SECONDS", 90)
    monkeypatch.setattr(settings, "LLM_MODEL_NAME", "llama3.2:3b")

    generator = ResponseGenerator(provider="ollama")
    answer = generator._generate_ollama(
        "Help me find schemes", UserProfile(), [], {}, "en", None, None
    )

    assert answer == "Here are the relevant schemes."
    assert captured["url"] == "http://127.0.0.1:11434/api/chat"
    assert captured["payload"]["model"] == "llama3.2:3b"
    assert captured["payload"]["stream"] is False
    assert "Preserve every PASS, FAIL, and UNKNOWN status" in captured["payload"]["messages"][1]["content"]


def test_ollama_provider_falls_back_to_deterministic_when_unavailable(monkeypatch):
    generator = ResponseGenerator(provider="ollama")
    monkeypatch.setattr(generator, "_generate_ollama", lambda *args: (_ for _ in ()).throw(ConnectionError("offline")))
    monkeypatch.setattr(generator, "_generate_deterministic", lambda *args: "safe deterministic fallback")

    answer = generator.generate_response(
        query="Help", profile=UserProfile(), recommended_schemes=[],
        schemes_data_map={}, language="en"
    )
    assert answer == "safe deterministic fallback"
