"""Agent orchestration system for WeeKI."""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class AgentType(Enum):
    """Types of agents in the system."""
    ORCHESTRATOR = "orchestrator"
    SPECIALIST = "specialist"
    UTILITY = "utility"


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Task data structure."""
    id: str
    directive: str
    context: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    created_at: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    completed_at: Optional[float] = None


class BaseAgent:
    """Base agent class."""
    
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.id = agent_id
        self.type = agent_type
        self.logger = logging.getLogger(f"agent.{agent_id}")
        self.is_active = False
    
    async def initialize(self):
        """Initialize the agent."""
        self.logger.info(f"Initializing {self.type.value} agent: {self.id}")
        self.is_active = True
    
    async def shutdown(self):
        """Shutdown the agent."""
        self.logger.info(f"Shutting down {self.type.value} agent: {self.id}")
        self.is_active = False
    
    async def process_task(self, task: Task) -> Task:
        """Process a task. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement process_task")


class UtilityAgent(BaseAgent):
    """Utility agent for routine tasks."""
    
    def __init__(self, agent_id: str, specialty: str = "general"):
        super().__init__(agent_id, AgentType.UTILITY)
        self.specialty = specialty
    
    async def process_task(self, task: Task) -> Task:
        """Process utility tasks."""
        self.logger.info(f"Processing utility task: {task.id}")
        
        # Simulate processing
        await asyncio.sleep(1)
        
        task.status = TaskStatus.COMPLETED
        task.message = f"Utility task processed by {self.specialty} agent"
        task.result = {
            "processed_by": self.id,
            "specialty": self.specialty,
            "original_directive": task.directive
        }
        task.completed_at = asyncio.get_event_loop().time()
        
        return task


class SpecialistAgent(BaseAgent):
    """Specialist agent for domain-specific tasks."""
    
    def __init__(self, agent_id: str, domain: str):
        super().__init__(agent_id, AgentType.SPECIALIST)
        self.domain = domain
    
    async def process_task(self, task: Task) -> Task:
        """Process specialist tasks."""
        self.logger.info(f"Processing specialist task in domain {self.domain}: {task.id}")
        
        # Simulate more complex processing
        await asyncio.sleep(2)
        
        task.status = TaskStatus.COMPLETED
        task.message = f"Specialist task completed in domain: {self.domain}"
        task.result = {
            "processed_by": self.id,
            "domain": self.domain,
            "analysis": f"Domain-specific analysis for: {task.directive}",
            "recommendations": ["recommendation_1", "recommendation_2"]
        }
        task.completed_at = asyncio.get_event_loop().time()
        
        return task


class OrchestratorAgent(BaseAgent):
    """Orchestrator agent that coordinates other agents."""
    
    def __init__(self):
        super().__init__("orchestrator", AgentType.ORCHESTRATOR)
        self.specialist_agents: Dict[str, SpecialistAgent] = {}
        self.utility_agents: Dict[str, UtilityAgent] = {}
    
    async def initialize(self):
        """Initialize orchestrator and sub-agents."""
        await super().initialize()
        
        # Initialize specialist agents
        for domain in ["coding", "design", "research", "writing"]:
            agent = SpecialistAgent(f"specialist_{domain}", domain)
            await agent.initialize()
            self.specialist_agents[domain] = agent
        
        # Initialize utility agents
        for specialty in ["data_processing", "formatting", "communication"]:
            agent = UtilityAgent(f"utility_{specialty}", specialty)
            await agent.initialize()
            self.utility_agents[specialty] = agent
    
    async def shutdown(self):
        """Shutdown orchestrator and all sub-agents."""
        # Shutdown specialist agents
        for agent in self.specialist_agents.values():
            await agent.shutdown()
        
        # Shutdown utility agents
        for agent in self.utility_agents.values():
            await agent.shutdown()
        
        await super().shutdown()
    
    def get_active_agent_count(self) -> int:
        """Get the number of active agents."""
        count = 1 if self.is_active else 0  # Self
        count += sum(1 for agent in self.specialist_agents.values() if agent.is_active)
        count += sum(1 for agent in self.utility_agents.values() if agent.is_active)
        return count
    
    async def route_task(self, task: Task) -> BaseAgent:
        """Route task to appropriate agent based on directive analysis."""
        directive_lower = task.directive.lower()
        
        # Simple routing logic based on keywords
        if any(keyword in directive_lower for keyword in ["code", "program", "develop", "build"]):
            return self.specialist_agents.get("coding")
        elif any(keyword in directive_lower for keyword in ["design", "ui", "visual", "interface"]):
            return self.specialist_agents.get("design")
        elif any(keyword in directive_lower for keyword in ["research", "analyze", "study", "investigate"]):
            return self.specialist_agents.get("research")
        elif any(keyword in directive_lower for keyword in ["write", "document", "text", "content"]):
            return self.specialist_agents.get("writing")
        elif any(keyword in directive_lower for keyword in ["format", "process", "convert"]):
            return self.utility_agents.get("data_processing")
        elif any(keyword in directive_lower for keyword in ["communicate", "send", "notify"]):
            return self.utility_agents.get("communication")
        else:
            # Default to general utility agent
            return self.utility_agents.get("data_processing")
    
    async def process_task(self, task: Task) -> Task:
        """Process task by routing to appropriate agent."""
        self.logger.info(f"Orchestrating task: {task.id}")
        
        try:
            task.status = TaskStatus.IN_PROGRESS
            
            # Route to appropriate agent
            agent = await self.route_task(task)
            if not agent:
                task.status = TaskStatus.FAILED
                task.message = "No suitable agent found for task"
                return task
            
            # Process with selected agent
            result_task = await agent.process_task(task)
            
            self.logger.info(f"Task {task.id} completed by agent {agent.id}")
            return result_task
            
        except Exception as e:
            self.logger.error(f"Error processing task {task.id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.message = f"Processing error: {str(e)}"
            task.completed_at = asyncio.get_event_loop().time()
            return task


class AgentOrchestrator:
    """Main orchestrator for the agent system."""
    
    def __init__(self):
        self.orchestrator = OrchestratorAgent()
        self.tasks: Dict[str, Task] = {}
        self.logger = logging.getLogger("orchestrator")
    
    async def initialize(self):
        """Initialize the orchestrator system."""
        self.logger.info("Initializing agent orchestrator system")
        await self.orchestrator.initialize()
    
    async def shutdown(self):
        """Shutdown the orchestrator system."""
        self.logger.info("Shutting down agent orchestrator system")
        await self.orchestrator.shutdown()
    
    def get_active_agent_count(self) -> int:
        """Get the number of active agents."""
        return self.orchestrator.get_active_agent_count()
    
    async def create_task(self, directive: str, context: Dict[str, Any] = None) -> str:
        """Create a new task and return its ID."""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            directive=directive,
            context=context or {}
        )
        
        self.tasks[task_id] = task
        self.logger.info(f"Created task {task_id}: {directive}")
        
        # Process task asynchronously
        asyncio.create_task(self._process_task(task))
        
        return task_id
    
    async def _process_task(self, task: Task):
        """Internal method to process a task."""
        try:
            processed_task = await self.orchestrator.process_task(task)
            self.tasks[task.id] = processed_task
        except Exception as e:
            self.logger.error(f"Error in task processing: {str(e)}")
            task.status = TaskStatus.FAILED
            task.message = f"Internal error: {str(e)}"
            task.completed_at = asyncio.get_event_loop().time()
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "directive": task.directive,
            "status": task.status.value,
            "message": task.message,
            "result": task.result,
            "created_at": task.created_at,
            "completed_at": task.completed_at
        }