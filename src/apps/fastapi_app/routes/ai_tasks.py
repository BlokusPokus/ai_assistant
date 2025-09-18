import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.tools.ai_scheduler import AITaskManager

# Create router
router = APIRouter(prefix="/api/v1/ai-tasks", tags=["ai-tasks"])

logger = logging.getLogger(__name__)

async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user_db(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from database."""
    if not hasattr(request.state, "authenticated") or not request.state.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    user_id = request.state.user_id
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user

@router.get("/test")
async def test_ai_tasks_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user_db),
):
    """Test endpoint to check if AI tasks functionality is working."""
    try:
        logger.info(f"Testing AI tasks endpoint for user {current_user.id}")
        return {
            "message": "AI tasks endpoint is working",
            "user_id": current_user.id,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Test endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Test failed: {str(e)}",
        )

@router.get("/db-check")
async def check_database(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Check if ai_tasks table exists and is accessible."""
    try:
        # Check if ai_tasks table exists
        result = await db.execute(text("SELECT COUNT(*) FROM ai_tasks"))
        count = result.scalar()
        
        return {
            "message": "Database connection successful",
            "ai_tasks_table_exists": True,
            "total_ai_tasks": count,
            "user_id": current_user.id,
        }
    except Exception as e:
        logger.error(f"Database check error: {e}")
        return {
            "message": "Database check failed",
            "ai_tasks_table_exists": False,
            "error": str(e),
            "user_id": current_user.id,
        }

@router.get("/")
async def get_ai_tasks(
    request: Request,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    task_type_filter: Optional[str] = Query(None, description="Filter by task type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Get AI tasks for the current user with optional filtering."""
    try:
        logger.info(f"Fetching AI tasks for user {current_user.id}")
        task_manager = AITaskManager()
        
        # Get tasks with filtering (only status and task_type are supported)
        tasks = await task_manager.get_user_tasks(
            user_id=current_user.id,
            status=status_filter,
            task_type=task_type_filter,
            limit=100,  # Add reasonable limit
        )
        
        return {
            "tasks": [task.as_dict() for task in tasks],
            "count": len(tasks),
        }
        
    except Exception as e:
        logger.error(f"Error fetching AI tasks for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch AI tasks: {str(e)}",
        )

@router.post("/")
async def create_ai_task(
    request: Request,
    task_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Create a new AI task for the current user."""
    try:
        logger.info(f"Creating AI task for user {current_user.id}: {task_data.get('title')}")
        task_manager = AITaskManager()
        
        task = await task_manager.create_task(
            user_id=current_user.id,
            title=task_data.get('title'),
            description=task_data.get('description'),
            task_type=task_data.get('task_type', 'reminder'),
            schedule_type=task_data.get('schedule_type', 'once'),
            schedule_config=task_data.get('schedule_config'),
            next_run_at=task_data.get('next_run_at'),
            ai_context=task_data.get('ai_context'),
            notification_channels=task_data.get('notification_channels', []),
        )
        
        return {
            "message": "AI task created successfully",
            "task": task.as_dict(),
        }
        
    except Exception as e:
        logger.error(f"Error creating AI task for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create AI task: {str(e)}",
        )

@router.put("/{task_id}")
async def update_ai_task(
    request: Request,
    task_id: int,
    task_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Update an existing AI task for the current user."""
    try:
        logger.info(f"Updating AI task {task_id} for user {current_user.id}")
        task_manager = AITaskManager()
        
        result = await task_manager.update_task(
            task_id=task_id,
            user_id=current_user.id,
            update_data=task_data,
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to update task"),
            )
        
        return {
            "message": "AI task updated successfully",
            "result": result,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating AI task {task_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update AI task: {str(e)}",
        )

@router.delete("/{task_id}")
async def delete_ai_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Delete an AI task for the current user."""
    try:
        logger.info(f"Deleting AI task {task_id} for user {current_user.id}")
        task_manager = AITaskManager()
        
        success = await task_manager.delete_task(
            task_id=task_id,
            user_id=current_user.id,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or unauthorized",
            )
        
        return {"message": "AI task deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting AI task {task_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete AI task: {str(e)}",
        )

@router.post("/{task_id}/execute")
async def execute_ai_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Manually execute an AI task for the current user."""
    try:
        logger.info(f"Executing AI task {task_id} for user {current_user.id}")
        task_manager = AITaskManager()
        
        # First get the task to verify ownership
        tasks = await task_manager.get_user_tasks(
            user_id=current_user.id,
            limit=1000,  # Get all tasks to find the specific one
        )
        
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or unauthorized",
            )
        
        # Import TaskExecutor to execute the task
        from personal_assistant.tools.ai_scheduler import TaskExecutor
        executor = TaskExecutor()
        
        result = await executor.execute_task(task)
        
        return {
            "message": "AI task executed successfully",
            "result": result,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing AI task {task_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute AI task: {str(e)}",
        )

@router.post("/{task_id}/pause")
async def pause_ai_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Pause or resume an AI task for the current user."""
    try:
        logger.info(f"Pausing/resuming AI task {task_id} for user {current_user.id}")
        task_manager = AITaskManager()
        
        # First get the task to check current status
        tasks = await task_manager.get_user_tasks(
            user_id=current_user.id,
            limit=1000,  # Get all tasks to find the specific one
        )
        
        task = next((t for t in tasks if t.id == task_id), None)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found or unauthorized",
            )
        
        # Toggle status: if active -> paused, if paused -> active
        new_status = "paused" if task.status == "active" else "active"
        
        success = await task_manager.update_task_status(
            task_id=task_id,
            status=new_status,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update task status",
            )
        
        return {
            "message": f"AI task {'paused' if new_status == 'paused' else 'resumed'} successfully",
            "status": new_status,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing/resuming AI task {task_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause/resume AI task: {str(e)}",
        )
