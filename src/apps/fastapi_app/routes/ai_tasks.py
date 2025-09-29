"""
AI Tasks API endpoints for managing AI-generated tasks.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from personal_assistant.tools.ai_tasks.ai_task_service import ai_task_service
from personal_assistant.tools.ai_tasks.ai_task_models import TaskStatus, TaskComplexity
from personal_assistant.database.models.users import User
from personal_assistant.database.models.ai_tasks import AITask as DBAITask
from personal_assistant.database.session import AsyncSessionLocal
from apps.fastapi_app.routes.auth import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/ai-tasks", tags=["ai-tasks"])


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


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


@router.get("/", response_model=dict)
async def get_user_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all AI tasks for the current user."""
    try:
        print(f"🔍 DEBUG: Getting AI tasks for user {current_user.id}")
        
        # Query database for user's AI tasks
        query = select(DBAITask).where(DBAITask.user_id == current_user.id)
        result = await db.execute(query)
        db_tasks = result.scalars().all()
        
        print(f"📊 DEBUG: Found {len(db_tasks)} AI tasks in database")
        
        # Also check if there are any tasks at all
        all_tasks_query = select(DBAITask)
        all_result = await db.execute(all_tasks_query)
        all_tasks = all_result.scalars().all()
        print(f"📊 DEBUG: Total AI tasks in database: {len(all_tasks)}")
        
        # Convert database tasks to response format
        tasks = []
        for db_task in db_tasks:
            task_dict = db_task.as_dict()
            print(f"📋 DEBUG: Processing task {task_dict['id']}: {task_dict['title']}")
            
            # Convert to AITaskResponse format
            response_task = AITaskResponse(
                id=str(task_dict["id"]),
                content=task_dict["title"],  # Map title to content
                status=task_dict["status"],
                complexity=1,  # Default complexity
                conversation_id="",  # Not applicable for DB tasks
                dependencies=[],  # Not applicable for DB tasks
                parent_task_id=None,
                created_at=task_dict["created_at"],
                updated_at=task_dict["updated_at"],
                completed_at=None,  # Not tracked in DB model
                auto_generated=False,  # DB tasks are user-created
                ai_reasoning=task_dict.get("ai_context")
            )
            
            # Add additional fields that frontend expects
            response_task_dict = response_task.dict()
            response_task_dict.update({
                "title": task_dict["title"],
                "description": task_dict.get("description"),
                "task_type": task_dict["task_type"],
                "schedule_type": task_dict["schedule_type"],
                "next_run_at": task_dict.get("next_run_at"),
                "notification_channels": task_dict.get("notification_channels", []),
                "ai_context": task_dict.get("ai_context")
            })
            tasks.append(response_task_dict)
        
        print(f"✅ DEBUG: Returning {len(tasks)} tasks to frontend")
        # Frontend expects { tasks: [...] } format
        return {"tasks": tasks}
    except Exception as e:
        print(f"❌ DEBUG: Error getting user tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user tasks: {str(e)}")


@router.post("/test-create")
async def create_test_task(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a test AI task for debugging."""
    try:
        print(f"🧪 DEBUG: Creating test task for user {current_user.id}")
        
        # Create a test task
        test_task = DBAITask(
            user_id=current_user.id,
            title="Test AI Task",
            description="This is a test task created for debugging",
            task_type="reminder",
            schedule_type="once",
            status="active",
            ai_context="Test context for debugging"
        )
        
        db.add(test_task)
        await db.commit()
        await db.refresh(test_task)
        
        print(f"✅ DEBUG: Created test task with ID {test_task.id}")
        return {"message": f"Test task created with ID {test_task.id}", "task": test_task.as_dict()}
        
    except Exception as e:
        print(f"❌ DEBUG: Error creating test task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create test task: {str(e)}")


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