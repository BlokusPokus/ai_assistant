"""
AI Tasks API endpoints for managing AI-generated tasks.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from personal_assistant.tools.ai_tasks.ai_task_service import ai_task_service
from personal_assistant.tools.ai_tasks.ai_task_models import TaskStatus
from personal_assistant.database.models.users import User
from personal_assistant.database.models.ai_tasks import AITask as DBAITask
from personal_assistant.database.session import AsyncSessionLocal
from apps.fastapi_app.routes.auth import get_current_user
from personal_assistant.workers.tasks.ai_tasks import execute_single_ai_task
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
    """Request model for creating AI tasks (in-memory, conversation-based)."""
    content: str
    conversation_id: str
    complexity: int = 1
    dependencies: List[str] = []
    parent_task_id: Optional[str] = None
    ai_reasoning: Optional[str] = None


class AITaskDBCreateRequest(BaseModel):
    """Request model for creating AI tasks in DB (dashboard form). Matches frontend AITaskForm."""
    title: str
    description: Optional[str] = None
    task_type: str = "reminder"  # reminder | automated_task | periodic_task
    schedule_type: str = "once"  # once | daily | weekly | monthly | custom
    schedule_config: Optional[dict] = None
    next_run_at: Optional[str] = None
    status: str = "active"  # active | paused | completed | failed
    ai_context: Optional[str] = None
    notification_channels: List[str] = []


class AITaskUpdateRequest(BaseModel):
    """Request model for updating AI tasks (in-memory service)."""
    content: Optional[str] = None
    status: Optional[str] = None
    complexity: Optional[int] = None
    ai_reasoning: Optional[str] = None


class AITaskDBUpdateRequest(BaseModel):
    """Request model for updating DB AI tasks (dashboard). Matches frontend Partial<AITask>."""
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_config: Optional[dict] = None
    next_run_at: Optional[str] = None
    status: Optional[str] = None
    ai_context: Optional[str] = None
    notification_channels: Optional[List[str]] = None


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


@router.post("/", response_model=dict)
async def create_task(
    request: AITaskDBCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new AI task (DB). Expects dashboard form shape: title, task_type, schedule_type, etc."""
    try:
        next_run_at = None
        if request.next_run_at:
            try:
                s = request.next_run_at.replace("Z", "+00:00")
                next_run_at = datetime.fromisoformat(s)
            except (ValueError, AttributeError):
                pass

        db_task = DBAITask(
            user_id=current_user.id,
            title=request.title,
            description=request.description or None,
            task_type=request.task_type,
            schedule_type=request.schedule_type,
            schedule_config=request.schedule_config,
            next_run_at=next_run_at,
            status=request.status,
            ai_context=request.ai_context or None,
            notification_channels=request.notification_channels or [],
        )
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        task_dict = db_task.as_dict()
        # Frontend expects { task: ... } and same shape as GET list items
        out = {
            "id": str(task_dict["id"]),
            "content": task_dict["title"],
            "status": task_dict["status"],
            "complexity": 1,
            "conversation_id": "",
            "dependencies": [],
            "parent_task_id": None,
            "created_at": task_dict["created_at"] or "",
            "updated_at": task_dict["updated_at"] or "",
            "completed_at": None,
            "auto_generated": False,
            "ai_reasoning": task_dict.get("ai_context"),
            "title": task_dict["title"],
            "description": task_dict.get("description"),
            "task_type": task_dict["task_type"],
            "schedule_type": task_dict["schedule_type"],
            "next_run_at": task_dict.get("next_run_at"),
            "notification_channels": task_dict.get("notification_channels", []),
            "ai_context": task_dict.get("ai_context"),
        }
        return {"task": out}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: int,
    request: AITaskDBUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an AI task (DB). Expects dashboard shape: title, task_type, schedule_type, status, etc."""
    result = await db.execute(select(DBAITask).where(DBAITask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    if request.title is not None:
        task.title = request.title
    if request.description is not None:
        task.description = request.description
    if request.task_type is not None:
        task.task_type = request.task_type
    if request.schedule_type is not None:
        task.schedule_type = request.schedule_type
    if request.schedule_config is not None:
        task.schedule_config = request.schedule_config
    if request.next_run_at is not None:
        try:
            s = request.next_run_at.replace("Z", "+00:00")
            task.next_run_at = datetime.fromisoformat(s)
        except (ValueError, AttributeError):
            pass
    if request.status is not None:
        task.status = request.status
    if request.ai_context is not None:
        task.ai_context = request.ai_context
    if request.notification_channels is not None:
        task.notification_channels = request.notification_channels

    task.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(task)
    task_dict = task.as_dict()
    out = {
        "id": str(task_dict["id"]),
        "content": task_dict["title"],
        "status": task_dict["status"],
        "complexity": 1,
        "conversation_id": "",
        "dependencies": [],
        "parent_task_id": None,
        "created_at": task_dict["created_at"] or "",
        "updated_at": task_dict["updated_at"] or "",
        "completed_at": None,
        "auto_generated": False,
        "ai_reasoning": task_dict.get("ai_context"),
        "title": task_dict["title"],
        "description": task_dict.get("description"),
        "task_type": task_dict["task_type"],
        "schedule_type": task_dict["schedule_type"],
        "next_run_at": task_dict.get("next_run_at"),
        "notification_channels": task_dict.get("notification_channels", []),
        "ai_context": task_dict.get("ai_context"),
    }
    return {"task": out}


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


@router.post("/{task_id}/execute", response_model=dict)
async def execute_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Queue a single AI task for execution (dashboard "Execute" button). Task runs in Celery worker."""
    result = await db.execute(select(DBAITask).where(DBAITask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    execute_single_ai_task.delay(task_id)
    return {"message": "Task queued for execution", "task_id": task_id}


@router.post("/{task_id}/pause", response_model=dict)
async def pause_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set an AI task status to paused (dashboard "Pause" button)."""
    result = await db.execute(select(DBAITask).where(DBAITask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = "paused"
    task.updated_at = datetime.utcnow()
    await db.commit()
    return {"message": "Task paused", "task_id": task_id, "status": "paused"}


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
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an AI task (DB). Requires ownership."""
    result = await db.execute(select(DBAITask).where(DBAITask.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted successfully"}


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