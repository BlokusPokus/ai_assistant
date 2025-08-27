import React from 'react';
import { Card } from '@/components/ui';
import { MessageSquare, Send, Bot, User } from 'lucide-react';
import { Input } from '@/components/ui';

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
    {
      id: 4,
      content:
        'I have a big project deadline on Friday, and I need to prepare for a meeting on Wednesday',
      isUser: true,
      timestamp: '10:32 AM',
    },
    {
      id: 5,
      content:
        "Perfect! Let me break this down for you. I'll create a structured plan with your project deadline and meeting preparation. Would you like me to set up reminders for these tasks?",
      isUser: false,
      timestamp: '10:32 AM',
    },
    {
      id: 6,
      content:
        'Yes, that would be great! Can you also help me prioritize my daily tasks?',
      isUser: true,
      timestamp: '10:33 AM',
    },
    {
      id: 7,
      content:
        "Absolutely! I'll analyze your current workload and create a daily priority system. This will help you focus on what's most important each day. Should I also set up time blocks for deep work sessions?",
      isUser: false,
      timestamp: '10:33 AM',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-primary">AI Chat Assistant</h1>
        <p className="text-gray-600">
          Chat with your personal AI assistant to get help with tasks,
          organization, and more.
        </p>
      </div>

      {/* Chat Interface */}
      <Card className="min-h-[600px] flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center space-x-3 pb-4 border-b border-gray-200 mb-4 px-4 flex-shrink-0">
          <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center">
            <img src="/orca3d.png" alt="AI Assistant" className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-medium text-primary">AI Assistant</h3>
            <p className="text-sm text-gray-500">Online • Ready to help</p>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 space-y-4 px-4 pb-4 min-h-0">
          {mockMessages.map(message => (
            <div
              key={message.id}
              className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.isUser
                    ? 'bg-accent text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p
                  className={`text-xs mt-1 ${
                    message.isUser ? 'text-accent-light' : 'text-gray-500'
                  }`}
                >
                  {message.timestamp}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Chat Input */}
        <div className="border-t border-gray-200 pt-4 px-4 pb-4 flex-shrink-0 bg-white">
          <div className="flex space-x-3">
            <Input
              type="text"
              placeholder="Type your message..."
              className="flex-1 min-w-0"
            />
            <button className="px-6 py-3 bg-accent text-white rounded-2xl hover:bg-accent-light focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 transition-colors duration-200 flex-shrink-0">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </Card>

      {/* Coming Soon Features */}
      <Card className="bg-gradient-to-r from-accent/5 to-purple-50 border-accent/20">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-primary mb-2">
            🚀 Advanced Chat Features Coming Soon!
          </h3>
          <p className="text-gray-600 mb-4">
            We're working on bringing you advanced chat capabilities including:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-accent" />
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
