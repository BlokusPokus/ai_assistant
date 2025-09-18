import React, { useEffect, useState } from 'react';
import { useTodoStore } from '../../stores/todoStore';
import { TodoForm } from './TodoForm';
import { TodoList } from './TodoList';
import { Plus } from 'lucide-react';

export const TodoTab: React.FC = () => {
  const { fetchTodos } = useTodoStore();
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  return (
    <div className="px-4 sm:px-0">
      {/* Page Header */}
      <div className="mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">My Todos</h2>
          <p className="mt-2 text-sm text-gray-600">
            Manage your tasks and stay organized with your personal todo list.
          </p>
        </div>
      </div>

      {/* Add Todo Form - Only show when toggled */}
      {showAddForm && (
        <div className="mb-6">
          <TodoForm onSuccess={() => setShowAddForm(false)} />
        </div>
      )}

      {/* Todo List - Main View */}
      <TodoList
        showAddForm={showAddForm}
        onToggleAddForm={() => setShowAddForm(!showAddForm)}
      />
    </div>
  );
};
