"""
Enterprise-grade SQLAlchemy models for GenAI Fraud Detection Platform.

Session-Centric Architecture:
- Every uploaded dataset creates ONE Analysis Session
- Every table contains: session_id, user_id, project_id, created_at, updated_at, deleted_at
- Soft delete only (deleted_at for audit trail, never permanent delete)
- All queries MUST filter by session_id + user_id + project_id
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Any

from sqlalchemy import (
    JSON,
    Enum,
    ForeignKey,
    String,
    Text,
    Boolean,
    Integer,
    Float,
    DateTime,
    Index,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.common.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.backend.db.base import Base


# ============================================================================
# ENUMS
# ============================================================================


class RoleEnum(str, PyEnum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class ProjectStatus(str, PyEnum):
    CREATED = "created"
    ACTIVE = "active"
    ARCHIVED = "archived"


class UploadStatus(str, PyEnum):
    RECEIVED = "received"
    PARSING = "parsing"
    VALIDATED = "validated"
    FAILED = "failed"


class ValidationStatus(str, PyEnum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


class DataProcessingStatus(str, PyEnum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionStatus(str, PyEnum):
    INITIALIZED = "initialized"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PredictedLabel(str, PyEnum):
    FRAUD = "fraud"
    REVIEW = "review"
    SAFE = "safe"


class InsightPriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReportType(str, PyEnum):
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    BUSINESS = "business"


class ReportStatus(str, PyEnum):
    DRAFT = "draft"
    COMPLETED = "completed"
    EXPORTED = "exported"


class ChatIntent(str, PyEnum):
    FRAUD_COUNT = "fraud_count"
    RISK_ANALYSIS = "risk_analysis"
    DASHBOARD_EXPLAIN = "dashboard_explain"
    REPORT_EXPLAIN = "report_explain"
    FOLLOW_UP = "follow_up"


class AnswerSource(str, PyEnum):
    RULE_BASED = "rule_based"
    MODEL_BASED = "model_based"
    RETRIEVAL = "retrieval"


class FeedbackType(str, PyEnum):
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"
    CORRECTED_LABEL = "corrected_label"


class FeedbackStatus(str, PyEnum):
    PENDING_REVIEW = "pending_review"
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"


class AuditActionType(str, PyEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    EXPORT = "export"


# ============================================================================
# USER & PROJECT MODELS
# ============================================================================


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User account model.
    Stores authentication, profile, and role information.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, native_enum=False), default=RoleEnum.ANALYST, nullable=False)
    auth_provider: Mapped[str] = mapped_column(String(64), default="local", nullable=False)
    auth_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    analysis_sessions = relationship("AnalysisSession", back_populates="user")
    uploads = relationship("UploadRecord", back_populates="user")
    validated_data = relationship("ValidatedData", back_populates="user")
    cleaned_data = relationship("CleanedData", back_populates="user")
    processed_data = relationship("ProcessedData", back_populates="user")
    fraud_results = relationship("FraudResult", back_populates="user")
    ai_insights = relationship("AIInsight", back_populates="user")
    dashboards = relationship("DashboardSnapshot", back_populates="user")
    reports = relationship("ReportArtifact", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    feedback = relationship("AnalystFeedback", back_populates="user")
    learning_datasets = relationship("LearningDataset", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
    settings = relationship("UserSetting", back_populates="user")

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_active", "is_active"),
    )


class Project(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Project model.
    One user can have multiple projects.
    Each project can have multiple analysis sessions (one per upload).
    """

    __tablename__ = "projects"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus, native_enum=False), default=ProjectStatus.CREATED, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="projects", foreign_keys=[owner_id])
    analysis_sessions = relationship("AnalysisSession", back_populates="project")
    uploads = relationship("UploadRecord", back_populates="project")
    validated_data = relationship("ValidatedData", back_populates="project")
    cleaned_data = relationship("CleanedData", back_populates="project")
    processed_data = relationship("ProcessedData", back_populates="project")
    fraud_results = relationship("FraudResult", back_populates="project")
    ai_insights = relationship("AIInsight", back_populates="project")
    dashboards = relationship("DashboardSnapshot", back_populates="project")
    reports = relationship("ReportArtifact", back_populates="project")
    chat_messages = relationship("ChatMessage", back_populates="project")
    feedback = relationship("AnalystFeedback", back_populates="project")
    learning_datasets = relationship("LearningDataset", back_populates="project")
    settings = relationship("UserSetting", back_populates="project")

    __table_args__ = (
        Index("idx_projects_owner", "owner_id", "created_at"),
        UniqueConstraint("owner_id", "name", name="uk_projects_owner_name"),
    )


# ============================================================================
# ANALYSIS SESSION - THE HEART OF THE SYSTEM
# ============================================================================


class AnalysisSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Analysis Session model.
    Every uploaded dataset creates ONE unique session that isolates all data.
    Session ID is the primary isolation key across all tables.
    """

    __tablename__ = "analysis_sessions"

    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    upload_id: Mapped[str] = mapped_column(ForeignKey("uploads.id"), nullable=False)
    session_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus, native_enum=False), default=SessionStatus.INITIALIZED, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str | None] = mapped_column(Text)
    session_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="analysis_sessions")
    user = relationship("User", back_populates="analysis_sessions")
    upload = relationship("UploadRecord", back_populates="analysis_session")
    validated_data = relationship("ValidatedData", back_populates="analysis_session")
    cleaned_data = relationship("CleanedData", back_populates="analysis_session")
    processed_data = relationship("ProcessedData", back_populates="analysis_session")
    fraud_results = relationship("FraudResult", back_populates="analysis_session")
    ai_insights = relationship("AIInsight", back_populates="analysis_session")
    dashboards = relationship("DashboardSnapshot", back_populates="analysis_session")
    dashboard_cards = relationship("DashboardCard", back_populates="analysis_session")
    dashboard_charts = relationship("DashboardChart", back_populates="analysis_session")
    dashboard_tables = relationship("DashboardTable", back_populates="analysis_session")
    reports = relationship("ReportArtifact", back_populates="analysis_session")
    chat_messages = relationship("ChatMessage", back_populates="analysis_session")
    feedback = relationship("AnalystFeedback", back_populates="analysis_session")
    learning_dataset = relationship("LearningDataset", back_populates="analysis_session", uselist=False)

    __table_args__ = (
        Index("idx_sessions_project_user", "project_id", "user_id", "created_at"),
        Index("idx_sessions_status", "status"),
        UniqueConstraint("upload_id", name="uk_sessions_upload_id"),
    )


# ============================================================================
# DATA PIPELINE - UPLOAD → VALIDATION → CLEANING → PROCESSING
# ============================================================================


class UploadRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Upload record model.
    Tracks original file uploads per session.
    """

    __tablename__ = "uploads"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer)
    column_count: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[UploadStatus] = mapped_column(Enum(UploadStatus, native_enum=False), default=UploadStatus.RECEIVED, nullable=False)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="upload")
    project = relationship("Project", back_populates="uploads")
    user = relationship("User", back_populates="uploads")

    __table_args__ = (
        Index("idx_uploads_session", "session_id", "project_id", "user_id"),
        Index("idx_uploads_project", "project_id"),
        Index("idx_uploads_status", "status"),
    )


class ValidatedData(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Validated data model.
    Stores validation results and rules applied to uploaded dataset.
    """

    __tablename__ = "validated_data"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    upload_id: Mapped[str] = mapped_column(ForeignKey("uploads.id"), nullable=False)
    validation_rules: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    validation_errors: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    valid_rows: Mapped[int] = mapped_column(Integer, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_rows: Mapped[int] = mapped_column(Integer, default=0)
    data_profile: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[ValidationStatus] = mapped_column(Enum(ValidationStatus, native_enum=False), default=ValidationStatus.PENDING, nullable=False)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="validated_data")
    project = relationship("Project", back_populates="validated_data")
    user = relationship("User", back_populates="validated_data")

    __table_args__ = (
        Index("idx_validated_data_session", "session_id", "project_id", "user_id"),
        Index("idx_validated_data_status", "status"),
    )


class CleanedData(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Cleaned data model.
    Stores cleaned and transformed dataset path and metadata.
    """

    __tablename__ = "cleaned_data"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    validated_data_id: Mapped[str] = mapped_column(ForeignKey("validated_data.id"), nullable=False)
    parquet_path: Mapped[str] = mapped_column(Text, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    transformations_applied: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    quality_metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[DataProcessingStatus] = mapped_column(Enum(DataProcessingStatus, native_enum=False), default=DataProcessingStatus.PROCESSING, nullable=False)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="cleaned_data")
    project = relationship("Project", back_populates="cleaned_data")
    user = relationship("User", back_populates="cleaned_data")

    __table_args__ = (
        Index("idx_cleaned_data_session", "session_id", "project_id", "user_id"),
        Index("idx_cleaned_data_status", "status"),
    )


class ProcessedData(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Processed data model.
    Stores feature-engineered dataset path and metadata.
    """

    __tablename__ = "processed_data"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    cleaned_data_id: Mapped[str] = mapped_column(ForeignKey("cleaned_data.id"), nullable=False)
    parquet_path: Mapped[str] = mapped_column(Text, nullable=False)
    row_count: Mapped[int] = mapped_column(Integer, nullable=False)
    feature_engineered_columns: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    scaling_parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    feature_importance: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[DataProcessingStatus] = mapped_column(Enum(DataProcessingStatus, native_enum=False), default=DataProcessingStatus.PROCESSING, nullable=False)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="processed_data")
    project = relationship("Project", back_populates="processed_data")
    user = relationship("User", back_populates="processed_data")

    __table_args__ = (
        Index("idx_processed_data_session", "session_id", "project_id", "user_id"),
        Index("idx_processed_data_status", "status"),
    )


# ============================================================================
# FRAUD DETECTION & ML RESULTS
# ============================================================================


class FraudResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Fraud result model.
    Stores fraud predictions, risk scores, confidence, and explainability.
    """

    __tablename__ = "fraud_results"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    processed_data_id: Mapped[str] = mapped_column(ForeignKey("processed_data.id"), nullable=False)
    row_identifier: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_label: Mapped[PredictedLabel] = mapped_column(Enum(PredictedLabel, native_enum=False), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    model_decision_path: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    shap_values: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    feature_contributions: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    explanation: Mapped[str | None] = mapped_column(Text)
    raw_record: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="fraud_results")
    project = relationship("Project", back_populates="fraud_results")
    user = relationship("User", back_populates="fraud_results")
    feedback = relationship("AnalystFeedback", back_populates="fraud_result")

    __table_args__ = (
        Index("idx_fraud_results_session", "session_id", "project_id", "user_id"),
        Index("idx_fraud_results_label_risk", "predicted_label", "risk_score"),
        CheckConstraint("risk_score BETWEEN 0 AND 1", name="chk_fraud_risk_score"),
        CheckConstraint("confidence_score BETWEEN 0 AND 1", name="chk_fraud_confidence"),
    )


class AIInsight(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    AI Insight model.
    Stores generated AI observations and patterns.
    """

    __tablename__ = "ai_insights"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    insight_category: Mapped[str] = mapped_column(String(255), nullable=False)
    insight_text: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    priority: Mapped[InsightPriority] = mapped_column(Enum(InsightPriority, native_enum=False), default=InsightPriority.MEDIUM)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="ai_insights")
    project = relationship("Project", back_populates="ai_insights")
    user = relationship("User", back_populates="ai_insights")

    __table_args__ = (
        Index("idx_ai_insights_session", "session_id", "project_id", "priority"),
        CheckConstraint("confidence BETWEEN 0 AND 1", name="chk_insight_confidence"),
    )


# ============================================================================
# DASHBOARD & VISUALIZATION
# ============================================================================


class DashboardSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Dashboard model.
    Stores dashboard metadata and aggregated KPIs per session.
    """

    __tablename__ = "dashboard"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    kpi_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    summary_metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="dashboards")
    project = relationship("Project", back_populates="dashboards")
    user = relationship("User", back_populates="dashboards")
    cards = relationship("DashboardCard", back_populates="dashboard")
    charts = relationship("DashboardChart", back_populates="dashboard")
    tables = relationship("DashboardTable", back_populates="dashboard")

    __table_args__ = (
        Index("idx_dashboard_session", "session_id", "project_id", "last_updated"),
    )


class DashboardCard(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Dashboard Card model.
    KPI cards displayed on dashboard.
    """

    __tablename__ = "dashboard_cards"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    dashboard_id: Mapped[str] = mapped_column(ForeignKey("dashboard.id", ondelete="CASCADE"), nullable=False, index=True)
    card_name: Mapped[str] = mapped_column(String(255), nullable=False)
    card_type: Mapped[str] = mapped_column(String(64), nullable=False)
    card_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="dashboard_cards")
    dashboard = relationship("DashboardSnapshot", back_populates="cards")

    __table_args__ = (
        Index("idx_dashboard_cards_session", "session_id", "dashboard_id"),
    )


class DashboardChart(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Dashboard Chart model.
    Charts displayed on dashboard.
    """

    __tablename__ = "dashboard_charts"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    dashboard_id: Mapped[str] = mapped_column(ForeignKey("dashboard.id", ondelete="CASCADE"), nullable=False, index=True)
    chart_name: Mapped[str] = mapped_column(String(255), nullable=False)
    chart_type: Mapped[str] = mapped_column(String(64), nullable=False)
    chart_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    chart_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="dashboard_charts")
    dashboard = relationship("DashboardSnapshot", back_populates="charts")

    __table_args__ = (
        Index("idx_dashboard_charts_session", "session_id", "dashboard_id"),
    )


class DashboardTable(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Dashboard Table model.
    Fraud tables displayed on dashboard.
    """

    __tablename__ = "dashboard_tables"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    dashboard_id: Mapped[str] = mapped_column(ForeignKey("dashboard.id", ondelete="CASCADE"), nullable=False, index=True)
    table_name: Mapped[str] = mapped_column(String(255), nullable=False)
    table_columns: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    table_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="dashboard_tables")
    dashboard = relationship("DashboardSnapshot", back_populates="tables")

    __table_args__ = (
        Index("idx_dashboard_tables_session", "session_id", "dashboard_id"),
    )


# ============================================================================
# REPORTS
# ============================================================================


class ReportArtifact(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Report model.
    Stores generated reports (executive, technical, business).
    """

    __tablename__ = "reports"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type: Mapped[ReportType] = mapped_column(Enum(ReportType, native_enum=False), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    executive_summary: Mapped[str | None] = mapped_column(Text)
    findings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    recommendations: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus, native_enum=False), default=ReportStatus.DRAFT, nullable=False)
    export_path: Mapped[str | None] = mapped_column(Text)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="reports")
    project = relationship("Project", back_populates="reports")
    user = relationship("User", back_populates="reports")

    __table_args__ = (
        Index("idx_reports_session", "session_id", "project_id", "created_at"),
        Index("idx_reports_status", "status"),
    )


# ============================================================================
# CHAT & CONVERSATION
# ============================================================================


class ChatMessage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Chat Message model.
    Stores conversation history per session.
    Session-isolated: all chats belong to one session only.
    """

    __tablename__ = "chat_messages"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[ChatIntent] = mapped_column(Enum(ChatIntent, native_enum=False), default=ChatIntent.FRAUD_COUNT, nullable=False)
    context_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    answer_source: Mapped[AnswerSource] = mapped_column(Enum(AnswerSource, native_enum=False), default=AnswerSource.RULE_BASED, nullable=False)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="chat_messages")
    project = relationship("Project", back_populates="chat_messages")
    user = relationship("User", back_populates="chat_messages")

    __table_args__ = (
        Index("idx_chat_messages_session", "session_id", "project_id", "created_at"),
        Index("idx_chat_messages_intent", "intent"),
    )


# ============================================================================
# FEEDBACK & MODEL IMPROVEMENT
# ============================================================================


class AnalystFeedback(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Analyst Feedback model.
    Stores corrections, false positives/negatives for model retraining.
    """

    __tablename__ = "feedback"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    fraud_result_id: Mapped[str] = mapped_column(ForeignKey("fraud_results.id"), nullable=False)
    feedback_type: Mapped[FeedbackType] = mapped_column(Enum(FeedbackType, native_enum=False), nullable=False)
    corrected_label: Mapped[str | None] = mapped_column(String(64))
    comment: Mapped[str | None] = mapped_column(Text)
    attached_evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[FeedbackStatus] = mapped_column(Enum(FeedbackStatus, native_enum=False), default=FeedbackStatus.PENDING_REVIEW, nullable=False)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="feedback")
    project = relationship("Project", back_populates="feedback")
    user = relationship("User", back_populates="feedback")
    fraud_result = relationship("FraudResult", back_populates="feedback")

    __table_args__ = (
        Index("idx_feedback_session", "session_id", "project_id", "status"),
        Index("idx_feedback_type", "feedback_type"),
    )


class LearningDataset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Learning Dataset model.
    Stores validated feedback for model retraining.
    One per analysis session.
    """

    __tablename__ = "learning_dataset"

    session_id: Mapped[str] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    feedback_item_count: Mapped[int] = mapped_column(Integer, default=0)
    dataset_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    parquet_path: Mapped[str | None] = mapped_column(Text)

    # Relationships
    analysis_session = relationship("AnalysisSession", back_populates="learning_dataset")
    project = relationship("Project", back_populates="learning_datasets")
    user = relationship("User", back_populates="learning_datasets")

    __table_args__ = (
        Index("idx_learning_dataset_session", "session_id", "project_id"),
    )


# ============================================================================
# AUDIT & LOGGING
# ============================================================================


class AuditLog(Base, UUIDPrimaryKeyMixin):
    """
    Audit Log model.
    Tracks all user actions for compliance and debugging.
    """

    __tablename__ = "audit_log"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="SET NULL"), index=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    action: Mapped[AuditActionType] = mapped_column(Enum(AuditActionType, native_enum=False), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(128), nullable=False)
    before_value: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    after_value: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    status: Mapped[str] = mapped_column(String(32), default="success")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_log_session", "session_id", "user_id", "created_at"),
        Index("idx_audit_log_resource", "resource_type", "resource_id", "created_at"),
    )


# ============================================================================
# SETTINGS & CONFIGURATION
# ============================================================================


class UserSetting(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    User Setting model.
    Stores user and project-level configuration.
    """

    __tablename__ = "user_settings"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    setting_key: Mapped[str] = mapped_column(String(255), nullable=False)
    setting_value: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Relationships
    project = relationship("Project", back_populates="settings")
    user = relationship("User", back_populates="settings")

    __table_args__ = (
        Index("idx_user_settings_user_key", "user_id", "setting_key"),
        UniqueConstraint("user_id", "project_id", "setting_key", name="uk_user_settings_key"),
    )


# ============================================================================
# LOGS
# ============================================================================


class AppLog(Base, UUIDPrimaryKeyMixin):
    """
    Application Log model.
    Stores API, AI, error, warning, and performance logs.
    """

    __tablename__ = "app_logs"

    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="SET NULL"), index=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("analysis_sessions.id", ondelete="SET NULL"), index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    log_level: Mapped[str] = mapped_column(String(32), nullable=False)
    log_category: Mapped[str] = mapped_column(String(128), nullable=False)
    log_message: Mapped[str] = mapped_column(Text, nullable=False)
    log_context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    performance_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index("idx_app_logs_session", "session_id", "created_at"),
        Index("idx_app_logs_category_level", "log_category", "log_level", "created_at"),
    )
