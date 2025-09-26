"""
AI Tasks API endpoints for managing AI-generated tasks.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from personal_assistant.tools.ai_tasks.ai_task_service import ai_task_service
from personal_assistant.tools.ai_tasks.ai_task_models import TaskStatus, TaskComplexity

router = APIRouter(prefix="/api/ai-tasks", tags=["ai-tasks"])


class AITaskResponse(BaseModel):
    """Response model for AI task data."""
    id: str
    content: str
    status: str
    complexity: int
    conversation_id: str
    dependencies: List[str]
    parent_task_id: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    auto_generated: bool
    ai_reasoning: Optional[str] = None


class AITaskCreateRequest(BaseModel):
    """Request model for creating AI tasks."""
    content: str
    conversation_id: str
    complexity: int = 1
    dependencies: List[str] = []
    parent_task_id: Optional[str] = None
    ai_reasoning: Optional[str] = None


class AITaskUpdateRequest(BaseModel):
    """Request model for updating AI tasks."""
    content: Optional[str] = None
    status: Optional[str] = None
    complexity: Optional[int] = None
    ai_reasoning: Optional[str] = None


@router.get("/{conversation_id}", response_model=List[AITaskResponse])
async def get_conversation_tasks(conversation_id: str):
    """Get all AI tasks for a conversation."""
    try:
        tasks = await ai_task_service.get_tasks_by_conversation(conversation_id)
        return [AITaskResponse(**task.to_dict()) for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")


@router.get("/{conversation_id}/next", response_model=Optional[AITaskResponse])
async def get_next_task(conversation_id: str):
    """Get the next task ready for execution."""
    try:
        task = await ai_task_service.get_next_task(conversation_id)
        if task:
            return AITaskResponse(**task.to_dict())
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get next task: {str(e)}")


@router.post("/", response_model=AITaskResponse)
async def create_task(request: AITaskCreateRequest):
    """Create a new AI task."""
    try:
        complexity = TaskComplexity(request.complexity)
        task = await ai_task_service.create_task(
            content=request.content,
            conversation_id=request.conversation_id,
            complexity=complexity,
            dependencies=request.dependencies,
            parent_task_id=request.parent_task_id,
            ai_reasoning=request.ai_reasoning
        )
        return AITaskResponse(**task.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.put("/{task_id}", response_model=AITaskResponse)
async def update_task(task_id: str, request: AITaskUpdateRequest):
    """Update an AI task."""
    try:
        task = await ai_task_service.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update content if provided
        if request.content is not None:
            task = await ai_task_service.update_task_content(task_id, request.content)
        
        # Update status if provided
        if request.status is not None:
            status = TaskStatus(request.status)
            task = await ai_task_service.update_task_status(task_id, status)
        
        # Update complexity if provided
        if request.complexity is not None:
            task.complexity = TaskComplexity(request.complexity)
            task.updated_at = task.updated_at  # Trigger update
        
        # Update AI reasoning if provided
        if request.ai_reasoning is not None:
            task.ai_reasoning = request.ai_reasoning
            task.updated_at = task.updated_at  # Trigger update
        
        return AITaskResponse(**task.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@router.put("/{task_id}/status", response_model=AITaskResponse)
async def update_task_status(task_id: str, status: str):
    """Update task status."""
    try:
        task_status = TaskStatus(status)
        task = await ai_task_service.update_task_status(task_id, task_status)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return AITaskResponse(**task.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid status: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update status: {str(e)}")


@router.post("/{task_id}/dependencies/{dependency_id}")
async def add_dependency(task_id: str, dependency_id: str):
    """Add a dependency to a task."""
    try:
        success = await ai_task_service.add_dependency(task_id, dependency_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add dependency")
        
        return {"message": "Dependency added successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add dependency: {str(e)}")


@router.delete("/{task_id}/dependencies/{dependency_id}")
async def remove_dependency(task_id: str, dependency_id: str):
    """Remove a dependency from a task."""
    try:
        success = await ai_task_service.remove_dependency(task_id, dependency_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to remove dependency")
        
        return {"message": "Dependency removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove dependency: {str(e)}")


@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """Delete an AI task."""
    try:
        success = await ai_task_service.delete_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


@router.delete("/conversation/{conversation_id}")
async def clear_conversation_tasks(conversation_id: str):
    """Clear all tasks for a conversation."""
    try:
        task_count = await ai_task_service.clear_conversation(conversation_id)
        return {"message": f"Cleared {task_count} tasks for conversation {conversation_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear tasks: {str(e)}")


@router.get("/stats")
async def get_service_stats():
    """Get AI task service statistics."""
    try:
        stats = ai_task_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/cleanup")
async def cleanup_expired_sessions():
    """Clean up expired conversation sessions."""
    try:
        cleaned_count = await ai_task_service.cleanup_expired_sessions()
        return {"message": f"Cleaned up {cleaned_count} tasks from expired sessions"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup: {str(e)}")