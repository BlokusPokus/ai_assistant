import React, { useState } from 'react';
import { useAITaskStore } from '../../stores/aiTaskStore';
import { Card } from '@/components/ui';

interface AITaskFormProps {
  onSuccess: () => void;
}

interface FormData {
  title: string;
  description: string;
  task_type: 'reminder' | 'automated_task' | 'periodic_task';
  schedule_type: 'once' | 'daily' | 'weekly' | 'monthly' | 'custom';
  ai_context: string;
  notification_channels: string[];
  status: 'active' | 'paused' | 'completed' | 'failed';
}

export const AITaskForm: React.FC<AITaskFormProps> = ({ onSuccess }) => {
  const { createTask } = useAITaskStore();
  const [formData, setFormData] = useState<FormData>({
    title: '',
    description: '',
    task_type: 'reminder',
    schedule_type: 'once',
    ai_context: '',
    notification_channels: [],
    status: 'active',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTask(formData);
      onSuccess();
    } catch (error) {
      console.error('Error creating AI task:', error);
    }
  };

  const handleNotificationChange = (channel: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      notification_channels: checked
        ? [...prev.notification_channels, channel]
        : prev.notification_channels.filter(c => c !== channel),
    }));
  };

  return (
    <Card>
      <div className="p-4">
        <h3 className="text-base font-medium text-gray-900 mb-3">
          Create AI Task
        </h3>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={e =>
                setFormData(prev => ({ ...prev, title: e.target.value }))
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
              onChange={e =>
                setFormData(prev => ({
                  ...prev,
                  description: e.target.value,
                }))
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Task Type
              </label>
              <select
                value={formData.task_type}
                onChange={e =>
                  setFormData(prev => ({
                    ...prev,
                    task_type: e.target.value as FormData['task_type'],
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
                onChange={e =>
                  setFormData(prev => ({
                    ...prev,
                    schedule_type: e.target.value as FormData['schedule_type'],
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
              onChange={e =>
                setFormData(prev => ({ ...prev, ai_context: e.target.value }))
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
              {['sms', 'email', 'in_app'].map(channel => (
                <label key={channel} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.notification_channels.includes(channel)}
                    onChange={e =>
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

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={onSuccess}
              className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Create Task
            </button>
          </div>
        </form>
      </div>
    </Card>
  );
};
