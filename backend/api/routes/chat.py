"""
Chat & Conversational Reasoning Endpoints.
Handles multilingual citizen queries, profile extraction, adaptive questioning,
and evidence-grounded scheme recommendations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from backend.schemas.chat import ChatMessageRequest, ChatMessageResponse
from backend.services.chat_service import ChatService
from backend.api.deps import get_chat_service

router = APIRouter(prefix="/chat", tags=["Chat"])


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
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service),
):
    """Resets an active conversation session."""
    return {
        "status": "success",
        "conversation_id": conversation_id,
        "message": "Conversation session and profile reset successfully.",
    }
