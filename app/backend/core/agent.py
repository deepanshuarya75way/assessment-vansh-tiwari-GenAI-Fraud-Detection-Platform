"""Base Agent Class and Agent Context"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from app.backend.core.agent_enums import AgentStatus, AgentType, RetryPolicy

T = TypeVar("T")


@dataclass
class AgentContext:
    """Context passed to each agent during execution."""
    
    session_id: str
    user_id: str
    project_id: str
    agent_type: AgentType
    workflow_id: str
    
    # Input data from previous stage
    input_data: dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    
    # Status tracking
    status: AgentStatus = AgentStatus.PENDING
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    
    # Output from agent
    output_data: dict[str, Any] = field(default_factory=dict)
    
    # Logging
    logs: list[str] = field(default_factory=list)


@dataclass
class AgentExecutionResult:
    """Result returned by an agent after execution."""
    
    agent_type: AgentType
    status: AgentStatus
    output_data: dict[str, Any]
    error_message: str | None = None
    retry_count: int = 0
    execution_time_seconds: float = 0.0
    logs: list[str] = field(default_factory=list)


class BaseAgent(ABC, Generic[T]):
    """
    Base class for all AI agents.
    
    Every agent:
    - Has ONE responsibility
    - Validates input
    - Performs operation
    - Returns structured output
    - Handles errors gracefully
    """
    
    def __init__(
        self,
        agent_type: AgentType,
        retry_policy: RetryPolicy = RetryPolicy.EXPONENTIAL_BACKOFF,
    ) -> None:
        self.agent_type = agent_type
        self.retry_policy = retry_policy
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentExecutionResult:
        """
        Execute the agent's core logic.
        
        Must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    async def validate_input(self, context: AgentContext) -> bool:
        """
        Validate that input data meets agent requirements.
        
        Return True if valid, False otherwise.
        """
        pass
    
    async def validate_and_execute(
        self, context: AgentContext
    ) -> AgentExecutionResult:
        """
        Wrapper that validates input before executing.
        
        Handles validation errors gracefully.
        """
        try:
            is_valid = await self.validate_input(context)
            if not is_valid:
                return AgentExecutionResult(
                    agent_type=self.agent_type,
                    status=AgentStatus.FAILED,
                    output_data={},
                    error_message="Input validation failed",
                )
            
            result = await self.execute(context)
            return result
            
        except Exception as e:
            return AgentExecutionResult(
                agent_type=self.agent_type,
                status=AgentStatus.FAILED,
                output_data={},
                error_message=str(e),
            )
    
    def _log(self, context: AgentContext, message: str) -> None:
        """Add log message to context."""
        timestamp = datetime.utcnow().isoformat()
        context.logs.append(f"[{timestamp}] {self.agent_type.value}: {message}")
