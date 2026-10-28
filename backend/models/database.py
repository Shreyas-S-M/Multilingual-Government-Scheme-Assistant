"""
SQLAlchemy 2.0 ORM Database Models.
Normalized relational schemas for schemes, eligibility rules, official sources,
conversations, messages, user feedback, and administrative audit logs.
"""
from datetime import datetime
from typing import List, Optional, Any
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SchemeModel(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_id = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    name_kannada = Column(String(255), nullable=True)
    aliases = Column(JSON, default=list)  # List[str]
    level = Column(String(32), nullable=False, index=True)  # 'central' or 'state'
    state = Column(String(64), nullable=True, index=True)
    department = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, index=True)
    subcategory = Column(String(64), nullable=True)
    short_description = Column(Text, nullable=False)
    detailed_description = Column(Text, nullable=False)
    description_kannada = Column(Text, nullable=True)

    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    max_income = Column(Float, nullable=True)
    eligible_genders = Column(JSON, default=lambda: ["all"])
    eligible_categories = Column(JSON, default=lambda: ["all"])
    target_occupations = Column(JSON, default=lambda: ["all"])

    benefits_summary = Column(Text, nullable=False)
    benefits_amount = Column(String(128), nullable=True)
    required_documents = Column(JSON, default=list)
    application_process = Column(JSON, default=list)

    official_portal_url = Column(String(512), nullable=False)
    application_url = Column(String(512), nullable=True)
    source_title = Column(String(255), nullable=False)
    source_excerpt = Column(Text, nullable=False)

    effective_date = Column(String(32), nullable=True)
    last_verified_date = Column(String(32), nullable=False)
    source_reliability = Column(String(64), default="official_portal")
    status = Column(String(32), default="active", index=True)
    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    rules = relationship("CriterionRuleModel", back_populates="scheme", cascade="all, delete-orphan")
    sources = relationship("SchemeSourceModel", back_populates="scheme", cascade="all, delete-orphan")


class CriterionRuleModel(Base):
    __tablename__ = "criterion_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    criterion_id = Column(String(64), nullable=False, index=True)
    scheme_id = Column(String(64), ForeignKey("schemes.scheme_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    field = Column(String(64), nullable=False, index=True)
    operator = Column(String(32), nullable=False)
    expected_value = Column(JSON, nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    source_citation = Column(Text, nullable=False)
    description_kannada = Column(Text, nullable=True)
    clarification_question_en = Column(Text, nullable=True)
    clarification_question_kn = Column(Text, nullable=True)

    scheme = relationship("SchemeModel", back_populates="rules")


class SchemeSourceModel(Base):
    __tablename__ = "scheme_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scheme_id = Column(String(64), ForeignKey("schemes.scheme_id", ondelete="CASCADE"), nullable=False, index=True)
    source_url = Column(String(512), nullable=False)
    source_title = Column(String(255), nullable=False)
    last_checked_date = Column(String(32), nullable=False)
    verification_status = Column(String(32), default="verified", index=True)
    verification_notes = Column(Text, nullable=True)

    scheme = relationship("SchemeModel", back_populates="sources")


class ConversationModel(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), unique=True, nullable=False, index=True)
    language = Column(String(16), default="en")
    user_profile_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(64), ForeignKey("conversations.session_id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(16), nullable=False)  # 'user', 'assistant'
    message_text = Column(Text, nullable=False)
    extracted_entities = Column(JSON, nullable=True)
    recommended_scheme_ids = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("ConversationModel", back_populates="messages")


class UserFeedbackModel(Base):
    __tablename__ = "user_feedbacks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(64), nullable=True, index=True)
    scheme_id = Column(String(64), nullable=True, index=True)
    rating = Column(Integer, nullable=False)  # e.g. 1 to 5
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String(64), nullable=False, index=True)
    entity_type = Column(String(64), nullable=False)
    entity_id = Column(String(64), nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
