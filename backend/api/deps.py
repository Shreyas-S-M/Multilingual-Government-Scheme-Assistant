"""
FastAPI Route Dependencies.
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.retrieval.hybrid_search import HybridRetriever
from backend.retrieval.vector_store import VectorStore
from backend.retrieval.bm25_search import BM25Retriever
from backend.services.chat_service import ChatService

# Global in-memory singleton for retriever across worker
_global_hybrid_retriever = None


def get_hybrid_retriever() -> HybridRetriever:
    global _global_hybrid_retriever
    if _global_hybrid_retriever is None:
        vs = VectorStore()
        bm = BM25Retriever()
        _global_hybrid_retriever = HybridRetriever(vector_store=vs, bm25_retriever=bm)
    return _global_hybrid_retriever


def get_chat_service(
    db: Session = Depends(get_db),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
) -> ChatService:
    return ChatService(db=db, hybrid_retriever=retriever)
