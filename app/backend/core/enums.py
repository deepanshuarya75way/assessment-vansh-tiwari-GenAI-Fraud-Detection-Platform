from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    REVIEWER = "reviewer"


class ProjectStatus(str, Enum):
    CREATED = "created"
    UPLOADED = "uploaded"
    VALIDATED = "validated"
    CLEANED = "cleaned"
    PREPROCESSED = "preprocessed"
    DETECTED = "detected"
    EXPLAINED = "explained"
    ANALYZED = "analyzed"
    DASHBOARD_READY = "dashboard_ready"
    REPORT_READY = "report_ready"
    COMPLETED = "completed"


class UploadStatus(str, Enum):
    RECEIVED = "received"
    STORED = "stored"
    PROCESSED = "processed"
    FAILED = "failed"


class FraudLabel(str, Enum):
    SAFE = "safe"
    REVIEW = "review"
    FRAUD = "fraud"


class FeedbackType(str, Enum):
    LABEL_CORRECTION = "label_correction"
    EXPLANATION_FEEDBACK = "explanation_feedback"
    REPORT_FEEDBACK = "report_feedback"


class ChatAnswerSource(str, Enum):
    RULE_BASED = "rule_based"
    RETRIEVAL = "retrieval"
