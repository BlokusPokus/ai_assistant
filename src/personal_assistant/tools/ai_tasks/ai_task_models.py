"""
Data models for AI Task Tracker system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
import uuid


class TaskStatus(Enum):
    """Status enumeration for AI tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskComplexity(Enum):
    """Complexity levels for AI tasks."""
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3
    ADVANCED = 4
    EXPERT = 5


@dataclass
class AITask:
    """AI Task data model for session-based task management."""
    
    # Core fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    status: TaskStatus = TaskStatus.PENDING
    complexity: TaskComplexity = TaskComplexity.SIMPLE
    
    # Session management
    conversation_id: str = ""
    
    # Dependency management (linear, max 6 levels)
    dependencies: List[str] = field(default_factory=list)
    parent_task_id: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # AI-specific fields
    auto_generated: bool = True
    ai_reasoning: Optional[str] = None  # Why the AI created this task
    
    def __post_init__(self):
        """Validate task after initialization."""
        if not self.content.strip():
            raise ValueError("Task content cannot be empty")
        
        if not self.conversation_id:
            raise ValueError("conversation_id is required")
        
        # Validate dependency depth (max 6 levels)
        if len(self.dependencies) > 6:
            raise ValueError("Maximum dependency depth is 6 levels")
    
    def update_status(self, new_status: TaskStatus) -> None:
        """Update task status with timestamp."""
        self.status = new_status
        self.updated_at = datetime.now()
        
        if new_status == TaskStatus.COMPLETED:
            self.completed_at = datetime.now()
    
    def add_dependency(self, task_id: str) -> None:
        """Add a dependency task."""
        if len(self.dependencies) >= 6:
            raise ValueError("Maximum dependency depth is 6 levels")
        
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)
            self.updated_at = datetime.now()
    
    def remove_dependency(self, task_id: str) -> None:
        """Remove a dependency task."""
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)
            self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "status": self.status.value,
            "complexity": self.complexity.value,
            "conversation_id": self.conversation_id,
            "dependencies": self.dependencies,
            "parent_task_id": self.parent_task_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "auto_generated": self.auto_generated,
            "ai_reasoning": self.ai_reasoning,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AITask":
        """Create task from dictionary."""
        task = cls(
            id=data["id"],
            content=data["content"],
            status=TaskStatus(data["status"]),
            complexity=TaskComplexity(data["complexity"]),
            conversation_id=data["conversation_id"],
            dependencies=data.get("dependencies", []),
            parent_task_id=data.get("parent_task_id"),
            auto_generated=data.get("auto_generated", True),
            ai_reasoning=data.get("ai_reasoning"),
        )
        
        # Set timestamps
        if "created_at" in data:
            task.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            task.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("completed_at"):
            task.completed_at = datetime.fromisoformat(data["completed_at"])
        
        return task


