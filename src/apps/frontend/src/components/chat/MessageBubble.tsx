import React from 'react';
import type { MessageResponse } from '@/services/chatApi';
import { formatMessageContent } from '@/utils/messageUtils';

interface MessageBubbleProps {
  message: MessageResponse;
  formatTimestamp: (timestamp: string) => string;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  formatTimestamp,
}) => {
  const isUser = message.role === 'user';
  const formattedContent = formatMessageContent(message.content);

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
          isUser ? 'bg-accent text-white' : 'bg-gray-100 text-gray-900'
        }`}
      >
        <div className="text-sm whitespace-pre-wrap leading-relaxed break-words">
          {formattedContent}
        </div>
        <div className={`text-xs mt-2 ${isUser ? 'opacity-80' : 'opacity-70'}`}>
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
