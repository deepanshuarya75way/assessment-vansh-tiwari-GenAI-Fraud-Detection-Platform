"""Workflow Coordinator - Manages end-to-end workflow execution"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from app.backend.core.agent_enums import AgentType, WorkflowStatus
from app.backend.core.orchestrator import AIOrchestrator
from app.backend.db.database_service import DatabaseService
from app.backend.modules.logs.service import LogService


class WorkflowCoordinator:
    """
    Coordinates the complete workflow from upload to completion.
    
    Flow:
    1. Initialize session
    2. Execute Upload Agent
    3. Execute Validation Agent
    4. Execute Cleaning Agent
    5. Execute Preprocessing Agent
    6. Execute Fraud Detection Agent
    7. Execute Explainability Agent
    8. Execute Analytics Agent
    9. Execute Dashboard Agent
    10. Mark Chatbot Ready
    11. Complete workflow
    
    Handles all orchestration and error scenarios.
    """
    
    # Agent execution order
    AGENT_PIPELINE = [
        AgentType.VALIDATION,
        AgentType.CLEANING,
        AgentType.PREPROCESSING,
        AgentType.FRAUD_DETECTION,
        AgentType.EXPLAINABILITY,
        AgentType.ANALYTICS,
        AgentType.DASHBOARD,
    ]
    
    def __init__(
        self,
        orchestrator: AIOrchestrator,
        db_service: DatabaseService,
        log_service: LogService,
    ) -> None:
        self.orchestrator = orchestrator
        self.db_service = db_service
        self.log_service = log_service
    
    async def execute_upload_workflow(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        upload_data: dict[str, Any],
    ) -> str:
        """
        Execute the complete upload and processing workflow.
        
        Returns:
            workflow_id: Identifier for this workflow execution
        """
        workflow_id = str(uuid4())
        
        try:
            # Initialize workflow
            await self.orchestrator.initialize_workflow(
                session_id=session_id,
                user_id=user_id,
                project_id=project_id,
                workflow_id=workflow_id,
                initial_data=upload_data,
            )
            
            # Execute agent pipeline
            for agent_type in self.AGENT_PIPELINE:
                result = await self.orchestrator.execute_agent(
                    workflow_id=workflow_id,
                    agent_type=agent_type,
                )
                
                # Check for failure
                if result.status.value == "failed":
                    await self.orchestrator.fail_workflow(
                        workflow_id=workflow_id,
                        error_message=f"{agent_type.value} agent failed: {result.error_message}",
                    )
                    return workflow_id
            
            # Mark chatbot ready
            await self._mark_chatbot_ready(
                workflow_id=workflow_id,
                session_id=session_id,
                user_id=user_id,
                project_id=project_id,
            )
            
            # Complete workflow
            await self.orchestrator.complete_workflow(workflow_id=workflow_id)
            
            return workflow_id
            
        except Exception as e:
            await self.orchestrator.fail_workflow(
                workflow_id=workflow_id,
                error_message=str(e),
            )
            return workflow_id
    
    async def _mark_chatbot_ready(
        self,
        workflow_id: str,
        session_id: str,
        user_id: str,
        project_id: str,
    ) -> None:
        """Mark the session as ready for chatbot interaction."""
        workflow_status = self.orchestrator.get_workflow_status(workflow_id)
        
        # Update session status in database
        await self.log_service.log_action(
            user_id=user_id,
            action="chatbot_ready",
            details={
                "session_id": session_id,
                "workflow_id": workflow_id,
            },
        )
    
    async def handle_user_feedback(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        feedback_data: dict[str, Any],
    ) -> None:
        """
        Handle user feedback and trigger learning feedback loop.
        
        Feedback can trigger:
        - Model retraining
        - Dashboard updates
        - Report regeneration
        """
        feedback_id = str(uuid4())
        
        await self.log_service.log_action(
            user_id=user_id,
            action="user_feedback_received",
            details={
                "session_id": session_id,
                "feedback_id": feedback_id,
                "feedback": feedback_data,
            },
        )
        
        # Audit trail
        self.db_service._audit_action(
            user_id=user_id,
            session_id=session_id,
            project_id=project_id,
            action="FEEDBACK_CREATED",
            resource_type="feedback",
            resource_id=feedback_id,
            after_value=feedback_data,
        )


class WorkflowExecutor:
    """
    Async wrapper for executing workflows.
    
    Handles:
    - Background task execution
    - Concurrent workflow management
    - Frontend notifications
    - Error recovery
    """
    
    def __init__(
        self,
        coordinator: WorkflowCoordinator,
        db_service: DatabaseService,
    ) -> None:
        self.coordinator = coordinator
        self.db_service = db_service
        self.active_workflows: dict[str, dict[str, Any]] = {}
    
    async def start_workflow(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        upload_data: dict[str, Any],
    ) -> str:
        """Start a new workflow and track it."""
        workflow_id = await self.coordinator.execute_upload_workflow(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            upload_data=upload_data,
        )
        
        self.active_workflows[workflow_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "project_id": project_id,
            "started_at": datetime.utcnow(),
            "status": "executing",
        }
        
        return workflow_id
    
    def get_workflow_progress(self, workflow_id: str) -> dict[str, Any]:
        """Get current progress of a workflow."""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        status = self.coordinator.orchestrator.get_workflow_status(workflow_id)
        workflow = self.active_workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "session_id": workflow["session_id"],
            "status": status["status"],
            "agents_completed": len(status["agents_completed"]),
            "agents_failed": len(status["agents_failed"]),
            "total_agents": len(self.coordinator.AGENT_PIPELINE),
            "started_at": workflow["started_at"],
        }
    
    def mark_workflow_complete(self, workflow_id: str) -> None:
        """Mark workflow as no longer active."""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "completed"
