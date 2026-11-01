"""
Chat & Conversation Service Orchestrator.
Integrates NLP, Profile State, Hybrid Retrieval, Three-State Eligibility,
Adaptive Questioning, Near-Miss Recommendations, and RAG Generation.
"""
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.nlp.language_detector import LanguageDetector
from backend.nlp.intent_classifier import IntentClassifier
from backend.nlp.entity_extractor import EntityExtractor
from backend.schemas.user_profile import UserProfile
from backend.schemas.chat import ChatMessageRequest, ChatMessageResponse, SourceReference
from backend.schemas.eligibility import SchemeEligibilityResult, EligibilityStatus
from backend.retrieval.hybrid_search import HybridRetriever
from backend.eligibility.adaptive_questioner import AdaptiveQuestioner
from backend.eligibility.near_miss import NearMissRecommender
from backend.rag.generator import ResponseGenerator
from backend.repositories.scheme_repo import SchemeRepository
from backend.models.database import ConversationModel, MessageModel
from backend.core.logging import logger


class ChatService:
    def __init__(self, db: Session, hybrid_retriever: HybridRetriever = None):
        self.db = db
        self.scheme_repo = SchemeRepository(db)
        self.hybrid_retriever = hybrid_retriever or HybridRetriever()
        self.generator = ResponseGenerator()

    def process_message(self, request: ChatMessageRequest) -> ChatMessageResponse:
        session_id = request.conversation_id or str(uuid.uuid4())
        raw_msg = request.message.strip()

        # 1. Language Detection
        detected_lang, lang_conf, is_mixed = LanguageDetector.detect(raw_msg)
        effective_lang = request.language or detected_lang

        # 2. Intent Classification
        intent, intent_conf = IntentClassifier.classify(raw_msg)

        # 3. Entity Extraction
        extracted_entities = EntityExtractor.extract_entities(raw_msg)

        # 4. Profile Management & State Accumulation
        current_profile = request.current_profile or UserProfile()
        conflicts = []
        if extracted_entities:
            # Check for conflicting statements before update
            for field, data in extracted_entities.items():
                curr = getattr(current_profile, field, None)
                if curr is not None and curr != data["value"]:
                    conflicts.append(field)
            EntityExtractor.apply_to_profile(current_profile, extracted_entities)

        # 5. Fetch all verified schemes from DB
        all_schemes = self.scheme_repo.get_all(active_only=True)
        schemes_pool = [
            {
                "scheme_id": s.scheme_id,
                "name": s.name,
                "name_kannada": s.name_kannada,
                "aliases": s.aliases or [],
                "level": s.level,
                "state": s.state,
                "department": s.department,
                "category": s.category,
                "subcategory": s.subcategory,
                "short_description": s.short_description,
                "detailed_description": s.detailed_description,
                "description_kannada": s.description_kannada,
                "benefits_summary": s.benefits_summary,
                "benefits_amount": s.benefits_amount,
                "required_documents": s.required_documents or [],
                "application_process": s.application_process or [],
                "official_portal_url": s.official_portal_url,
                "application_url": s.application_url,
                "source_title": s.source_title,
                "source_excerpt": s.source_excerpt,
                "last_verified_date": s.last_verified_date,
                "rules": [
                    {
                        "criterion_id": r.criterion_id,
                        "name": r.name,
                        "field": r.field,
                        "operator": r.operator,
                        "expected_value": r.expected_value,
                        "is_mandatory": r.is_mandatory,
                        "source_citation": r.source_citation,
                        "description_kannada": r.description_kannada,
                        "clarification_question_en": r.clarification_question_en,
                        "clarification_question_kn": r.clarification_question_kn,
                    }
                    for r in s.rules
                ],
            }
            for s in all_schemes
        ]
        schemes_map = {s["scheme_id"]: s for s in schemes_pool}

        # 6. Hybrid Retrieval & Three-State Eligibility Evaluation
        # Prevent query drift during multi-turn intake by enriching brief answers with profile context
        retrieval_query = raw_msg
        known_attrs = current_profile.get_known_attributes()
        if known_attrs and len(raw_msg.split()) < 4:
            key_context = " ".join(f"{k} {v}" for k, v in known_attrs.items() if k in ("occupation", "state", "residence_type"))
            retrieval_query = f"{raw_msg} {key_context}".strip()

        retrieval_output = self.hybrid_retriever.retrieve_and_evaluate(
            query=retrieval_query,
            profile=current_profile,
            schemes_pool=schemes_pool,
            top_k=8,
        )

        eligible_schemes = retrieval_output["eligible"]
        unknown_schemes = retrieval_output["needs_more_info"]
        ineligible_schemes = retrieval_output["ineligible"]

        # Combined recommended list: First confirmed PASS, then UNKNOWN
        recommended = eligible_schemes + unknown_schemes

        # 7. Adaptive Follow-Up Question Selection
        follow_up_q = None
        follow_up_attr = None
        if settings.ENABLE_ADAPTIVE_QUESTIONING:
            follow_up_q, follow_up_attr = AdaptiveQuestioner.select_next_question(
                candidate_results=recommended,
                profile=current_profile,
                language=effective_lang,
            )

        # 8. Near-Miss Recommendations
        near_misses = []
        if settings.ENABLE_NEAR_MISS_RECOMMENDATIONS and ineligible_schemes and not eligible_schemes:
            near_misses = NearMissRecommender.find_alternatives_for_failed_schemes(
                failed_results=ineligible_schemes,
                all_candidate_schemes=schemes_pool,
                profile=current_profile,
                max_alternatives=3,
            )

        # 9. Grounded RAG Response Generation
        bot_reply = self.generator.generate_response(
            query=raw_msg,
            profile=current_profile,
            recommended_schemes=recommended if recommended else ineligible_schemes,
            schemes_data_map=schemes_map,
            language=effective_lang,
            follow_up_question=follow_up_q,
            near_misses=near_misses,
        )

        # 10. Compile verified source references
        sources_list: List[SourceReference] = []
        for r in (recommended + near_misses)[:5]:
            s_data = schemes_map.get(r.scheme_id, {})
            sources_list.append(
                SourceReference(
                    scheme_id=r.scheme_id,
                    scheme_name=r.scheme_name,
                    official_portal_url=r.official_portal_url or s_data.get("official_portal_url", ""),
                    source_title=s_data.get("source_title", "Official Gazette / Government Portal"),
                    last_verified_date=s_data.get("last_verified_date", "2025-01-01"),
                )
            )

        # 11. Persist Conversation & Messages in DB
        try:
            conv = (
                self.db.query(ConversationModel)
                .filter(ConversationModel.session_id == session_id)
                .first()
            )
            if not conv:
                conv = ConversationModel(
                    session_id=session_id,
                    language=effective_lang,
                    user_profile_snapshot=current_profile.get_known_attributes(),
                )
                self.db.add(conv)
                self.db.flush()
            else:
                conv.user_profile_snapshot = current_profile.get_known_attributes()

            # Record user message
            u_msg = MessageModel(
                conversation_id=session_id,
                sender="user",
                message_text=raw_msg,
                extracted_entities={k: v["value"] for k, v in extracted_entities.items()},
            )
            self.db.add(u_msg)

            # Record assistant reply
            a_msg = MessageModel(
                conversation_id=session_id,
                sender="assistant",
                message_text=bot_reply,
                recommended_scheme_ids=[r.scheme_id for r in recommended],
            )
            self.db.add(a_msg)
            self.db.commit()
        except Exception as e:
            logger.warning(f"Could not persist message in DB: {e}")
            self.db.rollback()

        return ChatMessageResponse(
            reply=bot_reply,
            language=effective_lang,
            detected_language=detected_lang,
            intent=intent,
            conversation_id=session_id,
            extracted_entities={k: v["value"] for k, v in extracted_entities.items()},
            updated_profile=current_profile,
            recommended_schemes=recommended,
            near_miss_schemes=near_misses,
            follow_up_question=follow_up_q,
            follow_up_target_attribute=follow_up_attr,
            sources=sources_list,
            is_llm_generated=(self.generator.provider == "gemini"),
            has_conflicts=bool(conflicts),
            conflicting_fields=conflicts,
        )

    def reset_conversation(self, session_id: str) -> bool:
        """Deletes stored conversation and messages for the given session ID."""
        _, success = self.reset_conversation_detailed(session_id)
        return success

    def reset_conversation_detailed(self, session_id: str | None) -> tuple[int, bool]:
        """
        Deletes stored conversation and messages for the given session ID from SQLite.
        Returns (deleted_message_count, success_boolean).
        """
        try:
            if not session_id:
                deleted_msgs = self.db.query(MessageModel).delete(synchronize_session=False)
                deleted_convs = self.db.query(ConversationModel).delete(synchronize_session=False)
                self.db.commit()
                logger.info(f"Reset all active conversations ({deleted_convs} convs, {deleted_msgs} msgs)")
                return deleted_msgs, True

            deleted_msgs = self.db.query(MessageModel).filter(
                MessageModel.conversation_id == session_id
            ).delete(synchronize_session=False)

            deleted_convs = self.db.query(ConversationModel).filter(
                ConversationModel.session_id == session_id
            ).delete(synchronize_session=False)

            self.db.commit()
            logger.info(f"Reset {deleted_msgs} messages and conversation for session: {session_id}")
            return deleted_msgs, (deleted_convs > 0 or deleted_msgs > 0 or True)
        except Exception as e:
            logger.warning(f"Error resetting conversation {session_id}: {e}")
            self.db.rollback()
            return 0, False
