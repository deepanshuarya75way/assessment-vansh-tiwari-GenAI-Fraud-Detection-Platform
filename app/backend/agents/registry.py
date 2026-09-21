from app.backend.agents.analytics_agent import AnalyticsAgent
from app.backend.agents.chatbot_agent import ChatbotAgent
from app.backend.agents.cleaning_agent import CleaningAgent
from app.backend.agents.dashboard_agent import DashboardAgent
from app.backend.agents.explainability_agent import ExplainabilityAgent
from app.backend.agents.feedback_agent import FeedbackAgent
from app.backend.agents.fraud_detection_agent import FraudDetectionAgent
from app.backend.agents.preprocessing_agent import PreprocessingAgent
from app.backend.agents.report_agent import ReportAgent
from app.backend.agents.upload_agent import UploadAgent
from app.backend.agents.validation_agent import ValidationAgent


def default_agent_pipeline() -> list:
    return [
        UploadAgent(),
        ValidationAgent(),
        CleaningAgent(),
        PreprocessingAgent(),
        FraudDetectionAgent(),
        ExplainabilityAgent(),
        AnalyticsAgent(),
        DashboardAgent(),
        ChatbotAgent(),
        ReportAgent(),
        FeedbackAgent(),
    ]