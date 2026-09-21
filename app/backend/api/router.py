from fastapi import APIRouter

from app.backend.core.config import get_settings
from app.backend.modules.analytics.controller import router as analytics_router
from app.backend.modules.auth.controller import router as auth_router
from app.backend.modules.chatbot.controller import router as chatbot_router
from app.backend.modules.cleaning.controller import router as cleaning_router
from app.backend.modules.dashboard.controller import router as dashboard_router
from app.backend.modules.detection.controller import router as detection_router
from app.backend.modules.explainability.controller import router as explainability_router
from app.backend.modules.feedback.controller import router as feedback_router
from app.backend.modules.logs.controller import router as logs_router
from app.backend.modules.preprocessing.controller import router as preprocessing_router
from app.backend.modules.projects.controller import router as projects_router
from app.backend.modules.reports.controller import router as reports_router
from app.backend.modules.settings.controller import router as settings_router
from app.backend.modules.uploads.controller import router as uploads_router
from app.backend.modules.validation.controller import router as validation_router

settings = get_settings()
api_router = APIRouter(prefix=settings.api_prefix)

api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(uploads_router)
api_router.include_router(validation_router)
api_router.include_router(cleaning_router)
api_router.include_router(preprocessing_router)
api_router.include_router(detection_router)
api_router.include_router(explainability_router)
api_router.include_router(analytics_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
api_router.include_router(logs_router)
api_router.include_router(settings_router)
api_router.include_router(chatbot_router)
api_router.include_router(feedback_router)