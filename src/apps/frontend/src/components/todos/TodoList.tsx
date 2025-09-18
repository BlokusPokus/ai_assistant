import React, { useState } from 'react';
import { useTodoStore } from '../../stores/todoStore';
import { TodoItem } from './TodoItem';
import { Card } from '@/components/ui';
import { Plus } from 'lucide-react';

interface TodoListProps {
  showAddForm: boolean;
  onToggleAddForm: () => void;
}

export const TodoList: React.FC<TodoListProps> = ({
  showAddForm,
  onToggleAddForm,
}) => {
  const { todos, loading, error } = useTodoStore();
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [sortBy, setSortBy] = useState<'created_at' | 'due_date' | 'priority'>(
    'created_at'
  );

  const filteredTodos = todos.filter(todo => {
    if (filter === 'all') return true;
    return todo.status === filter;
  });

  const filterOptions = [
    { value: 'all', label: 'All Todos', count: todos.length },
    {
      value: 'pending',
      label: 'Pending',
      count: todos.filter(todo => todo.status === 'pending').length,
    },
    {
      value: 'completed',
      label: 'Completed',
      count: todos.filter(todo => todo.status === 'completed').length,
    },
  ];

  const sortedTodos = [...filteredTodos].sort((a, b) => {
    switch (sortBy) {
      case 'due_date':
        if (!a.due_date && !b.due_date) return 0;
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      case 'priority':
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
      <Card>
        <div className="flex flex-col md:flex-row md:items-center space-y-4 md:space-y-0 md:space-x-4">
          {/* Filter Buttons */}
          <div className="flex space-x-2">
            {filterOptions.map(option => (
              <button
                key={option.value}
                onClick={() =>
                  setFilter(option.value as 'all' | 'pending' | 'completed')
                }
                className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  filter === option.value
                    ? 'bg-blue-100 text-blue-700 border border-blue-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {option.label} ({option.count})
              </button>
            ))}
          </div>

          {/* Sort By and Add Todo Button */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">
                Sort by:
              </label>
              <select
                value={sortBy}
                onChange={e =>
                  setSortBy(
                    e.target.value as 'created_at' | 'due_date' | 'priority'
                  )
                }
                className="h-10 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 hover:border-gray-400 appearance-none w-36"
              >
                <option value="created_at" className="py-2">
                  Created Date
                </option>
                <option value="due_date" className="py-2">
                  Due Date
                </option>
                <option value="priority" className="py-2">
                  Priority
                </option>
              </select>
            </div>
          </div>

          {/* Count */}
          <div className="text-sm text-gray-500 ml-auto">
            {sortedTodos.length} todo(s) found
          </div>
          <button
            onClick={onToggleAddForm}
            className="inline-flex items-center px-4 py-2 text-sm font-medium rounded-2xl border border-white/30 bg-white/25 backdrop-blur-xl shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden text-gray-800 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
          >
            <Plus className="w-4 h-4 mr-2" />
            {showAddForm ? 'Cancel' : 'Add Todo'}
          </button>
        </div>
      </Card>

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
            {filter === 'all'
              ? 'Get started by creating your first todo.'
              : `No ${filter} todos found.`}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedTodos.map(todo => (
            <TodoItem key={todo.id} todo={todo} />
          ))}
        </div>
      )}
    </div>
  );
};
