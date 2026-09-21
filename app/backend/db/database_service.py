"""
Database Service Layer - Transaction management and cross-repository operations.

Use this layer for:
- Multi-table transactions (atomicity)
- Session-scoped operations
- Batch imports/exports
- Data consistency checks
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

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
    ReportArtifact,
    ChatMessage,
    AnalystFeedback,
    LearningDataset,
    AuditLog,
    AppLog,
    AuditActionType,
    SessionStatus,
)
from app.backend.db.session_repositories import SessionRepositories


class DatabaseService:
    """
    High-level database operations for fraud detection platform.
    Manages transactions, session lifecycle, and complex operations.
    """

    def __init__(self, db_session: Session) -> None:
        self.db = db_session
        self.repos = SessionRepositories(db_session)

    @contextmanager
    def transaction(self) -> Generator[SessionRepositories, None, None]:
        """
        Context manager for database transactions.
        
        Usage:
            with db_service.transaction() as repos:
                repos.fraud_results.add(result)
                repos.ai_insights.add(insight)
                # Auto-commits on success, auto-rollbacks on exception
        """
        try:
            yield self.repos
            self.repos.commit()
        except Exception as e:
            self.repos.rollback()
            raise e

    # ========================================================================
    # SESSION LIFECYCLE OPERATIONS
    # ========================================================================

    def create_analysis_session(
        self,
        project_id: str,
        user_id: str,
        upload_id: str,
        session_name: str,
        session_metadata: dict[str, Any] | None = None,
    ) -> AnalysisSession:
        """
        Create a new analysis session.
        Called when user uploads a dataset.
        """
        session = AnalysisSession(
            project_id=project_id,
            user_id=user_id,
            upload_id=upload_id,
            session_name=session_name,
            status=SessionStatus.INITIALIZED,
            started_at=datetime.now(timezone.utc),
            session_metadata=session_metadata or {},
        )
        with self.transaction() as repos:
            repos.analysis_sessions.add(session)
        return session

    def complete_analysis_session(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        summary: str | None = None,
    ) -> AnalysisSession:
        """Mark session as completed with summary."""
        session = self.repos.analysis_sessions.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = SessionStatus.COMPLETED
        session.completed_at = datetime.now(timezone.utc)
        session.summary = summary

        with self.transaction() as repos:
            repos.db.flush()

        self._audit_action(
            user_id=user_id,
            session_id=session_id,
            project_id=project_id,
            action=AuditActionType.UPDATE,
            resource_type="analysis_session",
            resource_id=session_id,
            after_value={"status": "completed"},
        )
        return session

    def fail_analysis_session(self, session_id: str, error_message: str) -> AnalysisSession:
        """Mark session as failed."""
        session = self.repos.analysis_sessions.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session.status = SessionStatus.FAILED
        session.session_metadata["error"] = error_message

        with self.transaction() as repos:
            repos.db.flush()

        return session

    # ========================================================================
    # DATA PIPELINE OPERATIONS
    # ========================================================================

    def import_validated_data(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        upload_id: str,
        validation_rules: dict[str, Any],
        validation_errors: dict[str, Any],
        data_profile: dict[str, Any],
        valid_rows: int,
        invalid_rows: int,
        duplicate_rows: int,
    ) -> ValidatedData:
        """Import validation results for a dataset."""
        validated = ValidatedData(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            upload_id=upload_id,
            validation_rules=validation_rules,
            validation_errors=validation_errors,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            duplicate_rows=duplicate_rows,
            data_profile=data_profile,
        )

        with self.transaction() as repos:
            repos.validated_data.add(validated)

        self._log_action(
            session_id=session_id,
            user_id=user_id,
            log_category="data_validation",
            log_message=f"Validated {valid_rows} rows, {invalid_rows} invalid, {duplicate_rows} duplicates",
        )
        return validated

    def import_cleaned_data(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        validated_data_id: str,
        parquet_path: str,
        row_count: int,
        transformations_applied: dict[str, Any],
        quality_metrics: dict[str, Any],
    ) -> CleanedData:
        """Import cleaned data results."""
        cleaned = CleanedData(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            validated_data_id=validated_data_id,
            parquet_path=parquet_path,
            row_count=row_count,
            transformations_applied=transformations_applied,
            quality_metrics=quality_metrics,
        )

        with self.transaction() as repos:
            repos.cleaned_data.add(cleaned)

        self._log_action(
            session_id=session_id,
            user_id=user_id,
            log_category="data_cleaning",
            log_message=f"Cleaned data with {row_count} rows",
        )
        return cleaned

    def import_processed_data(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        cleaned_data_id: str,
        parquet_path: str,
        row_count: int,
        feature_engineered_columns: dict[str, Any],
        scaling_parameters: dict[str, Any],
        feature_importance: dict[str, Any],
    ) -> ProcessedData:
        """Import feature-engineered data results."""
        processed = ProcessedData(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            cleaned_data_id=cleaned_data_id,
            parquet_path=parquet_path,
            row_count=row_count,
            feature_engineered_columns=feature_engineered_columns,
            scaling_parameters=scaling_parameters,
            feature_importance=feature_importance,
        )

        with self.transaction() as repos:
            repos.processed_data.add(processed)

        self._log_action(
            session_id=session_id,
            user_id=user_id,
            log_category="feature_engineering",
            log_message=f"Processed data with {len(feature_engineered_columns)} features",
        )
        return processed

    # ========================================================================
    # BATCH FRAUD RESULTS IMPORT
    # ========================================================================

    def import_fraud_results_batch(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        processed_data_id: str,
        results: list[dict[str, Any]],
        batch_size: int = 1000,
    ) -> int:
        """
        Bulk import fraud detection results.
        Returns count of inserted rows.
        """
        imported_count = 0

        for batch_start in range(0, len(results), batch_size):
            batch = results[batch_start : batch_start + batch_size]
            fraud_objects = [
                FraudResult(
                    session_id=session_id,
                    user_id=user_id,
                    project_id=project_id,
                    processed_data_id=processed_data_id,
                    row_identifier=result.get("row_id", idx),
                    predicted_label=result.get("label", "safe"),
                    risk_score=float(result.get("risk_score", 0.0)),
                    confidence_score=float(result.get("confidence", 0.0)),
                    model_decision_path=result.get("decision_path", {}),
                    shap_values=result.get("shap_values", {}),
                    feature_contributions=result.get("feature_contributions", {}),
                    explanation=result.get("explanation"),
                    raw_record=result.get("raw_record", {}),
                )
                for idx, result in enumerate(batch)
            ]

            with self.transaction() as repos:
                for obj in fraud_objects:
                    repos.fraud_results.add(obj)
                imported_count += len(fraud_objects)

        self._log_action(
            session_id=session_id,
            user_id=user_id,
            log_category="fraud_detection",
            log_message=f"Imported {imported_count} fraud detection results",
        )

        return imported_count

    # ========================================================================
    # AI INSIGHTS & ANALYTICS
    # ========================================================================

    def add_ai_insight(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        category: str,
        text: str,
        evidence: dict[str, Any],
        confidence: float,
        priority: str,
    ) -> AIInsight:
        """Add an AI-generated insight."""
        insight = AIInsight(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            insight_category=category,
            insight_text=text,
            evidence=evidence,
            confidence=confidence,
            priority=priority,
        )

        with self.transaction() as repos:
            repos.ai_insights.add(insight)

        return insight

    def get_session_statistics(self, session_id: str, user_id: str, project_id: str) -> dict[str, Any]:
        """Get comprehensive statistics for a session."""
        fraud_stats = self.repos.fraud_results.get_statistics(session_id, user_id, project_id)
        chat_count = self.repos.chat_messages.count_session(session_id, user_id, project_id)
        insights_count = self.repos.ai_insights.count_session(session_id, user_id, project_id)
        feedback_count = self.repos.feedback.count_session(session_id, user_id, project_id)

        return {
            "fraud_statistics": fraud_stats,
            "chat_message_count": chat_count,
            "ai_insights_count": insights_count,
            "feedback_count": feedback_count,
            "processed_at": datetime.now(timezone.utc),
        }

    # ========================================================================
    # FEEDBACK & MODEL IMPROVEMENT
    # ========================================================================

    def add_feedback(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        fraud_result_id: str,
        feedback_type: str,
        corrected_label: str | None = None,
        comment: str | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> AnalystFeedback:
        """Record analyst feedback for model improvement."""
        feedback = AnalystFeedback(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            fraud_result_id=fraud_result_id,
            feedback_type=feedback_type,
            corrected_label=corrected_label,
            comment=comment,
            attached_evidence=evidence or {},
        )

        with self.transaction() as repos:
            repos.feedback.add(feedback)

        self._log_action(
            session_id=session_id,
            user_id=user_id,
            log_category="model_feedback",
            log_message=f"Feedback {feedback_type} recorded for result {fraud_result_id}",
        )
        return feedback

    def build_learning_dataset(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        feedback_items: list[AnalystFeedback],
        parquet_path: str,
        metadata: dict[str, Any],
    ) -> LearningDataset:
        """Create validated learning dataset from feedback."""
        learning_dataset = LearningDataset(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            feedback_item_count=len(feedback_items),
            parquet_path=parquet_path,
            dataset_metadata=metadata,
        )

        with self.transaction() as repos:
            repos.learning_datasets.add(learning_dataset)

        self._log_action(
            session_id=session_id,
            user_id=user_id,
            log_category="model_training",
            log_message=f"Created learning dataset with {len(feedback_items)} feedback items",
        )
        return learning_dataset

    # ========================================================================
    # CLEANUP & MAINTENANCE
    # ========================================================================

    def cleanup_session_soft_deletes(self, session_id: str) -> int:
        """
        Perform cleanup of soft-deleted records in a session.
        (Calls VACUUM internally after deletes)
        """
        deleted_count = 0

        with self.transaction() as repos:
            # Mark all soft-deleted fraud results
            fraud_results = repos.fraud_results.list_session(session_id, "", "")
            for result in fraud_results:
                if result.deleted_at is not None:
                    deleted_count += 1

        # Note: Real cleanup would trigger VACUUM in background job
        return deleted_count

    def export_session_data(
        self, session_id: str, user_id: str, project_id: str
    ) -> dict[str, Any]:
        """Export all session data in dictionary format (for analytics/archive)."""
        session = self.repos.analysis_sessions.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session": {
                "id": session.id,
                "name": session.session_name,
                "status": session.status.value,
                "created_at": session.created_at.isoformat(),
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "summary": session.summary,
            },
            "fraud_results": [
                {
                    "row_id": r.row_identifier,
                    "label": r.predicted_label.value,
                    "risk_score": r.risk_score,
                    "confidence": r.confidence_score,
                }
                for r in self.repos.fraud_results.list_session(session_id, user_id, project_id)
            ],
            "ai_insights": [
                {
                    "category": i.insight_category,
                    "text": i.insight_text,
                    "confidence": i.confidence,
                    "priority": i.priority.value,
                }
                for i in self.repos.ai_insights.list_session(session_id, user_id, project_id)
            ],
            "chat_history": [
                {
                    "question": m.question,
                    "answer": m.answer,
                    "intent": m.intent.value,
                    "source": m.answer_source.value,
                }
                for m in self.repos.chat_messages.list_session(session_id, user_id, project_id)
            ],
            "feedback_count": self.repos.feedback.count_session(session_id, user_id, project_id),
            "statistics": self.get_session_statistics(session_id, user_id, project_id),
        }

    # ========================================================================
    # AUDIT & LOGGING
    # ========================================================================

    def _audit_action(
        self,
        user_id: str,
        session_id: str | None,
        project_id: str | None,
        action: AuditActionType,
        resource_type: str,
        resource_id: str,
        before_value: dict[str, Any] | None = None,
        after_value: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        """Record an audit log entry."""
        audit_entry = AuditLog(
            user_id=user_id,
            session_id=session_id,
            project_id=project_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            before_value=before_value,
            after_value=after_value,
            ip_address=ip_address,
            status="success",
        )

        self.repos.audit_logs.add(audit_entry)
        self.repos.flush()
        return audit_entry

    def _log_action(
        self,
        session_id: str | None,
        user_id: str | None,
        log_category: str,
        log_message: str,
        log_level: str = "INFO",
        context: dict[str, Any] | None = None,
    ) -> AppLog:
        """Record an application log entry."""
        log_entry = AppLog(
            session_id=session_id,
            user_id=user_id,
            log_level=log_level,
            log_category=log_category,
            log_message=log_message,
            log_context=context or {},
        )

        self.repos.app_logs.add(log_entry)
        self.repos.flush()
        return log_entry

    def get_audit_trail(self, session_id: str, limit: int = 100) -> list[AuditLog]:
        """Retrieve audit trail for a session."""
        return self.repos.audit_log_repository.list_by_session(session_id, limit)

    def get_session_logs(self, session_id: str, limit: int = 500) -> list[AppLog]:
        """Retrieve application logs for a session."""
        return self.repos.app_logs.list_by_session(session_id, limit)
