# AI Task Tab Implementation Guide

## Step-by-Step Implementation

### Phase 1: Backend API Development

#### Step 1.1: Create FastAPI Router

Create `src/apps/fastapi_app/routes/ai_tasks.py`:

```python
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from apps.fastapi_app.middleware.auth import get_current_user
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

@router.get("/")
async def get_ai_tasks(
    request: Request,
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    task_type_filter: Optional[str] = Query(None, description="Filter by task type"),
    schedule_type_filter: Optional[str] = Query(None, description="Filter by schedule type"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_db),
):
    """Get AI tasks for the current user with optional filtering."""
    try:
        logger.info(f"Fetching AI tasks for user {current_user.id}")
        task_manager = AITaskManager()

        # Get tasks with filtering
        tasks = await task_manager.get_user_tasks(
            user_id=current_user.id,
            status=status_filter,
            task_type=task_type_filter,
            schedule_type=schedule_type_filter,
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

        task = await task_manager.update_task(
            task_id=task_id,
            user_id=current_user.id,
            **task_data,
        )

        return {
            "message": "AI task updated successfully",
            "task": task.as_dict(),
        }

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

        await task_manager.delete_task(
            task_id=task_id,
            user_id=current_user.id,
        )

        return {"message": "AI task deleted successfully"}

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

        result = await task_manager.execute_task(
            task_id=task_id,
            user_id=current_user.id,
        )

        return {
            "message": "AI task executed successfully",
            "result": result,
        }

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

        task = await task_manager.toggle_task_status(
            task_id=task_id,
            user_id=current_user.id,
        )

        return {
            "message": f"AI task {'paused' if task.status == 'paused' else 'resumed'} successfully",
            "task": task.as_dict(),
        }

    except Exception as e:
        logger.error(f"Error pausing/resuming AI task {task_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause/resume AI task: {str(e)}",
        )
```

#### Step 1.2: Update Main App

Add to `src/apps/fastapi_app/main.py`:

```python
from apps.fastapi_app.routes import (
    # ... existing imports
    ai_tasks,  # Add this import
)

# ... existing code

app.include_router(ai_tasks.router)  # Add this line
```

### Phase 2: Frontend Store Development

#### Step 2.1: Create Zustand Store

Create `src/apps/frontend/src/stores/aiTaskStore.ts`:

```typescript
import { create } from "zustand";
import api from "../services/api";

interface AITask {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  task_type: "reminder" | "automated_task" | "periodic_task";
  schedule_type: "once" | "daily" | "weekly" | "monthly" | "custom";
  schedule_config?: any;
  next_run_at?: string;
  last_run_at?: string;
  status: "active" | "paused" | "completed" | "failed";
  ai_context?: string;
  notification_channels: string[];
  created_at: string;
  updated_at: string;
}

interface AITaskState {
  tasks: AITask[];
  loading: boolean;
  error: string | null;
  fetchTasks: () => Promise<void>;
  createTask: (
    task: Omit<AITask, "id" | "user_id" | "created_at" | "updated_at">
  ) => Promise<void>;
  updateTask: (id: number, updates: Partial<AITask>) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
  executeTask: (id: number) => Promise<void>;
  pauseTask: (id: number) => Promise<void>;
}

export const useAITaskStore = create<AITaskState>((set, get) => ({
  tasks: [],
  loading: false,
  error: null,

  fetchTasks: async () => {
    set({ loading: true, error: null });
    try {
      const response = await api.get("/ai-tasks");
      set({ tasks: response.data.tasks || [], loading: false });
    } catch (error) {
      console.error("Error fetching AI tasks:", error);
      set({
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
        loading: false,
      });
    }
  },

  createTask: async (task) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post("/ai-tasks", task);
      set((state) => ({
        tasks: [response.data.task, ...state.tasks],
        loading: false,
      }));
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
        loading: false,
      });
    }
  },

  updateTask: async (id, updates) => {
    set({ loading: true, error: null });
    try {
      const response = await api.put(`/ai-tasks/${id}`, updates);
      set((state) => ({
        tasks: state.tasks.map((task) =>
          task.id === id ? response.data.task : task
        ),
        loading: false,
      }));
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
        loading: false,
      });
    }
  },

  deleteTask: async (id) => {
    set({ loading: true, error: null });
    try {
      await api.delete(`/ai-tasks/${id}`);
      set((state) => ({
        tasks: state.tasks.filter((task) => task.id !== id),
        loading: false,
      }));
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
        loading: false,
      });
    }
  },

  executeTask: async (id) => {
    set({ loading: true, error: null });
    try {
      await api.post(`/ai-tasks/${id}/execute`);
      // Refresh tasks to get updated status
      await get().fetchTasks();
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
        loading: false,
      });
    }
  },

  pauseTask: async (id) => {
    set({ loading: true, error: null });
    try {
      const response = await api.post(`/ai-tasks/${id}/pause`);
      set((state) => ({
        tasks: state.tasks.map((task) =>
          task.id === id ? response.data.task : task
        ),
        loading: false,
      }));
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Unknown error occurred",
        loading: false,
      });
    }
  },
}));
```

### Phase 3: Frontend Components

#### Step 3.1: Create AITaskItem Component

Create `src/apps/frontend/src/components/ai-tasks/AITaskItem.tsx`:

```typescript
import React from "react";
import { useAITaskStore } from "../../stores/aiTaskStore";
import { Card } from "@/components/ui";
import {
  Play,
  Pause,
  Trash2,
  Clock,
  Calendar,
  Brain,
  Bell,
} from "lucide-react";

interface AITaskItemProps {
  task: {
    id: number;
    title: string;
    description?: string;
    task_type: string;
    schedule_type: string;
    next_run_at?: string;
    status: string;
    notification_channels: string[];
  };
}

export const AITaskItem: React.FC<AITaskItemProps> = ({ task }) => {
  const { deleteTask, executeTask, pauseTask } = useAITaskStore();

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "paused":
        return "bg-yellow-100 text-yellow-800";
      case "completed":
        return "bg-blue-100 text-blue-800";
      case "failed":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getTaskTypeIcon = (taskType: string) => {
    switch (taskType) {
      case "reminder":
        return <Bell className="w-4 h-4" />;
      case "automated_task":
        return <Brain className="w-4 h-4" />;
      case "periodic_task":
        return <Clock className="w-4 h-4" />;
      default:
        return <Brain className="w-4 h-4" />;
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {getTaskTypeIcon(task.task_type)}
              <h3 className="font-semibold text-gray-900">{task.title}</h3>
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                  task.status
                )}`}
              >
                {task.status}
              </span>
            </div>

            {task.description && (
              <p className="text-gray-600 text-sm mb-2">{task.description}</p>
            )}

            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <Calendar className="w-4 h-4" />
                <span>{task.schedule_type}</span>
              </div>

              {task.next_run_at && (
                <div className="flex items-center space-x-1">
                  <Clock className="w-4 h-4" />
                  <span>{new Date(task.next_run_at).toLocaleDateString()}</span>
                </div>
              )}

              {task.notification_channels.length > 0 && (
                <div className="flex items-center space-x-1">
                  <Bell className="w-4 h-4" />
                  <span>{task.notification_channels.join(", ")}</span>
                </div>
              )}
            </div>
          </div>

          <div className="flex space-x-2">
            {task.status === "active" ? (
              <button
                onClick={() => pauseTask(task.id)}
                className="p-2 hover:bg-yellow-100 rounded text-yellow-600 hover:text-yellow-700"
                title="Pause task"
              >
                <Pause className="w-4 h-4" />
              </button>
            ) : (
              <button
                onClick={() => pauseTask(task.id)}
                className="p-2 hover:bg-green-100 rounded text-green-600 hover:text-green-700"
                title="Resume task"
              >
                <Play className="w-4 h-4" />
              </button>
            )}

            <button
              onClick={() => executeTask(task.id)}
              className="p-2 hover:bg-blue-100 rounded text-blue-600 hover:text-blue-700"
              title="Execute task"
            >
              <Play className="w-4 h-4" />
            </button>

            <button
              onClick={() => deleteTask(task.id)}
              className="p-2 hover:bg-red-100 rounded text-red-600 hover:text-red-700"
              title="Delete task"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </Card>
  );
};
```

#### Step 3.2: Create AITaskList Component

Create `src/apps/frontend/src/components/ai-tasks/AITaskList.tsx`:

```typescript
import React, { useState } from "react";
import { useAITaskStore } from "../../stores/aiTaskStore";
import { AITaskItem } from "./AITaskItem";
import { Card } from "@/components/ui";
import { Plus } from "lucide-react";

interface AITaskListProps {
  showAddForm: boolean;
  onToggleAddForm: () => void;
}

export const AITaskList: React.FC<AITaskListProps> = ({
  showAddForm,
  onToggleAddForm,
}) => {
  const { tasks, loading, error } = useAITaskStore();
  const [filter, setFilter] = useState<
    "all" | "active" | "paused" | "completed" | "failed"
  >("all");
  const [taskTypeFilter, setTaskTypeFilter] = useState<
    "all" | "reminder" | "automated_task" | "periodic_task"
  >("all");

  const filteredTasks = tasks.filter((task) => {
    const matchesStatus = filter === "all" || task.status === filter;
    const matchesType =
      taskTypeFilter === "all" || task.task_type === taskTypeFilter;
    return matchesStatus && matchesType;
  });

  const filterOptions = [
    { value: "all", label: "All Tasks", count: tasks.length },
    {
      value: "active",
      label: "Active",
      count: tasks.filter((task) => task.status === "active").length,
    },
    {
      value: "paused",
      label: "Paused",
      count: tasks.filter((task) => task.status === "paused").length,
    },
    {
      value: "completed",
      label: "Completed",
      count: tasks.filter((task) => task.status === "completed").length,
    },
    {
      value: "failed",
      label: "Failed",
      count: tasks.filter((task) => task.status === "failed").length,
    },
  ];

  const taskTypeOptions = [
    { value: "all", label: "All Types", count: tasks.length },
    {
      value: "reminder",
      label: "Reminders",
      count: tasks.filter((task) => task.task_type === "reminder").length,
    },
    {
      value: "automated_task",
      label: "Automated",
      count: tasks.filter((task) => task.task_type === "automated_task").length,
    },
    {
      value: "periodic_task",
      label: "Periodic",
      count: tasks.filter((task) => task.task_type === "periodic_task").length,
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-red-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              Error loading AI tasks
            </h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <Card>
        <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
          {/* Status Filter */}
          <div className="flex space-x-2">
            {filterOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setFilter(option.value as any)}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  filter === option.value
                    ? "bg-blue-100 text-blue-700 border border-blue-200"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {option.label} ({option.count})
              </button>
            ))}
          </div>

          {/* Task Type Filter */}
          <div className="flex space-x-2">
            {taskTypeOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => setTaskTypeFilter(option.value as any)}
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  taskTypeFilter === option.value
                    ? "bg-green-100 text-green-700 border border-green-200"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {option.label} ({option.count})
              </button>
            ))}
          </div>

          {/* Count */}
          <div className="text-sm text-gray-500 ml-auto">
            {filteredTasks.length} task(s) found
          </div>

          <button
            onClick={onToggleAddForm}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-2xl border border-white/30 bg-white/25 backdrop-blur-xl shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden text-gray-800 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          >
            <Plus className="w-4 h-4 mr-2" />
            {showAddForm ? "Cancel" : "Add AI Task"}
          </button>
        </div>
      </Card>

      {/* Task List */}
      {filteredTasks.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
              />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            No AI tasks found
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {filter === "all" && taskTypeFilter === "all"
              ? "Get started by creating your first AI task."
              : `No ${filter === "all" ? taskTypeFilter : filter} tasks found.`}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredTasks.map((task) => (
            <AITaskItem key={task.id} task={task} />
          ))}
        </div>
      )}
    </div>
  );
};
```

#### Step 3.3: Create AITaskForm Component

Create `src/apps/frontend/src/components/ai-tasks/AITaskForm.tsx`:

```typescript
import React, { useState } from "react";
import { useAITaskStore } from "../../stores/aiTaskStore";
import { Card } from "@/components/ui";

interface AITaskFormProps {
  onSuccess: () => void;
}

export const AITaskForm: React.FC<AITaskFormProps> = ({ onSuccess }) => {
  const { createTask } = useAITaskStore();
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    task_type: "reminder",
    schedule_type: "once",
    ai_context: "",
    notification_channels: [] as string[],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTask(formData);
      onSuccess();
    } catch (error) {
      console.error("Error creating AI task:", error);
    }
  };

  const handleNotificationChange = (channel: string, checked: boolean) => {
    setFormData((prev) => ({
      ...prev,
      notification_channels: checked
        ? [...prev.notification_channels, channel]
        : prev.notification_channels.filter((c) => c !== channel),
    }));
  };

  return (
    <Card>
      <div className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Create AI Task
        </h3>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, title: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Task Type
              </label>
              <select
                value={formData.task_type}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    task_type: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="reminder">Reminder</option>
                <option value="automated_task">Automated Task</option>
                <option value="periodic_task">Periodic Task</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Schedule Type
              </label>
              <select
                value={formData.schedule_type}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    schedule_type: e.target.value,
                  }))
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="once">Once</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="custom">Custom</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              AI Context
            </label>
            <textarea
              value={formData.ai_context}
              onChange={(e) =>
                setFormData((prev) => ({ ...prev, ai_context: e.target.value }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Provide context for AI processing..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notification Channels
            </label>
            <div className="space-y-2">
              {["sms", "email", "in_app"].map((channel) => (
                <label key={channel} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.notification_channels.includes(channel)}
                    onChange={(e) =>
                      handleNotificationChange(channel, e.target.checked)
                    }
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700 capitalize">
                    {channel}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onSuccess}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Create Task
            </button>
          </div>
        </form>
      </div>
    </Card>
  );
};
```

#### Step 3.4: Create AITaskTab Component

Create `src/apps/frontend/src/components/ai-tasks/AITaskTab.tsx`:

```typescript
import React, { useEffect, useState } from "react";
import { useAITaskStore } from "../../stores/aiTaskStore";
import { AITaskForm } from "./AITaskForm";
import { AITaskList } from "./AITaskList";

export const AITaskTab: React.FC = () => {
  const { fetchTasks } = useAITaskStore();
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return (
    <div className="px-4 sm:px-0">
      {/* Page Header */}
      <div className="mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI Tasks</h2>
          <p className="mt-2 text-sm text-gray-600">
            Manage your AI-driven tasks, reminders, and automated workflows.
          </p>
        </div>
      </div>

      {/* Add Task Form - Only show when toggled */}
      {showAddForm && (
        <div className="mb-6">
          <AITaskForm onSuccess={() => setShowAddForm(false)} />
        </div>
      )}

      {/* Task List - Main View */}
      <AITaskList
        showAddForm={showAddForm}
        onToggleAddForm={() => setShowAddForm(!showAddForm)}
      />
    </div>
  );
};
```

### Phase 4: Navigation Integration

#### Step 4.1: Update Sidebar Navigation

Add to `src/apps/frontend/src/components/dashboard/Sidebar.tsx`:

```typescript
// Add to imports
import { Bot } from 'lucide-react';

// Add to allNavigationItems array (around line 69)
{
  label: 'AI Tasks',
  href: '/dashboard/ai-tasks',
  icon: Bot,
},
```

#### Step 4.2: Update Role Utils

Add to `src/apps/frontend/src/utils/roleUtils.ts`:

```typescript
// Add to allItems array (around line 159)
{
  label: 'AI Tasks',
  href: '/dashboard/ai-tasks',
  requiredRole: null,
},
```

#### Step 4.3: Update Dashboard Header

Add to `src/apps/frontend/src/components/dashboard/DashboardHeader.tsx`:

```typescript
// Add to pathMap (around line 20)
'/dashboard/ai-tasks': 'AI Tasks',
```

#### Step 4.4: Create Standalone Page

Create `src/apps/frontend/src/pages/dashboard/AITasksPage.tsx`:

```typescript
import React from "react";
import { AITaskTab } from "@/components/ai-tasks/AITaskTab";

const AITasksPage: React.FC = () => {
  return <AITaskTab />;
};

export default AITasksPage;
```

#### Step 4.5: Update App Routing

Add to `src/apps/frontend/src/App.tsx`:

```typescript
// Add import
import AITasksPage from "./pages/dashboard/AITasksPage";

// Add route
<Route path="/dashboard/ai-tasks" element={<AITasksPage />} />;
```

#### Step 4.6: Update Dashboard Index

Add to `src/apps/frontend/src/pages/dashboard/index.ts`:

```typescript
export { default as AITasksPage } from "./AITasksPage";
```

## Testing Strategy

### Unit Tests

- Test individual components in isolation
- Test store actions and state updates
- Test API integration functions

### Integration Tests

- Test component interactions
- Test API endpoint functionality
- Test authentication flow

### E2E Tests

- Test complete user workflows
- Test task creation and management
- Test filtering and sorting

## Deployment Checklist

- [ ] Backend API endpoints implemented and tested
- [ ] Frontend components created and styled
- [ ] Navigation integration completed
- [ ] Authentication and authorization working
- [ ] Error handling implemented
- [ ] Loading states implemented
- [ ] Responsive design verified
- [ ] Cross-browser compatibility tested
- [ ] Performance optimized
- [ ] Documentation updated

This implementation guide provides a comprehensive roadmap for building the AI Tasks tab with full integration into the existing system architecture.
