"""Base Agent Definition for AI Swarm."""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import datetime
import uuid


class BaseAgent(ABC):
    """Abstract Base Class for all AI Swarm agents."""

    def __init__(self, agent_id: str, name: str, role: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.status = "WAITING"
        self.retry_count = 0
        self.current_task: Optional[str] = None
        self.start_time: Optional[datetime.datetime] = None
        self.end_time: Optional[datetime.datetime] = None

    def start(self, task_description: str):
        """Mark agent as running."""
        self.status = "RUNNING"
        self.current_task = task_description
        self.start_time = datetime.datetime.utcnow()

    def complete(self):
        """Mark agent as completed."""
        self.status = "COMPLETED"
        self.end_time = datetime.datetime.utcnow()

    def fail(self, error: str):
        """Mark agent as failed."""
        self.status = "FAILED"
        self.end_time = datetime.datetime.utcnow()

    def retry(self):
        """Mark agent as retrying."""
        self.status = "RETRYING"
        self.retry_count += 1

    def create_message(
        self,
        to_agent: str,
        message_type: str,
        content: str,
        data: Optional[Dict[str, Any]] = None,
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate structured inter-agent message."""
        return {
            "id": f"msg_{uuid.uuid4().hex[:12]}",
            "from_agent": self.agent_id,
            "to_agent": to_agent,
            "message_type": message_type,
            "task_id": task_id,
            "content": content,
            "data": data or {},
            "timestamp": datetime.datetime.utcnow().isoformat(),
        }

    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent responsibility given current swarm state."""
        pass
