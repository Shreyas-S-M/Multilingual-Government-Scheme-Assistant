"""
Frontend API Client Service.
Provides robust HTTP communication with the FastAPI backend with timeout protection
and transparent error handling.
"""
import sys
from pathlib import Path

# Ensure workspace root is in sys.path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests
from typing import Dict, Any, Optional, List
from backend.core.config import settings
from backend.schemas.user_profile import UserProfile

BASE_URL = settings.BACKEND_API_BASE_URL.rstrip("/")
TIMEOUT = 60.0


class APIClient:
    @staticmethod
    def check_health() -> Dict[str, Any]:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            return {"status": "degraded", "error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    @staticmethod
    def send_chat_message(
        message: str,
        conversation_id: Optional[str] = None,
        language: Optional[str] = None,
        current_profile: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "message": message,
            "conversation_id": conversation_id,
            "language": language,
            "current_profile": current_profile,
        }
        try:
            r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            return {
                "reply": "⏳ **Request Timed Out**: The backend server took longer than expected to respond (often happens during initial model loading). The model is now cached in memory; please click or send your message again for an instant response.",
                "language": language or "en",
                "detected_language": "en",
                "intent": "timeout",
                "conversation_id": conversation_id or "error",
                "extracted_entities": {},
                "updated_profile": current_profile or {},
                "recommended_schemes": [],
                "near_miss_schemes": [],
                "follow_up_question": None,
                "sources": [],
            }
        except requests.exceptions.ConnectionError:
            return {
                "reply": "⚠️ **Cannot Connect to Backend**: The FastAPI backend is not running at `http://127.0.0.1:8000`. Please start it in a terminal using:\n```powershell\nuvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload\n```",
                "language": language or "en",
                "detected_language": "en",
                "intent": "connection_error",
                "conversation_id": conversation_id or "error",
                "extracted_entities": {},
                "updated_profile": current_profile or {},
                "recommended_schemes": [],
                "near_miss_schemes": [],
                "follow_up_question": None,
                "sources": [],
            }
        except requests.exceptions.RequestException as e:
            return {
                "reply": f"⚠️ Could not connect to Backend API service: {str(e)}",
                "language": language or "en",
                "detected_language": "en",
                "intent": "error",
                "conversation_id": conversation_id or "error",
                "extracted_entities": {},
                "updated_profile": current_profile or {},
                "recommended_schemes": [],
                "near_miss_schemes": [],
                "follow_up_question": None,
                "sources": [],
            }

    @staticmethod
    def reset_conversation(conversation_id: str) -> Dict[str, Any]:
        """Resets active conversation and flushes stored messages from the backend."""
        try:
            resp = requests.post(
                f"{API_BASE_URL}/chat/reset",
                json={"conversation_id": conversation_id},
                timeout=5,
            )
            if resp.status_code == 200:
                return resp.json()
            return {"status": "warning", "message": f"Server returned {resp.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def list_schemes(
        category: Optional[str] = None,
        level: Optional[str] = None,
        state: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 12,
    ) -> Dict[str, Any]:
        params = {
            "category": category,
            "level": level,
            "state": state,
            "search": search,
            "page": page,
            "page_size": page_size,
        }
        # Filter None
        params = {k: v for k, v in params.items() if v is not None}
        try:
            r = requests.get(f"{BASE_URL}/schemes", params=params, timeout=TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"total": 0, "items": [], "error": str(e)}

    @staticmethod
    def get_scheme_details(scheme_id: str) -> Optional[Dict[str, Any]]:
        try:
            r = requests.get(f"{BASE_URL}/schemes/{scheme_id}", timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            return None
        except Exception:
            return None

    @staticmethod
    def check_eligibility(
        profile: Dict[str, Any], scheme_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        payload = {"profile": profile, "scheme_ids": scheme_ids}
        try:
            r = requests.post(
                f"{BASE_URL}/eligibility/check", json=payload, timeout=TIMEOUT
            )
            r.raise_for_status()
            return r.json()
        except Exception:
            return []

    @staticmethod
    def get_admin_stats(api_key: str) -> Optional[Dict[str, Any]]:
        headers = {"X-Admin-API-Key": api_key}
        try:
            r = requests.get(
                f"{BASE_URL}/admin/stats", headers=headers, timeout=TIMEOUT
            )
            if r.status_code == 200:
                return r.json()
            return None
        except Exception:
            return None

    @staticmethod
    def rebuild_index(api_key: str) -> Dict[str, Any]:
        headers = {"X-Admin-API-Key": api_key}
        try:
            r = requests.post(
                f"{BASE_URL}/admin/index/rebuild", headers=headers, timeout=TIMEOUT
            )
            return r.json()
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def import_schemes(
        schemes_data: List[Dict[str, Any]], overwrite: bool, api_key: str
    ) -> Dict[str, Any]:
        headers = {"X-Admin-API-Key": api_key}
        payload = {"schemes": schemes_data, "overwrite_existing": overwrite}
        try:
            r = requests.post(
                f"{BASE_URL}/admin/schemes/import",
                json=payload,
                headers=headers,
                timeout=TIMEOUT,
            )
            return r.json()
        except Exception as e:
            return {"total_received": len(schemes_data), "errors": [str(e)]}

    @staticmethod
    def get_evaluation_metrics() -> Dict[str, Any]:
        try:
            r = requests.get(f"{BASE_URL}/evaluation/metrics", timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            return {}
        except Exception:
            return {}
