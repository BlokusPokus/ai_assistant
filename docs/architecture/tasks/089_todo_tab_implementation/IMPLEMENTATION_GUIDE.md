# Todo Tab Implementation Guide

## Step-by-Step Implementation

### Phase 1: Project Setup and Component Structure

#### 1.1 Create Component Directory Structure

```bash
mkdir -p src/apps/frontend/src/components/todos
mkdir -p src/apps/frontend/src/pages/dashboard
```

#### 1.2 Create Todo Store

Create `src/apps/frontend/src/stores/todoStore.ts`:

```typescript
import { create } from "zustand";

interface Todo {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  priority: "high" | "medium" | "low";
  category?: string;
  status: "pending" | "in_progress" | "completed" | "cancelled";
  created_at: string;
  updated_at: string;
}

interface TodoStore {
  todos: Todo[];
  loading: boolean;
  error: string | null;
  fetchTodos: () => Promise<void>;
  createTodo: (
    todo: Omit<Todo, "id" | "created_at" | "updated_at">
  ) => Promise<void>;
  updateTodo: (id: number, updates: Partial<Todo>) => Promise<void>;
  deleteTodo: (id: number) => Promise<void>;
  completeTodo: (id: number) => Promise<void>;
}

export const useTodoStore = create<TodoStore>((set, get) => ({
  todos: [],
  loading: false,
  error: null,

  fetchTodos: async () => {
    set({ loading: true, error: null });
    try {
      // API call to fetch todos
      const response = await fetch("/api/todos");
      const data = await response.json();
      set({ todos: data.todos, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  createTodo: async (todo) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch("/api/todos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(todo),
      });
      const newTodo = await response.json();
      set((state) => ({
        todos: [newTodo.todo, ...state.todos],
        loading: false,
      }));
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  updateTodo: async (id, updates) => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`/api/todos/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });
      const updatedTodo = await response.json();
      set((state) => ({
        todos: state.todos.map((todo) =>
          todo.id === id ? updatedTodo.todo : todo
        ),
        loading: false,
      }));
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  deleteTodo: async (id) => {
    set({ loading: true, error: null });
    try {
      await fetch(`/api/todos/${id}`, { method: "DELETE" });
      set((state) => ({
        todos: state.todos.filter((todo) => todo.id !== id),
        loading: false,
      }));
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  completeTodo: async (id) => {
    const { updateTodo } = get();
    await updateTodo(id, { status: "completed" });
  },
}));
```

#### 1.3 Create TodoItem Component

Create `src/apps/frontend/src/components/todos/TodoItem.tsx`:

```typescript
import React, { useState } from "react";
import { useTodoStore } from "../../stores/todoStore";

interface TodoItemProps {
  todo: {
    id: number;
    title: string;
    description?: string;
    due_date?: string;
    priority: "high" | "medium" | "low";
    category?: string;
    status: "pending" | "in_progress" | "completed" | "cancelled";
    created_at: string;
    updated_at: string;
  };
}

export const TodoItem: React.FC<TodoItemProps> = ({ todo }) => {
  const [isEditing, setIsEditing] = useState(false);
  const { updateTodo, deleteTodo, completeTodo } = useTodoStore();

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "low":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "in_progress":
        return "bg-blue-100 text-blue-800";
      case "cancelled":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-yellow-100 text-yellow-800";
    }
  };

  const handleComplete = () => {
    completeTodo(todo.id);
  };

  const handleDelete = () => {
    if (window.confirm("Are you sure you want to delete this todo?")) {
      deleteTodo(todo.id);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <h3
              className={`text-lg font-medium ${
                todo.status === "completed"
                  ? "line-through text-gray-500"
                  : "text-gray-900"
              }`}
            >
              {todo.title}
            </h3>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(
                todo.priority
              )}`}
            >
              {todo.priority}
            </span>
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                todo.status
              )}`}
            >
              {todo.status}
            </span>
          </div>

          {todo.description && (
            <p className="text-gray-600 mb-2">{todo.description}</p>
          )}

          <div className="flex items-center space-x-4 text-sm text-gray-500">
            {todo.category && <span>Category: {todo.category}</span>}
            {todo.due_date && (
              <span>Due: {new Date(todo.due_date).toLocaleDateString()}</span>
            )}
            <span>
              Created: {new Date(todo.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          {todo.status !== "completed" && (
            <button
              onClick={handleComplete}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              ✓ Complete
            </button>
          )}
          <button
            onClick={handleDelete}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            🗑️ Delete
          </button>
        </div>
      </div>
    </div>
  );
};
```

### Phase 2: Main Components

#### 2.1 Create TodoForm Component

Create `src/apps/frontend/src/components/todos/TodoForm.tsx`:

```typescript
import React, { useState } from "react";
import { useTodoStore } from "../../stores/todoStore";

export const TodoForm: React.FC = () => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [priority, setPriority] = useState<"high" | "medium" | "low">("medium");
  const [category, setCategory] = useState("");
  const { createTodo, loading } = useTodoStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    await createTodo({
      title: title.trim(),
      description: description.trim() || undefined,
      due_date: dueDate || undefined,
      priority,
      category: category.trim() || undefined,
      status: "pending",
    });

    // Reset form
    setTitle("");
    setDescription("");
    setDueDate("");
    setPriority("medium");
    setCategory("");
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Todo</h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter todo title..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter description..."
            rows={3}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Due Date
            </label>
            <input
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) =>
                setPriority(e.target.value as "high" | "medium" | "low")
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <input
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Work, Personal"
            />
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading || !title.trim()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Adding..." : "Add Todo"}
          </button>
        </div>
      </form>
    </div>
  );
};
```

#### 2.2 Create TodoList Component

Create `src/apps/frontend/src/components/todos/TodoList.tsx`:

```typescript
import React, { useState } from "react";
import { useTodoStore } from "../../stores/todoStore";
import { TodoItem } from "./TodoItem";

export const TodoList: React.FC = () => {
  const { todos, loading, error } = useTodoStore();
  const [filter, setFilter] = useState<"all" | "pending" | "completed">("all");
  const [sortBy, setSortBy] = useState<"created_at" | "due_date" | "priority">(
    "created_at"
  );

  const filteredTodos = todos.filter((todo) => {
    if (filter === "all") return true;
    return todo.status === filter;
  });

  const sortedTodos = [...filteredTodos].sort((a, b) => {
    switch (sortBy) {
      case "due_date":
        if (!a.due_date && !b.due_date) return 0;
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      case "priority":
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      default:
        return (
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
    }
  });

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
              Error loading todos
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
      {/* Filters and Sorting */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Filter
              </label>
              <select
                value={filter}
                onChange={(e) =>
                  setFilter(e.target.value as "all" | "pending" | "completed")
                }
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Todos</option>
                <option value="pending">Pending</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sort By
              </label>
              <select
                value={sortBy}
                onChange={(e) =>
                  setSortBy(
                    e.target.value as "created_at" | "due_date" | "priority"
                  )
                }
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="created_at">Created Date</option>
                <option value="due_date">Due Date</option>
                <option value="priority">Priority</option>
              </select>
            </div>
          </div>

          <div className="text-sm text-gray-500">
            {sortedTodos.length} todo(s) found
          </div>
        </div>
      </div>

      {/* Todo List */}
      {sortedTodos.length === 0 ? (
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
            No todos found
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {filter === "all"
              ? "Get started by creating your first todo."
              : `No ${filter} todos found.`}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedTodos.map((todo) => (
            <TodoItem key={todo.id} todo={todo} />
          ))}
        </div>
      )}
    </div>
  );
};
```

### Phase 3: Main Todo Tab Component

#### 3.1 Create TodoTab Component

Create `src/apps/frontend/src/components/todos/TodoTab.tsx`:

```typescript
import React, { useEffect } from "react";
import { useTodoStore } from "../../stores/todoStore";
import { TodoForm } from "./TodoForm";
import { TodoList } from "./TodoList";

export const TodoTab: React.FC = () => {
  const { fetchTodos, loading } = useTodoStore();

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  return (
    <div className="px-4 sm:px-0">
      {/* Page Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">My Todos</h2>
        <p className="mt-2 text-sm text-gray-600">
          Manage your tasks and stay organized with your personal todo list.
        </p>
      </div>

      {/* Add Todo Form */}
      <TodoForm />

      {/* Todo List */}
      <TodoList />
    </div>
  );
};
```

### Phase 4: Integration Options

#### Option A: Add to OAuth Settings Page

Modify `src/apps/frontend/src/components/oauth-settings/components/TabNavigation.tsx`:

```typescript
// Add to allTabs array
{ id: 'todos', name: 'Todos', icon: '✅', requiredRole: null },
```

Modify `src/apps/frontend/src/components/oauth-settings/OAuthSettingsPage.tsx`:

```typescript
// Add import
import { TodoTab } from '../../todos/TodoTab';

// Add to renderTabContent function
case 'todos':
  return <TodoTab />;
```

#### Option B: Create New Todos Page (Recommended)

Create `src/apps/frontend/src/pages/dashboard/TodosPage.tsx`:

```typescript
import React from "react";
import { TodoTab } from "../../components/todos/TodoTab";

const TodosPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <TodoTab />
      </div>
    </div>
  );
};

export default TodosPage;
```

Add to `src/apps/frontend/src/pages/dashboard/index.ts`:

```typescript
export { default as TodosPage } from "./TodosPage";
```

### Phase 5: Backend API Integration

#### 5.1 Create API Endpoints

Create backend API endpoints to expose todo tool functionality:

```python
# Example FastAPI endpoint
@router.get("/todos")
async def get_todos(current_user: User = Depends(get_current_user)):
    todo_tool = TodoTool()
    result = await todo_tool.get_todos(user_id=current_user.id)
    return result

@router.post("/todos")
async def create_todo(
    todo_data: TodoCreateRequest,
    current_user: User = Depends(get_current_user)
):
    todo_tool = TodoTool()
    result = await todo_tool.create_todo(
        user_id=current_user.id,
        **todo_data.dict()
    )
    return result
```

## Testing Checklist

- [ ] Todo list loads correctly
- [ ] Add todo functionality works
- [ ] Delete todo functionality works
- [ ] Complete todo functionality works
- [ ] Filtering works correctly
- [ ] Sorting works correctly
- [ ] Error handling works
- [ ] Loading states display correctly
- [ ] Responsive design works
- [ ] User isolation is maintained

## Deployment Notes

1. Ensure backend API endpoints are deployed
2. Update frontend routing if using new page
3. Test user authentication and authorization
4. Verify database connections
5. Test error handling scenarios
