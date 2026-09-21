"""AI Orchestrator - Main workflow controller"""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.backend.core.agent import AgentContext, BaseAgent, AgentExecutionResult
from app.backend.core.agent_enums import (
    AgentStatus,
    AgentType,
    NotificationLevel,
    RetryPolicy,
    WorkflowStatus,
)
from app.backend.db.database_service import DatabaseService
from app.backend.db.enterprise_models import AuditActionType
from app.backend.modules.logs.service import LogService


class AIOrchestrator:
    """
    Central orchestrator managing AI workflow execution.
    
    Responsibilities:
    - Create and manage sessions
    - Execute agents in sequence
    - Handle failures and retries
    - Track execution progress
    - Notify frontend of status changes
    - Log all events for audit trail
    """
    
    def __init__(
        self,
        db_service: DatabaseService,
        log_service: LogService,
    ) -> None:
        self.db_service = db_service
        self.log_service = log_service
        self.agents: dict[AgentType, BaseAgent] = {}
        self.workflow_state: dict[str, Any] = {}
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent for use in workflows."""
        self.agents[agent.agent_type] = agent
    
    def register_agents(self, agents: list[BaseAgent]) -> None:
        """Register multiple agents at once."""
        for agent in agents:
            self.register_agent(agent)
    
    async def initialize_workflow(
        self,
        session_id: str,
        user_id: str,
        project_id: str,
        workflow_id: str,
        initial_data: dict[str, Any],
    ) -> None:
        """
        Initialize a new workflow execution.
        
        Creates session context and logs workflow start.
        """
        self.workflow_state[workflow_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "project_id": project_id,
            "status": WorkflowStatus.INITIATED,
            "started_at": datetime.utcnow(),
            "completed_at": None,
            "agent_results": {},
            "current_data": initial_data,
        }
        
        # Log workflow initialization
        await self.log_service.log_action(
            user_id=user_id,
            action="workflow_initiated",
            details={
                "session_id": session_id,
                "project_id": project_id,
                "workflow_id": workflow_id,
            },
        )
        
        # Audit trail
        self.db_service._audit_action(
            user_id=user_id,
            session_id=session_id,
            project_id=project_id,
            action=AuditActionType.CREATE,
            resource_type="workflow",
            resource_id=workflow_id,
            after_value={"status": WorkflowStatus.INITIATED.value},
        )
    
    async def execute_agent(
        self,
        workflow_id: str,
        agent_type: AgentType,
        session: Session | None = None,
    ) -> AgentExecutionResult:
        """
        Execute a single agent in the workflow.
        
        Handles:
        - Agent lookup
        - Context preparation
        - Retry logic
        - Error handling
        - Status tracking
        """
        if workflow_id not in self.workflow_state:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type.value} not registered")
        
        workflow = self.workflow_state[workflow_id]
        agent = self.agents[agent_type]
        
        # Update workflow status
        workflow["status"] = self._get_workflow_status_for_agent(agent_type)
        
        # Prepare agent context
        context = AgentContext(
            session_id=workflow["session_id"],
            user_id=workflow["user_id"],
            project_id=workflow["project_id"],
            agent_type=agent_type,
            workflow_id=workflow_id,
            input_data=workflow["current_data"],
            max_retries=3,
        )
        
        # Execute agent with retry logic
        result = await self._execute_with_retry(agent, context)
        
        # Store result
        workflow["agent_results"][agent_type.value] = result
        
        # Update workflow data for next agent
        if result.status == AgentStatus.COMPLETED:
            workflow["current_data"].update(result.output_data)
        
        # Log agent execution
        await self.log_service.log_action(
            user_id=workflow["user_id"],
            action=f"agent_{agent_type.value}_executed",
            details={
                "status": result.status.value,
                "execution_time": result.execution_time_seconds,
                "error": result.error_message,
            },
        )
        
        # Audit trail
        self.db_service._audit_action(
            user_id=workflow["user_id"],
            session_id=workflow["session_id"],
            project_id=workflow["project_id"],
            action=AuditActionType.UPDATE,
            resource_type="agent_execution",
            resource_id=agent_type.value,
            after_value={
                "status": result.status.value,
                "execution_time": result.execution_time_seconds,
            },
        )
        
        return result
    
    async def _execute_with_retry(
        self, agent: BaseAgent, context: AgentContext
    ) -> AgentExecutionResult:
        """Execute agent with retry logic."""
        last_error = None
        
        for attempt in range(context.max_retries):
            try:
                start_time = datetime.utcnow()
                result = await agent.validate_and_execute(context)
                end_time = datetime.utcnow()
                
                result.execution_time_seconds = (
                    end_time - start_time
                ).total_seconds()
                result.retry_count = attempt
                
                if result.status == AgentStatus.COMPLETED:
                    return result
                
                # Agent failed, may retry
                last_error = result.error_message
                context.status = AgentStatus.RETRYING
                context.retry_count = attempt + 1
                
            except Exception as e:
                last_error = str(e)
                if attempt < context.max_retries - 1:
                    continue
        
        # All retries exhausted
        return AgentExecutionResult(
            agent_type=agent.agent_type,
            status=AgentStatus.FAILED,
            output_data={},
            error_message=last_error or "Unknown error",
            retry_count=context.max_retries,
        )
    
    def _get_workflow_status_for_agent(self, agent_type: AgentType) -> WorkflowStatus:
        """Map agent type to workflow status."""
        mapping = {
            AgentType.UPLOAD: WorkflowStatus.PROCESSING,
            AgentType.VALIDATION: WorkflowStatus.VALIDATION_STAGE,
            AgentType.CLEANING: WorkflowStatus.CLEANING_STAGE,
            AgentType.PREPROCESSING: WorkflowStatus.PREPROCESSING_STAGE,
            AgentType.FRAUD_DETECTION: WorkflowStatus.FRAUD_DETECTION_STAGE,
            AgentType.EXPLAINABILITY: WorkflowStatus.EXPLAINABILITY_STAGE,
            AgentType.ANALYTICS: WorkflowStatus.ANALYTICS_STAGE,
            AgentType.DASHBOARD: WorkflowStatus.DASHBOARD_STAGE,
            AgentType.CHATBOT: WorkflowStatus.CHATBOT_READY,
        }
        return mapping.get(agent_type, WorkflowStatus.PROCESSING)
    
    async def complete_workflow(self, workflow_id: str) -> None:
        """Mark workflow as completed."""
        if workflow_id not in self.workflow_state:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflow_state[workflow_id]
        workflow["status"] = WorkflowStatus.COMPLETED
        workflow["completed_at"] = datetime.utcnow()
        
        await self.log_service.log_action(
            user_id=workflow["user_id"],
            action="workflow_completed",
            details={
                "workflow_id": workflow_id,
                "session_id": workflow["session_id"],
            },
        )
    
    async def fail_workflow(self, workflow_id: str, error_message: str) -> None:
        """Mark workflow as failed."""
        if workflow_id not in self.workflow_state:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflow_state[workflow_id]
        workflow["status"] = WorkflowStatus.FAILED
        workflow["completed_at"] = datetime.utcnow()
        workflow["error_message"] = error_message
        
        await self.log_service.log_action(
            user_id=workflow["user_id"],
            action="workflow_failed",
            details={
                "workflow_id": workflow_id,
                "session_id": workflow["session_id"],
                "error": error_message,
            },
        )
        
        # Audit trail
        self.db_service._audit_action(
            user_id=workflow["user_id"],
            session_id=workflow["session_id"],
            project_id=workflow["project_id"],
            action=AuditActionType.UPDATE,
            resource_type="workflow",
            resource_id=workflow_id,
            after_value={"status": "failed", "error": error_message},
        )
    
    def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """Get current workflow status."""
        if workflow_id not in self.workflow_state:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflow_state[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"].value,
            "started_at": workflow["started_at"],
            "completed_at": workflow["completed_at"],
            "agents_completed": [
                k for k, v in workflow["agent_results"].items()
                if v.status == AgentStatus.COMPLETED
            ],
            "agents_failed": [
                k for k, v in workflow["agent_results"].items()
                if v.status == AgentStatus.FAILED
            ],
        }
