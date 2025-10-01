import { create } from 'zustand';
import api from '../services/api';

interface Todo {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  priority: 'high' | 'medium' | 'low';
  category?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

interface TodoStore {
  todos: Todo[];
  loading: boolean;
  error: string | null;
  fetchTodos: () => Promise<void>;
  createTodo: (
    todo: Omit<Todo, 'id' | 'created_at' | 'updated_at'>
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
      // Use authenticated API service
      const response = await api.get('/todos/');
      set({ todos: response.data.todos || [], loading: false });
    } catch (error) {
      console.error('Error fetching todos:', error);
      set({
        error:
          error instanceof Error ? error.message : 'Unknown error occurred',
        loading: false,
      });
    }
  },

  createTodo: async todo => {
    set({ loading: true, error: null });
    try {
      const response = await api.post('/todos/', todo);
      set(state => ({
        todos: [response.data.todo, ...state.todos],
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

  updateTodo: async (id, updates) => {
    set({ loading: true, error: null });
    try {
      const response = await api.put(`/todos/${id}`, updates);
      set(state => ({
        todos: state.todos.map(todo =>
          todo.id === id ? response.data.todo : todo
        ),
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

  deleteTodo: async id => {
    set({ loading: true, error: null });
    try {
      await api.delete(`/todos/${id}`);
      set(state => ({
        todos: state.todos.filter(todo => todo.id !== id),
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

  completeTodo: async id => {
    const { updateTodo } = get();
    await updateTodo(id, { status: 'completed' });
  },
}));
