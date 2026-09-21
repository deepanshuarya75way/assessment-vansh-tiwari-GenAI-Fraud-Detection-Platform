"""Orchestration API Controller - Exposes workflow endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.backend.api.deps import CurrentUser, get_db_session, get_current_user
from app.backend.db.database_service import DatabaseService
from app.backend.modules.logs.service import LogService
from app.backend.modules.orchestration import OrchestrationService

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


class StartWorkflowRequest(BaseModel):
    """Request to start a fraud detection workflow."""
    
    session_id: str = Field(..., description="Analysis session ID")
    project_id: str = Field(..., description="Project ID")
    dataset_path: str = Field(..., description="Path to uploaded dataset")
    filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File type (csv, parquet, etc)")


class WorkflowStatusResponse(BaseModel):
    """Workflow status response."""
    
    workflow_id: str
    session_id: str
    status: str
    agents_completed: int
    agents_failed: int
    total_agents: int
    started_at: str


class FeedbackRequest(BaseModel):
    """User feedback request."""
    
    session_id: str
    feedback_type: str
    corrected_label: str | None = None
    comments: str | None = None


async def get_orchestration_service(
    db: CurrentUser = Depends(get_db_session),
) -> OrchestrationService:
    """Dependency to get orchestration service."""
    db_service = DatabaseService(db)
    log_service = LogService(db)
    return OrchestrationService.initialize(db_service, log_service)


@router.post("/start", response_model=dict)
async def start_workflow(
    request: StartWorkflowRequest,
    current_user: CurrentUser = Depends(get_current_user),
    orchestration_service: OrchestrationService = Depends(
        get_orchestration_service
    ),
) -> dict:
    """
    Start a new fraud detection workflow.
    
    Initiates the complete ML pipeline:
    1. Validation
    2. Cleaning
    3. Preprocessing
    4. Fraud Detection
    5. Explainability
    6. Analytics
    7. Dashboard
    """
    try:
        workflow_id = await orchestration_service.start_fraud_detection_workflow(
            session_id=request.session_id,
            user_id=current_user.id,
            project_id=request.project_id,
            dataset_path=request.dataset_path,
            filename=request.filename,
            file_type=request.file_type,
        )
        
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": "Fraud detection workflow initiated",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/status/{workflow_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    workflow_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    orchestration_service: OrchestrationService = Depends(
        get_orchestration_service
    ),
) -> WorkflowStatusResponse:
    """Get current status of a workflow."""
    try:
        status = orchestration_service.get_workflow_status(workflow_id)
        
        return WorkflowStatusResponse(
            workflow_id=workflow_id,
            session_id=status["session_id"],
            status=status["status"],
            agents_completed=len(status["agents_completed"]),
            agents_failed=len(status["agents_failed"]),
            total_agents=status["total_agents"],
            started_at=status["started_at"].isoformat(),
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: CurrentUser = Depends(get_current_user),
    orchestration_service: OrchestrationService = Depends(
        get_orchestration_service
    ),
) -> dict:
    """
    Submit user feedback on fraud detection results.
    
    Feedback can trigger:
    - Model retraining
    - Dashboard updates
    - Report regeneration
    """
    try:
        feedback_data = {
            "feedback_type": request.feedback_type,
            "corrected_label": request.corrected_label,
            "comments": request.comments,
        }
        
        await orchestration_service.handle_feedback(
            session_id=request.session_id,
            user_id=current_user.id,
            project_id="",  # Would be retrieved from session
            feedback_data=feedback_data,
        )
        
        return {
            "status": "feedback_received",
            "message": "Thank you for your feedback",
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/agents")
async def get_available_agents(
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """Get list of available agents in the pipeline."""
    agents = [
        {"name": "Validation", "type": "validation", "order": 1},
        {"name": "Cleaning", "type": "cleaning", "order": 2},
        {"name": "Preprocessing", "type": "preprocessing", "order": 3},
        {"name": "Fraud Detection", "type": "fraud_detection", "order": 4},
        {"name": "Explainability", "type": "explainability", "order": 5},
        {"name": "Analytics", "type": "analytics", "order": 6},
        {"name": "Dashboard", "type": "dashboard", "order": 7},
    ]
    
    return {"agents": agents, "total": len(agents)}
