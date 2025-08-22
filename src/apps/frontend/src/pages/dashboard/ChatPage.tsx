import React from 'react';
import { Card } from '@/components/ui';
import { MessageSquare, Send, Bot, User } from 'lucide-react';

const ChatPage: React.FC = () => {
  const mockMessages = [
    {
      id: 1,
      content: "Hello! I'm your AI assistant. How can I help you today?",
      isUser: false,
      timestamp: '10:30 AM',
    },
    {
      id: 2,
      content: 'I need help organizing my tasks for the week',
      isUser: true,
      timestamp: '10:31 AM',
    },
    {
      id: 3,
      content:
        "I'd be happy to help! Let me create a task list for you. What are your main priorities this week?",
      isUser: false,
      timestamp: '10:31 AM',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">AI Chat Assistant</h1>
        <p className="text-gray-600">
          Chat with your personal AI assistant to get help with tasks,
          organization, and more.
        </p>
      </div>

      {/* Chat Interface */}
      <Card padding="lg" className="h-96 flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center space-x-3 pb-4 border-b border-gray-200 mb-4">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-medium text-gray-900">AI Assistant</h3>
            <p className="text-sm text-gray-500">Online • Ready to help</p>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-4">
          {mockMessages.map(message => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.isUser
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p
                  className={`text-xs mt-1 ${
                    message.isUser ? 'text-blue-100' : 'text-gray-500'
                  }`}
                >
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-200 pt-4">
          <div className="flex space-x-3">
            <input
              type="text"
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Card>

      {/* Coming Soon Features */}
      <Card
        padding="lg"
        className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200"
      >
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            🚀 Advanced Chat Features Coming Soon!
          </h3>
          <p className="text-gray-600 mb-4">
            We're working on bringing you advanced chat capabilities including:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-blue-600" />
              <span>Voice messages</span>
            </div>
            <div className="flex items-center space-x-2">
              <Bot className="w-4 h-4 text-green-600" />
              <span>AI memory</span>
            </div>
            <div className="flex items-center space-x-2">
              <User className="w-4 h-4 text-purple-600" />
              <span>File sharing</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default ChatPage;
