import React from 'react';
import { useTodoStore } from '../../stores/todoStore';

interface TodoItemProps {
  todo: {
    id: number;
    title: string;
    description?: string;
    due_date?: string;
    priority: 'high' | 'medium' | 'low';
    category?: string;
    status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
    created_at: string;
    updated_at: string;
  };
}

export const TodoItem: React.FC<TodoItemProps> = ({ todo }) => {
  const { deleteTodo, completeTodo } = useTodoStore();

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const handleComplete = () => {
    completeTodo(todo.id);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this todo?')) {
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
                todo.status === 'completed'
                  ? 'line-through text-gray-500'
                  : 'text-gray-900'
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
          {todo.status !== 'completed' && (
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
