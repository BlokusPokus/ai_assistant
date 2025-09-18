import React, { useEffect, useState } from 'react';
import { useAITaskStore } from '../../stores/aiTaskStore';
import { AITaskForm } from './AITaskForm';
import { AITaskList } from './AITaskList';

export const AITaskTab: React.FC = () => {
  const { fetchTasks } = useAITaskStore();
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return (
    <div className="px-4 sm:px-0">
      {/* Page Header */}
      <div className="mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-900">AI Tasks</h2>
          <p className="mt-1 text-sm text-gray-600">
            Manage your AI-driven tasks, reminders, and automated workflows.
          </p>
        </div>
      </div>

      {/* Add Task Form - Only show when toggled */}
      {showAddForm && (
        <div className="mb-4">
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
