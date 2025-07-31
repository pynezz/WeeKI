"""Basic tests for WeeKI self-hosting functionality."""

import asyncio
import pytest
from unittest.mock import patch

from weeki.config import settings
from weeki.database import db_manager
from weeki.agents import AgentOrchestrator


@pytest.fixture
async def orchestrator():
    """Create and initialize an orchestrator for testing."""
    # Initialize database
    db_manager.initialize()
    await db_manager.create_tables_async()
    
    # Create orchestrator
    orch = AgentOrchestrator()
    await orch.initialize()
    
    yield orch
    
    # Cleanup
    await orch.shutdown()
    await db_manager.close()


@pytest.mark.asyncio
async def test_config_loading():
    """Test configuration loading."""
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert isinstance(settings.max_agents, int)


@pytest.mark.asyncio
async def test_database_initialization():
    """Test database initialization."""
    db_manager.initialize()
    await db_manager.create_tables_async()
    
    # Test database connection
    async with db_manager.get_async_session() as session:
        assert session is not None
    
    await db_manager.close()


@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initialization."""
    assert orchestrator.get_active_agent_count() > 0
    assert orchestrator.orchestrator.is_active


@pytest.mark.asyncio
async def test_task_creation(orchestrator):
    """Test task creation and processing."""
    task_id = await orchestrator.create_task("Test task", {"test": True})
    assert task_id is not None
    
    # Wait a moment for processing
    await asyncio.sleep(2)
    
    task_status = await orchestrator.get_task_status(task_id)
    assert task_status is not None
    assert task_status["status"] in ["completed", "in_progress", "pending"]


@pytest.mark.asyncio
async def test_task_listing(orchestrator):
    """Test task listing functionality."""
    # Create a few tasks
    task_ids = []
    for i in range(3):
        task_id = await orchestrator.create_task(f"Test task {i}", {"index": i})
        task_ids.append(task_id)
    
    # Wait for processing
    await asyncio.sleep(3)
    
    # List tasks
    task_list = await orchestrator.list_tasks(page=1, per_page=10)
    assert "tasks" in task_list
    assert task_list["total"] >= 3


if __name__ == "__main__":
    # Simple test runner for manual testing
    async def run_tests():
        print("Running basic WeeKI tests...")
        
        print("Testing configuration...")
        await test_config_loading()
        print("✓ Configuration test passed")
        
        print("Testing database...")
        await test_database_initialization()
        print("✓ Database test passed")
        
        print("Creating orchestrator...")
        db_manager.initialize()
        await db_manager.create_tables_async()
        orch = AgentOrchestrator()
        await orch.initialize()
        
        print("Testing orchestrator...")
        await test_orchestrator_initialization(orch)
        print("✓ Orchestrator test passed")
        
        print("Testing task creation...")
        await test_task_creation(orch)
        print("✓ Task creation test passed")
        
        print("Testing task listing...")
        await test_task_listing(orch)
        print("✓ Task listing test passed")
        
        await orch.shutdown()
        await db_manager.close()
        
        print("All tests passed! ✓")
    
    asyncio.run(run_tests())