"""Orchestration Service - Initializes and manages the AI orchestrator"""

from typing import Any

from app.backend.core.orchestrator import AIOrchestrator
from app.backend.core.workflow import WorkflowCoordinator, WorkflowExecutor
from app.backend.db.database_service import DatabaseService
from app.backend.modules.agents import (
    AnalyticsAgent,
    CleaningAgent,
    DashboardAgent,
    ExplainabilityAgent,
    FraudDetectionAgent,
    PreprocessingAgent,
    ValidationAgent,
)
from app.backend.modules.logs.service import LogService


class OrchestrationService:
    """
    Service for initializing and using the AI orchestrator.
    
    Manages:
    - Agent registration
    - Orchestrator initialization
    - Workflow coordination
    - Workflow execution
    """
    
    _instance: "OrchestrationService | None" = None
    _initialized: bool = False
    
    def __init__(
        self,
        db_service: DatabaseService,
        log_service: LogService,
    ) -> None:
        self.db_service = db_service
        self.log_service = log_service
        
        # Initialize orchestrator
        self.orchestrator = AIOrchestrator(db_service, log_service)
        
        # Register all agents
        self._register_agents()
        
        # Initialize coordinator and executor
        self.coordinator = WorkflowCoordinator(
            orchestrator=self.orchestrator,
            db_service=db_service,
            log_service=log_service,
        )
        
        self.executor = WorkflowExecutor(
            coordinator=self.coordinator,
            db_service=db_service,
        )
        
        OrchestrationService._initialized = True
    
    def _register_agents(self) -> None:
        """Register all agents with the orchestrator."""
        agents = [
            ValidationAgent(),
            CleaningAgent(),
            PreprocessingAgent(),
            FraudDetectionAgent(),
            ExplainabilityAgent(),
            AnalyticsAgent(),
            DashboardAgent(),
        ]
        
        self.orchestrator.register_agents(agents)
    
    async def start_fraud_detection_workflow(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        dataset_path: str,
        filename: str,
        file_type: str,
    ) -> str:
        """
        Start a complete fraud detection workflow.
        
        Returns:
            workflow_id: ID of the started workflow
        """
        upload_data = {
            "dataset_path": dataset_path,
            "filename": filename,
            "file_type": file_type,
        }
        
        workflow_id = await self.executor.start_workflow(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            upload_data=upload_data,
        )
        
        return workflow_id
    
    def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """Get current status of a workflow."""
        return self.executor.get_workflow_progress(workflow_id)
    
    async def handle_feedback(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        feedback_data: dict[str, Any],
    ) -> None:
        """Handle user feedback."""
        await self.coordinator.handle_user_feedback(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            feedback_data=feedback_data,
        )
    
    @classmethod
    def get_instance(
        cls,
        db_service: DatabaseService | None = None,
        log_service: LogService | None = None,
    ) -> "OrchestrationService":
        """
        Get or create singleton instance.
        
        First call must provide db_service and log_service.
        """
        if cls._instance is None:
            if db_service is None or log_service is None:
                raise ValueError(
                    "First call to get_instance must provide db_service and log_service"
                )
            cls._instance = cls(db_service, log_service)
        
        return cls._instance
    
    @classmethod
    def initialize(
        cls,
        db_service: DatabaseService,
        log_service: LogService,
    ) -> "OrchestrationService":
        """Initialize the service (for dependency injection)."""
        if cls._instance is not None:
            return cls._instance
        
        return cls.get_instance(db_service, log_service)
