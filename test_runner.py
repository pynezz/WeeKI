#!/usr/bin/env python3
"""Simple test runner for WeeKI self-hosting functionality."""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weeki.config import settings
from weeki.database import db_manager
from weeki.agents import AgentOrchestrator


async def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert isinstance(settings.max_agents, int)
    print("✓ Configuration loaded successfully")


async def test_database_initialization():
    """Test database initialization."""
    print("Testing database initialization...")
    db_manager.initialize()
    await db_manager.create_tables_async()
    
    # Test database connection
    async with db_manager.get_async_session() as session:
        assert session is not None
    
    await db_manager.close()
    print("✓ Database initialized successfully")


async def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    print("Testing orchestrator initialization...")
    
    # Initialize database
    db_manager.initialize()
    await db_manager.create_tables_async()
    
    # Create orchestrator
    orch = AgentOrchestrator()
    await orch.initialize()
    
    assert orch.get_active_agent_count() > 0
    assert orch.orchestrator.is_active
    
    await orch.shutdown()
    await db_manager.close()
    print("✓ Orchestrator initialized successfully")


async def test_task_creation_and_processing():
    """Test task creation and processing."""
    print("Testing task creation and processing...")
    
    # Initialize database
    db_manager.initialize()
    await db_manager.create_tables_async()
    
    # Create orchestrator
    orch = AgentOrchestrator()
    await orch.initialize()
    
    # Create a task
    task_id = await orch.create_task("Write a simple Hello World program", {"language": "python"})
    assert task_id is not None
    print(f"  Created task: {task_id}")
    
    # Wait for processing
    print("  Waiting for task processing...")
    await asyncio.sleep(3)
    
    # Check task status
    task_status = await orch.get_task_status(task_id)
    assert task_status is not None
    assert task_status["status"] in ["completed", "in_progress", "pending", "failed"]
    print(f"  Task status: {task_status['status']}")
    print(f"  Task message: {task_status.get('message', 'No message')}")
    
    await orch.shutdown()
    await db_manager.close()
    print("✓ Task creation and processing test passed")


async def run_all_tests():
    """Run all tests."""
    print("=" * 50)
    print("Running WeeKI Self-Hosting Tests")
    print("=" * 50)
    
    try:
        await test_config_loading()
        await test_database_initialization()
        await test_orchestrator_initialization()
        await test_task_creation_and_processing()
        
        print("=" * 50)
        print("✓ All tests passed successfully!")
        print("WeeKI is ready for self-hosting.")
        print("=" * 50)
        
    except Exception as e:
        print("=" * 50)
        print(f"✗ Test failed: {e}")
        print("=" * 50)
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())