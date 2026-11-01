"""
Chat & Conversational Reasoning Endpoints.
Handles multilingual citizen queries, profile extraction, adaptive questioning,
and evidence-grounded scheme recommendations.
"""
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from backend.schemas.chat import ChatMessageRequest, ChatMessageResponse
from backend.services.chat_service import ChatService
from backend.api.deps import get_chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


class ResetConversationRequest(BaseModel):
    conversation_id: Optional[str] = None


@router.post("", response_model=ChatMessageResponse)
def handle_chat_message(
    request: ChatMessageRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User message cannot be empty.",
        )
    return chat_service.process_message(request)


@router.post("/reset")
def reset_conversation(
    request: Optional[ResetConversationRequest] = Body(default=None),
    conversation_id: Optional[str] = Query(default=None),
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Resets an active conversation session and deletes stored messages from the database.
    Accepts conversation_id via JSON body {"conversation_id": "..."} or query parameter ?conversation_id=...
    """
    target_id = (request.conversation_id if request and request.conversation_id else None) or conversation_id
    deleted_count, success = chat_service.reset_conversation_detailed(target_id)
    return {
        "status": "success" if success else "warning",
        "conversation_id": target_id,
        "messages_deleted": deleted_count,
        "message": (
            f"Conversation session '{target_id}' and {deleted_count} messages reset successfully."
            if target_id
            else f"Reset all conversation sessions ({deleted_count} messages deleted)."
        ),
    }

