"""
Todo management API routes.

This module provides REST API endpoints for todo management including
CRUD operations, filtering, and status updates.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.database.models.users import User
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.tools.todos.todo_tool import TodoTool

# Create router
router = APIRouter(prefix="/api/v1/todos", tags=["todos"])

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
async def test_todos_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user_db),
):
    """Test endpoint to check if todos functionality is working."""
    try:
        logger.info(f"Testing todos endpoint for user {current_user.id}")
        return {
            "message": "Todos endpoint is working",
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
    """Check if todos table exists and is accessible."""
    try:
        from sqlalchemy import text
        
        # Check if todos table exists
        result = await db.execute(text("SELECT COUNT(*) FROM todos"))
        count = result.scalar()
        
        return {
            "message": "Database connection successful",
            "todos_table_exists": True,
            "total_todos": count,
            "user_id": current_user.id,
        }
    except Exception as e:
        logger.error(f"Database check error: {e}")
        return {
            "message": "Database check failed",
            "todos_table_exists": False,
            "error": str(e),
            "user_id": current_user.id,
        }


@router.get("/")
async def get_todos(
    request: Request,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    category_filter: Optional[str] = Query(None, description="Filter by category"),
    priority_filter: Optional[str] = Query(None, description="Filter by priority"),
    include_subtasks: bool = Query(True, description="Include subtasks"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Get todos for the current user with optional filtering."""
    try:
        logger.info(f"Fetching todos for user {current_user.id}")
        todo_tool = TodoTool()
        
        result = await todo_tool.get_todos(
            user_id=current_user.id,
            status=status_filter,
            category=category_filter,
            priority=priority_filter,
            include_subtasks=include_subtasks,
        )
        
        logger.info(f"Todo tool result: {result}")
        
        if not result.get("success"):
            logger.error(f"Todo tool failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to fetch todos"),
            )
        
        return {
            "todos": result.get("todos", []),
            "count": result.get("count", 0),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching todos for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch todos: {str(e)}",
        )


@router.post("/")
async def create_todo(
    request: Request,
    todo_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Create a new todo for the current user."""
    try:
        todo_tool = TodoTool()
        
        # Extract todo data from request
        title = todo_data.get("title")
        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required",
            )
        
        result = await todo_tool.create_todo(
            user_id=current_user.id,
            title=title,
            description=todo_data.get("description"),
            due_date=todo_data.get("due_date"),
            priority=todo_data.get("priority", "medium"),
            category=todo_data.get("category"),
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to create todo"),
            )
        
        return {
            "todo": result.get("todo"),
            "message": result.get("message", "Todo created successfully"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating todo for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create todo",
        )


@router.put("/{todo_id}")
async def update_todo(
    todo_id: int,
    request: Request,
    todo_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Update an existing todo for the current user."""
    try:
        todo_tool = TodoTool()
        
        result = await todo_tool.update_todo(
            todo_id=todo_id,
            user_id=current_user.id,
            title=todo_data.get("title"),
            description=todo_data.get("description"),
            due_date=todo_data.get("due_date"),
            priority=todo_data.get("priority"),
            category=todo_data.get("category"),
            status=todo_data.get("status"),
        )
        
        if not result.get("success"):
            if result.get("error") == "Todo not found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Todo not found",
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to update todo"),
            )
        
        return {
            "todo": result.get("todo"),
            "message": result.get("message", "Todo updated successfully"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo {todo_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update todo",
        )


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Delete a todo for the current user."""
    try:
        todo_tool = TodoTool()
        
        result = await todo_tool.delete_todo(
            todo_id=todo_id,
            user_id=current_user.id,
        )
        
        if not result.get("success"):
            if result.get("error") == "Todo not found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Todo not found",
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to delete todo"),
            )
        
        return {
            "message": result.get("message", "Todo deleted successfully"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting todo {todo_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete todo",
        )


@router.post("/{todo_id}/complete")
async def complete_todo(
    todo_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Mark a todo as completed for the current user."""
    try:
        todo_tool = TodoTool()
        
        result = await todo_tool.complete_todo(
            todo_id=todo_id,
            user_id=current_user.id,
        )
        
        if not result.get("success"):
            if result.get("error") == "Todo not found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Todo not found",
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to complete todo"),
            )
        
        return {
            "todo": result.get("todo"),
            "message": result.get("message", "Todo completed successfully"),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing todo {todo_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete todo",
        )
