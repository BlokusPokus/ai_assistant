import React, { useState } from 'react';
import { useAITaskStore } from '../../stores/aiTaskStore';
import { AITaskItem } from './AITaskItem';
import { Card } from '@/components/ui';
import { Plus } from 'lucide-react';

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
    'all' | 'active' | 'paused' | 'completed' | 'failed'
  >('all');
  const [taskTypeFilter, setTaskTypeFilter] = useState<
    'all' | 'reminder' | 'automated_task' | 'periodic_task'
  >('all');

  const filteredTasks = tasks.filter(task => {
    const matchesStatus = filter === 'all' || task.status === filter;
    const matchesType =
      taskTypeFilter === 'all' || task.task_type === taskTypeFilter;
    return matchesStatus && matchesType;
  });

  const filterOptions = [
    { value: 'all', label: 'All Tasks', count: tasks.length },
    {
      value: 'active',
      label: 'Active',
      count: tasks.filter(task => task.status === 'active').length,
    },
    {
      value: 'paused',
      label: 'Paused',
      count: tasks.filter(task => task.status === 'paused').length,
    },
    {
      value: 'completed',
      label: 'Completed',
      count: tasks.filter(task => task.status === 'completed').length,
    },
    {
      value: 'failed',
      label: 'Failed',
      count: tasks.filter(task => task.status === 'failed').length,
    },
  ];

  const taskTypeOptions = [
    { value: 'all', label: 'All Types', count: tasks.length },
    {
      value: 'reminder',
      label: 'Reminders',
      count: tasks.filter(task => task.task_type === 'reminder').length,
    },
    {
      value: 'automated_task',
      label: 'Automated',
      count: tasks.filter(task => task.task_type === 'automated_task').length,
    },
    {
      value: 'periodic_task',
      label: 'Periodic',
      count: tasks.filter(task => task.task_type === 'periodic_task').length,
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
    <div className="space-y-4">
      {/* Filters */}
      <Card>
        <div className="flex flex-col lg:flex-row lg:items-center space-y-3 lg:space-y-0 lg:space-x-3">
          {/* Status Filter */}
          <div className="flex flex-wrap gap-2">
            {filterOptions.map(option => (
              <button
                key={option.value}
                onClick={() => setFilter(option.value as any)}
                className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
                  filter === option.value
                    ? 'bg-blue-100 text-blue-700 border border-blue-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {option.label} ({option.count})
              </button>
            ))}
          </div>

          {/* Task Type Filter */}
          <div className="flex flex-wrap gap-2">
            {taskTypeOptions.map(option => (
              <button
                key={option.value}
                onClick={() => setTaskTypeFilter(option.value as any)}
                className={`px-2 py-1 text-xs font-medium rounded transition-colors ${
                  taskTypeFilter === option.value
                    ? 'bg-green-100 text-green-700 border border-green-200'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {option.label} ({option.count})
              </button>
            ))}
          </div>

          {/* Count and Add Button */}
          <div className="flex items-center justify-between lg:ml-auto lg:space-x-3">
            <div className="text-xs text-gray-500">
              {filteredTasks.length} task(s) found
            </div>

            <button
              onClick={onToggleAddForm}
              className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-lg border border-white/30 bg-white/25 backdrop-blur-xl shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden text-gray-800 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
            >
              <Plus className="w-3 h-3 mr-1.5" />
              {showAddForm ? 'Cancel' : 'Add AI Task'}
            </button>
          </div>
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
            {filter === 'all' && taskTypeFilter === 'all'
              ? 'Get started by creating your first AI task.'
              : `No ${filter === 'all' ? taskTypeFilter : filter} tasks found.`}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTasks.map(task => (
            <AITaskItem key={task.id} task={task} />
          ))}
        </div>
      )}
    </div>
  );
};
