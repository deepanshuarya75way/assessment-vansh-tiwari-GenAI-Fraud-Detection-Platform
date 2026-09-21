"""
Session-Aware Repository Layer

All repositories follow the session-centric pattern:
- Every query filters by (session_id, user_id, project_id)
- Soft delete only: never permanent delete
- Transaction-safe with proper commit/rollback
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.backend.db.enterprise_models import (
    AnalysisSession,
    UploadRecord,
    ValidatedData,
    CleanedData,
    ProcessedData,
    FraudResult,
    AIInsight,
    DashboardSnapshot,
    DashboardCard,
    DashboardChart,
    DashboardTable,
    ReportArtifact,
    ChatMessage,
    AnalystFeedback,
    LearningDataset,
    AuditLog,
    AppLog,
)

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Base repository with session-centric query patterns.
    Every query MUST include session_id + user_id + project_id filtering.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    @abstractmethod
    def model_class(self) -> type[T]:
        """Return the SQLAlchemy model class."""
        pass

    def add(self, entity: T) -> T:
        """Add entity and flush (not commit)."""
        self.session.add(entity)
        self.session.flush()
        return entity

    def delete_soft(self, entity: T) -> None:
        """Soft delete: set deleted_at timestamp."""
        from datetime import datetime, timezone

        entity.deleted_at = datetime.now(timezone.utc)
        self.session.flush()

    def list_session(self, session_id: str, user_id: str, project_id: str, limit: int = 1000) -> list[T]:
        """
        Retrieve all records for a session (soft-delete aware).
        """
        stmt = (
            select(self.model_class())
            .where(
                self.model_class().session_id == session_id,
                self.model_class().user_id == user_id,
                self.model_class().project_id == project_id,
                self.model_class().deleted_at.is_(None),
            )
            .order_by(desc(self.model_class().created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def list_session_paginated(
        self, session_id: str, user_id: str, project_id: str, skip: int = 0, limit: int = 50
    ) -> tuple[list[T], int]:
        """
        Retrieve paginated records for a session with total count.
        """
        stmt_count = select(func.count()).select_from(self.model_class()).where(
            self.model_class().session_id == session_id,
            self.model_class().user_id == user_id,
            self.model_class().project_id == project_id,
            self.model_class().deleted_at.is_(None),
        )
        total = self.session.scalar(stmt_count) or 0

        stmt = (
            select(self.model_class())
            .where(
                self.model_class().session_id == session_id,
                self.model_class().user_id == user_id,
                self.model_class().project_id == project_id,
                self.model_class().deleted_at.is_(None),
            )
            .order_by(desc(self.model_class().created_at))
            .offset(skip)
            .limit(limit)
        )
        items = list(self.session.scalars(stmt))
        return items, total

    def count_session(self, session_id: str, user_id: str, project_id: str) -> int:
        """Count records in session (soft-delete aware)."""
        stmt = select(func.count()).select_from(self.model_class()).where(
            self.model_class().session_id == session_id,
            self.model_class().user_id == user_id,
            self.model_class().project_id == project_id,
            self.model_class().deleted_at.is_(None),
        )
        return self.session.scalar(stmt) or 0


# ============================================================================
# SPECIFIC REPOSITORIES
# ============================================================================


class AnalysisSessionRepository(BaseRepository[AnalysisSession]):
    """Repository for Analysis Sessions."""

    def model_class(self) -> type[AnalysisSession]:
        return AnalysisSession

    def get_by_id(self, session_id: str) -> AnalysisSession | None:
        """Retrieve session by ID."""
        return self.session.scalar(select(AnalysisSession).where(AnalysisSession.id == session_id))

    def list_by_project(self, project_id: str, user_id: str, limit: int = 50) -> list[AnalysisSession]:
        """List all sessions for a project."""
        stmt = (
            select(AnalysisSession)
            .where(
                AnalysisSession.project_id == project_id,
                AnalysisSession.user_id == user_id,
                AnalysisSession.deleted_at.is_(None),
            )
            .order_by(desc(AnalysisSession.created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def latest_session(self, project_id: str, user_id: str) -> AnalysisSession | None:
        """Get the most recent session for a project."""
        stmt = (
            select(AnalysisSession)
            .where(
                AnalysisSession.project_id == project_id,
                AnalysisSession.user_id == user_id,
                AnalysisSession.deleted_at.is_(None),
            )
            .order_by(desc(AnalysisSession.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)


class UploadRepository(BaseRepository[UploadRecord]):
    """Repository for Uploads per session."""

    def model_class(self) -> type[UploadRecord]:
        return UploadRecord

    def get_by_checksum(self, session_id: str, user_id: str, project_id: str, checksum: str) -> UploadRecord | None:
        """Check for duplicate uploads by checksum."""
        stmt = select(UploadRecord).where(
            UploadRecord.session_id == session_id,
            UploadRecord.user_id == user_id,
            UploadRecord.project_id == project_id,
            UploadRecord.checksum == checksum,
            UploadRecord.deleted_at.is_(None),
        )
        return self.session.scalar(stmt)


class ValidatedDataRepository(BaseRepository[ValidatedData]):
    """Repository for Validated Data per session."""

    def model_class(self) -> type[ValidatedData]:
        return ValidatedData

    def get_latest(self, session_id: str, user_id: str, project_id: str) -> ValidatedData | None:
        """Get the latest validated data for a session."""
        stmt = (
            select(ValidatedData)
            .where(
                ValidatedData.session_id == session_id,
                ValidatedData.user_id == user_id,
                ValidatedData.project_id == project_id,
                ValidatedData.deleted_at.is_(None),
            )
            .order_by(desc(ValidatedData.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)


class CleanedDataRepository(BaseRepository[CleanedData]):
    """Repository for Cleaned Data per session."""

    def model_class(self) -> type[CleanedData]:
        return CleanedData

    def get_latest(self, session_id: str, user_id: str, project_id: str) -> CleanedData | None:
        """Get the latest cleaned data for a session."""
        stmt = (
            select(CleanedData)
            .where(
                CleanedData.session_id == session_id,
                CleanedData.user_id == user_id,
                CleanedData.project_id == project_id,
                CleanedData.deleted_at.is_(None),
            )
            .order_by(desc(CleanedData.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)


class ProcessedDataRepository(BaseRepository[ProcessedData]):
    """Repository for Processed Data per session."""

    def model_class(self) -> type[ProcessedData]:
        return ProcessedData

    def get_latest(self, session_id: str, user_id: str, project_id: str) -> ProcessedData | None:
        """Get the latest processed data for a session."""
        stmt = (
            select(ProcessedData)
            .where(
                ProcessedData.session_id == session_id,
                ProcessedData.user_id == user_id,
                ProcessedData.project_id == project_id,
                ProcessedData.deleted_at.is_(None),
            )
            .order_by(desc(ProcessedData.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)


class FraudResultRepository(BaseRepository[FraudResult]):
    """Repository for Fraud Results per session."""

    def model_class(self) -> type[FraudResult]:
        return FraudResult

    def list_by_label(self, session_id: str, user_id: str, project_id: str, label: str, limit: int = 1000) -> list[FraudResult]:
        """List fraud results by predicted label (fraud, review, safe)."""
        stmt = (
            select(FraudResult)
            .where(
                FraudResult.session_id == session_id,
                FraudResult.user_id == user_id,
                FraudResult.project_id == project_id,
                FraudResult.predicted_label == label,
                FraudResult.deleted_at.is_(None),
            )
            .order_by(desc(FraudResult.risk_score))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def list_high_risk(self, session_id: str, user_id: str, project_id: str, threshold: float = 0.7, limit: int = 100) -> list[FraudResult]:
        """List high-risk fraud results."""
        stmt = (
            select(FraudResult)
            .where(
                FraudResult.session_id == session_id,
                FraudResult.user_id == user_id,
                FraudResult.project_id == project_id,
                FraudResult.risk_score >= threshold,
                FraudResult.deleted_at.is_(None),
            )
            .order_by(desc(FraudResult.risk_score))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def get_statistics(self, session_id: str, user_id: str, project_id: str) -> dict[str, int]:
        """Get fraud result statistics for a session."""
        total = self.count_session(session_id, user_id, project_id)
        fraud_count = self.session.scalar(
            select(func.count()).select_from(FraudResult).where(
                FraudResult.session_id == session_id,
                FraudResult.user_id == user_id,
                FraudResult.project_id == project_id,
                FraudResult.predicted_label == "fraud",
                FraudResult.deleted_at.is_(None),
            )
        ) or 0
        review_count = self.session.scalar(
            select(func.count()).select_from(FraudResult).where(
                FraudResult.session_id == session_id,
                FraudResult.user_id == user_id,
                FraudResult.project_id == project_id,
                FraudResult.predicted_label == "review",
                FraudResult.deleted_at.is_(None),
            )
        ) or 0
        safe_count = total - fraud_count - review_count

        return {
            "total": total,
            "fraud": fraud_count,
            "review": review_count,
            "safe": safe_count,
        }


class AIInsightRepository(BaseRepository[AIInsight]):
    """Repository for AI Insights per session."""

    def model_class(self) -> type[AIInsight]:
        return AIInsight

    def list_by_priority(self, session_id: str, user_id: str, project_id: str, priority: str, limit: int = 50) -> list[AIInsight]:
        """List insights by priority level."""
        stmt = (
            select(AIInsight)
            .where(
                AIInsight.session_id == session_id,
                AIInsight.user_id == user_id,
                AIInsight.project_id == project_id,
                AIInsight.priority == priority,
                AIInsight.deleted_at.is_(None),
            )
            .order_by(desc(AIInsight.created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))


class DashboardRepository(BaseRepository[DashboardSnapshot]):
    """Repository for Dashboards per session."""

    def model_class(self) -> type[DashboardSnapshot]:
        return DashboardSnapshot

    def get_latest(self, session_id: str, user_id: str, project_id: str) -> DashboardSnapshot | None:
        """Get the most recent dashboard for a session."""
        stmt = (
            select(DashboardSnapshot)
            .where(
                DashboardSnapshot.session_id == session_id,
                DashboardSnapshot.user_id == user_id,
                DashboardSnapshot.project_id == project_id,
                DashboardSnapshot.deleted_at.is_(None),
            )
            .order_by(desc(DashboardSnapshot.last_updated))
            .limit(1)
        )
        return self.session.scalar(stmt)


class DashboardCardRepository(BaseRepository[DashboardCard]):
    """Repository for Dashboard Cards."""

    def model_class(self) -> type[DashboardCard]:
        return DashboardCard


class DashboardChartRepository(BaseRepository[DashboardChart]):
    """Repository for Dashboard Charts."""

    def model_class(self) -> type[DashboardChart]:
        return DashboardChart


class DashboardTableRepository(BaseRepository[DashboardTable]):
    """Repository for Dashboard Tables."""

    def model_class(self) -> type[DashboardTable]:
        return DashboardTable


class ReportRepository(BaseRepository[ReportArtifact]):
    """Repository for Reports per session."""

    def model_class(self) -> type[ReportArtifact]:
        return ReportArtifact

    def get_latest(self, session_id: str, user_id: str, project_id: str, report_type: str | None = None) -> ReportArtifact | None:
        """Get the most recent report for a session."""
        stmt = select(ReportArtifact).where(
            ReportArtifact.session_id == session_id,
            ReportArtifact.user_id == user_id,
            ReportArtifact.project_id == project_id,
            ReportArtifact.deleted_at.is_(None),
        )
        if report_type:
            stmt = stmt.where(ReportArtifact.report_type == report_type)
        stmt = stmt.order_by(desc(ReportArtifact.created_at)).limit(1)
        return self.session.scalar(stmt)


class ChatMessageRepository(BaseRepository[ChatMessage]):
    """Repository for Chat Messages per session."""

    def model_class(self) -> type[ChatMessage]:
        return ChatMessage

    def list_by_intent(self, session_id: str, user_id: str, project_id: str, intent: str, limit: int = 50) -> list[ChatMessage]:
        """List chat messages by intent."""
        stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session_id,
                ChatMessage.user_id == user_id,
                ChatMessage.project_id == project_id,
                ChatMessage.intent == intent,
                ChatMessage.deleted_at.is_(None),
            )
            .order_by(desc(ChatMessage.created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))


class FeedbackRepository(BaseRepository[AnalystFeedback]):
    """Repository for Analyst Feedback per session."""

    def model_class(self) -> type[AnalystFeedback]:
        return AnalystFeedback

    def list_by_status(self, session_id: str, user_id: str, project_id: str, status: str, limit: int = 100) -> list[AnalystFeedback]:
        """List feedback by status."""
        stmt = (
            select(AnalystFeedback)
            .where(
                AnalystFeedback.session_id == session_id,
                AnalystFeedback.user_id == user_id,
                AnalystFeedback.project_id == project_id,
                AnalystFeedback.status == status,
                AnalystFeedback.deleted_at.is_(None),
            )
            .order_by(desc(AnalystFeedback.created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))


class LearningDatasetRepository(BaseRepository[LearningDataset]):
    """Repository for Learning Datasets per session."""

    def model_class(self) -> type[LearningDataset]:
        return LearningDataset

    def get_by_session(self, session_id: str) -> LearningDataset | None:
        """Get learning dataset for a session (1-to-1 relationship)."""
        return self.session.scalar(select(LearningDataset).where(LearningDataset.session_id == session_id))


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository for Audit Logs."""

    def model_class(self) -> type[AuditLog]:
        return AuditLog

    def list_by_session(self, session_id: str, limit: int = 1000) -> list[AuditLog]:
        """List audit logs for a session."""
        stmt = (
            select(AuditLog)
            .where(AuditLog.session_id == session_id)
            .order_by(desc(AuditLog.created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def list_by_user(self, user_id: str, limit: int = 1000) -> list[AuditLog]:
        """List audit logs for a user."""
        stmt = select(AuditLog).where(AuditLog.user_id == user_id).order_by(desc(AuditLog.created_at)).limit(limit)
        return list(self.session.scalars(stmt))


class AppLogRepository(BaseRepository[AppLog]):
    """Repository for Application Logs."""

    def model_class(self) -> type[AppLog]:
        return AppLog

    def list_by_session(self, session_id: str, limit: int = 1000) -> list[AppLog]:
        """List logs for a session."""
        stmt = (
            select(AppLog)
            .where(AppLog.session_id == session_id)
            .order_by(desc(AppLog.created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def list_by_category(self, category: str, limit: int = 500) -> list[AppLog]:
        """List logs by category."""
        stmt = select(AppLog).where(AppLog.log_category == category).order_by(desc(AppLog.created_at)).limit(limit)
        return list(self.session.scalars(stmt))


# ============================================================================
# REPOSITORY FACTORY / SERVICE
# ============================================================================


class SessionRepositories:
    """
    Factory providing all repositories for session-based operations.
    Use this in services to ensure consistent session-scoped queries.
    """

    def __init__(self, db_session: Session) -> None:
        self.db = db_session
        self.analysis_sessions = AnalysisSessionRepository(db_session)
        self.uploads = UploadRepository(db_session)
        self.validated_data = ValidatedDataRepository(db_session)
        self.cleaned_data = CleanedDataRepository(db_session)
        self.processed_data = ProcessedDataRepository(db_session)
        self.fraud_results = FraudResultRepository(db_session)
        self.ai_insights = AIInsightRepository(db_session)
        self.dashboards = DashboardRepository(db_session)
        self.dashboard_cards = DashboardCardRepository(db_session)
        self.dashboard_charts = DashboardChartRepository(db_session)
        self.dashboard_tables = DashboardTableRepository(db_session)
        self.reports = ReportRepository(db_session)
        self.chat_messages = ChatMessageRepository(db_session)
        self.feedback = FeedbackRepository(db_session)
        self.learning_datasets = LearningDatasetRepository(db_session)
        self.audit_logs = AuditLogRepository(db_session)
        self.app_logs = AppLogRepository(db_session)

    def commit(self) -> None:
        """Commit all changes."""
        self.db.commit()

    def rollback(self) -> None:
        """Rollback all changes."""
        self.db.rollback()

    def flush(self) -> None:
        """Flush pending changes."""
        self.db.flush()
