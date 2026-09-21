"""Agent and Orchestration Enums"""

from enum import Enum


class AgentType(str, Enum):
    """AI Agent types in the workflow pipeline."""
    UPLOAD = "upload"
    VALIDATION = "validation"
    CLEANING = "cleaning"
    PREPROCESSING = "preprocessing"
    FRAUD_DETECTION = "fraud_detection"
    EXPLAINABILITY = "explainability"
    ANALYTICS = "analytics"
    DASHBOARD = "dashboard"
    CHATBOT = "chatbot"
    REPORT = "report"
    FEEDBACK = "feedback"


class AgentStatus(str, Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class WorkflowStatus(str, Enum):
    """Overall workflow status."""
    INITIATED = "initiated"
    PROCESSING = "processing"
    VALIDATION_STAGE = "validation_stage"
    CLEANING_STAGE = "cleaning_stage"
    PREPROCESSING_STAGE = "preprocessing_stage"
    FRAUD_DETECTION_STAGE = "fraud_detection_stage"
    EXPLAINABILITY_STAGE = "explainability_stage"
    ANALYTICS_STAGE = "analytics_stage"
    DASHBOARD_STAGE = "dashboard_stage"
    CHATBOT_READY = "chatbot_ready"
    COMPLETED = "completed"
    FAILED = "failed"


class RetryPolicy(str, Enum):
    """Retry strategy for failed agents."""
    NO_RETRY = "no_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


class NotificationLevel(str, Enum):
    """Frontend notification severity."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
