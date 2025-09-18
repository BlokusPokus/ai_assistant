import { create } from 'zustand';
import api from '../services/api';

interface AITask {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  task_type: 'reminder' | 'automated_task' | 'periodic_task';
  schedule_type: 'once' | 'daily' | 'weekly' | 'monthly' | 'custom';
  schedule_config?: any;
  next_run_at?: string;
  last_run_at?: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
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
    task: Omit<AITask, 'id' | 'user_id' | 'created_at' | 'updated_at'>
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
      const response = await api.get('/ai-tasks');
      set({ tasks: response.data.tasks || [], loading: false });
    } catch (error) {
      console.error('Error fetching AI tasks:', error);
      set({
        error:
          error instanceof Error ? error.message : 'Unknown error occurred',
        loading: false,
      });
    }
  },

  createTask: async task => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/ai-tasks', task);
      set(state => ({
        tasks: [response.data.task, ...state.tasks],
        loading: false,
      }));
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Unknown error occurred',
        loading: false,
      });
    }
  },

  updateTask: async (id, updates) => {
    set({ loading: true, error: null });
    try {
      await api.put(`/ai-tasks/${id}`, updates);
      // The backend returns a result object, not the task directly
      // We need to refresh the tasks to get the updated data
      await get().fetchTasks();
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Unknown error occurred',
        loading: false,
      });
    }
  },

  deleteTask: async id => {
    set({ loading: true, error: null });
    try {
      await api.delete(`/ai-tasks/${id}`);
      set(state => ({
        tasks: state.tasks.filter(task => task.id !== id),
        loading: false,
      }));
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Unknown error occurred',
        loading: false,
      });
    }
  },

  executeTask: async id => {
    set({ loading: true, error: null });
    try {
      await api.post(`/ai-tasks/${id}/execute`);
      // Refresh tasks to get updated status
      await get().fetchTasks();
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Unknown error occurred',
        loading: false,
      });
    }
  },

  pauseTask: async id => {
    set({ loading: true, error: null });
    try {
      await api.post(`/ai-tasks/${id}/pause`);
      // The backend returns a status, not the full task
      // We need to refresh the tasks to get the updated data
      await get().fetchTasks();
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : 'Unknown error occurred',
        loading: false,
      });
    }
  },
}));
