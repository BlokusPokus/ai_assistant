import React from 'react';
import { TodoTab } from '../../components/todos/TodoTab';

const TodosPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <TodoTab />
      </div>
    </div>
  );
};

export default TodosPage;
