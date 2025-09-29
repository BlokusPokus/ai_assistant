/**
 * AI Task Dashboard - Displays AI-generated tasks for the current conversation.
 * This is completely separate from user todos and shows AI agent task management.
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/Card/Card';
import Badge from '@/components/ui/Badge';
import Progress from '@/components/ui/Progress';
import { Clock, CheckCircle, Circle, XCircle, AlertCircle } from 'lucide-react';

interface AITask {
  id: string;
  content: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  complexity: number;
  conversation_id: string;
  dependencies: string[];
  parent_task_id?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  auto_generated: boolean;
  ai_reasoning?: string;
}

interface AITaskDashboardProps {
  conversationId: string;
  className?: string;
}

const AITaskDashboard: React.FC<AITaskDashboardProps> = ({
  conversationId,
  className = '',
}) => {
  const [tasks, setTasks] = useState<AITask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!conversationId) return;

    const fetchTasks = async () => {
      try {
        setLoading(true);
        // TODO: Replace with actual API call
        // const response = await fetch(`/api/ai-tasks/${conversationId}`);
        // const data = await response.json();

        // Mock data for now
        const mockTasks: AITask[] = [
          {
            id: '1',
            content: 'Analyze user request complexity',
            status: 'completed',
            complexity: 2,
            conversation_id: conversationId,
            dependencies: [],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            completed_at: new Date().toISOString(),
            auto_generated: true,
            ai_reasoning: 'Need to understand the scope of the user request',
          },
          {
            id: '2',
            content: 'Create implementation plan',
            status: 'in_progress',
            complexity: 3,
            conversation_id: conversationId,
            dependencies: ['1'],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            auto_generated: true,
            ai_reasoning: 'Based on analysis, create structured plan',
          },
          {
            id: '3',
            content: 'Implement core functionality',
            status: 'pending',
            complexity: 4,
            conversation_id: conversationId,
            dependencies: ['2'],
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            auto_generated: true,
            ai_reasoning: 'Execute the planned implementation',
          },
        ];

        setTasks(mockTasks);
        setError(null);
      } catch (err) {
        setError('Failed to load AI tasks');
        console.error('Error fetching AI tasks:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [conversationId]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Circle className="h-4 w-4 text-gray-400" />;
      case 'in_progress':
        return <Clock className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getComplexityColor = (complexity: number) => {
    switch (complexity) {
      case 1:
        return 'bg-green-100 text-green-800';
      case 2:
        return 'bg-yellow-100 text-yellow-800';
      case 3:
        return 'bg-orange-100 text-orange-800';
      case 4:
        return 'bg-red-100 text-red-800';
      case 5:
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getComplexityLabel = (complexity: number) => {
    switch (complexity) {
      case 1:
        return 'Simple';
      case 2:
        return 'Moderate';
      case 3:
        return 'Complex';
      case 4:
        return 'Advanced';
      case 5:
        return 'Expert';
      default:
        return 'Unknown';
    }
  };

  const completedTasks = tasks.filter(
    task => task.status === 'completed'
  ).length;
  const totalTasks = tasks.length;
  const progressPercentage =
    totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

  const pendingTasks = tasks.filter(task => task.status === 'pending');
  const inProgressTasks = tasks.filter(task => task.status === 'in_progress');
  const completedTasksList = tasks.filter(task => task.status === 'completed');

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="h-5 w-5 bg-blue-500 rounded animate-pulse" />
            AI Task Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded animate-pulse" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            AI Task Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600">{error}</p>
        </CardContent>
      </Card>
    );
  }

  if (tasks.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="h-5 w-5 bg-blue-500 rounded" />
            AI Task Progress
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-500 text-center py-4">
            No AI tasks for this conversation yet.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="h-5 w-5 bg-blue-500 rounded" />
          AI Task Progress
        </CardTitle>
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Overall Progress</span>
            <span>
              {completedTasks}/{totalTasks} tasks
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* In Progress Tasks */}
        {inProgressTasks.length > 0 && (
          <div>
            <h4 className="font-medium text-blue-600 mb-2 flex items-center gap-2">
              <Clock className="h-4 w-4" />
              In Progress ({inProgressTasks.length})
            </h4>
            <div className="space-y-2">
              {inProgressTasks.map(task => (
                <div
                  key={task.id}
                  className="p-3 bg-blue-50 rounded-lg border border-blue-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(task.status)}
                      <span className="font-medium">{task.content}</span>
                    </div>
                    <Badge className={getComplexityColor(task.complexity)}>
                      {getComplexityLabel(task.complexity)}
                    </Badge>
                  </div>
                  {task.ai_reasoning && (
                    <p className="text-sm text-gray-600 mt-1 italic">
                      "{task.ai_reasoning}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pending Tasks */}
        {pendingTasks.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-600 mb-2 flex items-center gap-2">
              <Circle className="h-4 w-4" />
              Pending ({pendingTasks.length})
            </h4>
            <div className="space-y-2">
              {pendingTasks.map(task => (
                <div
                  key={task.id}
                  className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(task.status)}
                      <span className="font-medium">{task.content}</span>
                    </div>
                    <Badge className={getComplexityColor(task.complexity)}>
                      {getComplexityLabel(task.complexity)}
                    </Badge>
                  </div>
                  {task.dependencies.length > 0 && (
                    <p className="text-sm text-gray-500 mt-1">
                      Depends on {task.dependencies.length} task(s)
                    </p>
                  )}
                  {task.ai_reasoning && (
                    <p className="text-sm text-gray-600 mt-1 italic">
                      "{task.ai_reasoning}"
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Completed Tasks */}
        {completedTasksList.length > 0 && (
          <div>
            <h4 className="font-medium text-green-600 mb-2 flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              Completed ({completedTasksList.length})
            </h4>
            <div className="space-y-2">
              {completedTasksList.map(task => (
                <div
                  key={task.id}
                  className="p-3 bg-green-50 rounded-lg border border-green-200"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(task.status)}
                      <span className="font-medium line-through text-gray-600">
                        {task.content}
                      </span>
                    </div>
                    <Badge className={getComplexityColor(task.complexity)}>
                      {getComplexityLabel(task.complexity)}
                    </Badge>
                  </div>
                  {task.completed_at && (
                    <p className="text-sm text-gray-500 mt-1">
                      Completed at{' '}
                      {new Date(task.completed_at).toLocaleTimeString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default AITaskDashboard;
