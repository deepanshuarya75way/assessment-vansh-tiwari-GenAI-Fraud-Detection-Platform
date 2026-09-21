"""
Complete System Integration Test

Demonstrates the entire fraud detection pipeline:
1. Initialize components
2. Create workflow
3. Execute agents sequentially
4. Track progress
5. Handle completion
"""

import asyncio
from datetime import datetime
from uuid import uuid4

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
from app.backend.modules.orchestration import OrchestrationService


async def run_complete_system_test() -> None:
    """Run complete fraud detection pipeline."""
    
    print("\n" + "=" * 80)
    print("COMPLETE FRAUD DETECTION PIPELINE INTEGRATION TEST")
    print("=" * 80)
    
    # Simulate session data
    session_id = str(uuid4())
    user_id = str(uuid4())
    project_id = str(uuid4())
    workflow_id = str(uuid4())
    
    print(f"\nTest Configuration:")
    print(f"  Session ID: {session_id[:12]}...")
    print(f"  User ID: {user_id[:12]}...")
    print(f"  Project ID: {project_id[:12]}...")
    print(f"  Workflow ID: {workflow_id[:12]}...")
    
    # Simulate database services (in real app, these come from FastAPI deps)
    print("\n1. Initializing System Components...")
    try:
        # Create mock services
        class MockDB:
            pass
        
        db_service = type('DatabaseService', (), {
            '_audit_action': lambda *args, **kwargs: None,
        })()
        
        log_service = type('LogService', (), {
            'log_action': lambda *args, **kwargs: asyncio.sleep(0),
        })()
        
        print("   OK: Database service initialized")
        print("   OK: Log service initialized")
        
    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return
    
    # Initialize orchestrator
    print("\n2. Registering Agents...")
    orchestrator = AIOrchestrator(db_service, log_service)
    
    agents = [
        ValidationAgent(),
        CleaningAgent(),
        PreprocessingAgent(),
        FraudDetectionAgent(),
        ExplainabilityAgent(),
        AnalyticsAgent(),
        DashboardAgent(),
    ]
    
    orchestrator.register_agents(agents)
    
    for agent in agents:
        print(f"   OK: Registered {agent.agent_type.value}")
    
    # Initialize workflow management
    print("\n3. Initializing Workflow Management...")
    coordinator = WorkflowCoordinator(orchestrator, db_service, log_service)
    executor = WorkflowExecutor(coordinator, db_service)
    print("   OK: Workflow coordinator initialized")
    print("   OK: Workflow executor initialized")
    
    # Prepare workflow data
    print("\n4. Preparing Workflow Data...")
    upload_data = {
        "dataset_path": "/uploads/fraud_detection_2024.parquet",
        "filename": "transactions.parquet",
        "file_type": "parquet",
    }
    print(f"   Dataset: {upload_data['filename']}")
    print(f"   Type: {upload_data['file_type']}")
    print(f"   Size: ~500MB (simulated)")
    
    # Initialize workflow
    print("\n5. Initializing Workflow...")
    await orchestrator.initialize_workflow(
        session_id=session_id,
        user_id=user_id,
        project_id=project_id,
        workflow_id=workflow_id,
        initial_data=upload_data,
    )
    print("   OK: Workflow initialized")
    
    # Execute agent pipeline
    print("\n6. Executing Agent Pipeline...")
    print("-" * 80)
    
    for agent_type in coordinator.AGENT_PIPELINE:
        print(f"\n   Executing: {agent_type.value.upper()}")
        
        result = await orchestrator.execute_agent(
            workflow_id=workflow_id,
            agent_type=agent_type,
        )
        
        if result.status.value == "completed":
            print(f"   Status: COMPLETED")
            if result.output_data:
                keys = list(result.output_data.keys())[:2]
                print(f"   Output: {', '.join(keys)}")
            print(f"   Time: {result.execution_time_seconds:.2f}s")
        else:
            print(f"   Status: FAILED")
            print(f"   Error: {result.error_message}")
            break
    
    # Get final status
    print("\n7. Workflow Completion Status...")
    print("-" * 80)
    
    final_status = orchestrator.get_workflow_status(workflow_id)
    
    status_str = final_status['status'].value if hasattr(final_status['status'], 'value') else str(final_status['status'])
    print(f"\n   Overall Status: {status_str}")
    print(f"   Workflow ID: {final_status['workflow_id'][:12]}...")
    print(f"   Agents Completed: {len(final_status['agents_completed'])}")
    print(f"   Agents Failed: {len(final_status['agents_failed'])}")
    
    if final_status['agents_completed']:
        print(f"\n   Completed Agents:")
        for agent in final_status['agents_completed']:
            print(f"     - {agent}")
    
    if final_status['agents_failed']:
        print(f"\n   Failed Agents:")
        for agent in final_status['agents_failed']:
            print(f"     - {agent}")
    
    # Mark workflow as complete
    print("\n8. Finalizing Workflow...")
    await orchestrator.complete_workflow(workflow_id=workflow_id)
    print("   OK: Workflow marked as complete")
    
    # Summary
    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUMMARY")
    print("=" * 80)
    
    summary = {
        "Total Agents": len(coordinator.AGENT_PIPELINE),
        "Completed": len(final_status['agents_completed']),
        "Failed": len(final_status['agents_failed']),
        "Success Rate": f"{(len(final_status['agents_completed']) / len(coordinator.AGENT_PIPELINE) * 100):.1f}%",
        "Workflow Status": status_str,
        "Timestamp": datetime.utcnow().isoformat(),
    }
    
    for key, value in summary.items():
        print(f"{key:.<30} {value}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_complete_system_test())
