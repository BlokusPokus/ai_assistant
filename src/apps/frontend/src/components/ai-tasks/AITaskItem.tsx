import React from 'react';
import { useAITaskStore } from '../../stores/aiTaskStore';
import { Card } from '@/components/ui';
import {
  Play,
  Pause,
  Trash2,
  Clock,
  Calendar,
  Brain,
  Bell,
} from 'lucide-react';

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
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTaskTypeIcon = (taskType: string) => {
    switch (taskType) {
      case 'reminder':
        return <Bell className="w-4 h-4" />;
      case 'automated_task':
        return <Brain className="w-4 h-4" />;
      case 'periodic_task':
        return <Clock className="w-4 h-4" />;
      default:
        return <Brain className="w-4 h-4" />;
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <div className="p-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              {getTaskTypeIcon(task.task_type)}
              <h3 className="font-semibold text-gray-900 truncate">
                {task.title}
              </h3>
              <span
                className={`px-1.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                  task.status
                )}`}
              >
                {task.status}
              </span>
            </div>

            {task.description && (
              <p className="text-gray-600 text-xs mb-1 line-clamp-2">
                {task.description}
              </p>
            )}

            <div className="flex items-center space-x-3 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <Calendar className="w-3 h-3" />
                <span>{task.schedule_type}</span>
              </div>

              {task.next_run_at && (
                <div className="flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{new Date(task.next_run_at).toLocaleDateString()}</span>
                </div>
              )}

              {task.notification_channels.length > 0 && (
                <div className="flex items-center space-x-1">
                  <Bell className="w-3 h-3" />
                  <span>{task.notification_channels.join(', ')}</span>
                </div>
              )}
            </div>
          </div>

          <div className="flex space-x-1 ml-2">
            {task.status === 'active' ? (
              <button
                onClick={() => pauseTask(task.id)}
                className="p-1.5 hover:bg-yellow-100 rounded text-yellow-600 hover:text-yellow-700"
                title="Pause task"
              >
                <Pause className="w-3 h-3" />
              </button>
            ) : (
              <button
                onClick={() => pauseTask(task.id)}
                className="p-1.5 hover:bg-green-100 rounded text-green-600 hover:text-green-700"
                title="Resume task"
              >
                <Play className="w-3 h-3" />
              </button>
            )}

            <button
              onClick={() => executeTask(task.id)}
              className="p-1.5 hover:bg-blue-100 rounded text-blue-600 hover:text-blue-700"
              title="Execute task"
            >
              <Play className="w-3 h-3" />
            </button>

            <button
              onClick={() => deleteTask(task.id)}
              className="p-1.5 hover:bg-red-100 rounded text-red-600 hover:text-red-700"
              title="Delete task"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </Card>
  );
};
