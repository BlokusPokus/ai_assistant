import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, Bot, Plus, Trash2, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui';
import { chatApi } from '@/services';
import type { MessageResponse, ConversationResponse } from '@/services/chatApi';
import {
  filterVisibleMessages,
  removeDuplicateMessages,
} from '@/utils/messageUtils';
import MessageBubble from '@/components/chat/MessageBubble';

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [conversations, setConversations] = useState<ConversationResponse[]>(
    []
  );
  const [currentConversationId, setCurrentConversationId] = useState<
    string | null
  >(null);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [lastMessageCount, setLastMessageCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Load conversations on component mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load messages when conversation changes
  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId);
    } else {
      setMessages([]);
    }
  }, [currentConversationId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    // Use setTimeout to ensure DOM is updated before scrolling
    const timer = setTimeout(() => {
      scrollToBottom();
    }, 100);
    return () => clearTimeout(timer);
  }, [messages]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({
        behavior: 'smooth',
        block: 'end',
        inline: 'nearest',
      });
    }
  };

  const loadConversations = async () => {
    try {
      setIsLoadingConversations(true);
      setError(null);
      const response = await chatApi.getConversations();
      setConversations(response.conversations);
    } catch (error: any) {
      console.error('Error loading conversations:', error);
      setError('Failed to load conversations');
    } finally {
      setIsLoadingConversations(false);
    }
  };

  const loadMessages = async (conversationId: string) => {
    try {
      setError(null);
      const messages = await chatApi.getConversationMessages(conversationId);
      // Filter visible messages and remove duplicates
      const filteredMessages = removeDuplicateMessages(
        filterVisibleMessages(messages)
      );
      // Backend now returns messages in chronological order (by ID)
      setMessages(filteredMessages);
      setLastMessageCount(filteredMessages.length);
    } catch (error: any) {
      console.error('Error loading messages:', error);
      setError('Failed to load messages');
    }
  };

  const checkForNewMessages = async () => {
    if (!currentConversationId || isPolling) return;

    try {
      const messages = await chatApi.getConversationMessages(
        currentConversationId
      );
      const filteredMessages = removeDuplicateMessages(
        filterVisibleMessages(messages)
      );

      // Check if we have new messages
      if (filteredMessages.length > lastMessageCount) {
        setMessages(filteredMessages);
        setLastMessageCount(filteredMessages.length);

        // Stop polling if we have a real AI response (not placeholder)
        const lastMessage = filteredMessages[filteredMessages.length - 1];
        if (
          lastMessage.role === 'assistant' &&
          lastMessage.content !== 'Processing your request...' &&
          lastMessage.id !== 0
        ) {
          stopPolling();
        }
      }
    } catch (error: any) {
      console.error('Error checking for new messages:', error);
      // Don't show error to user for polling failures
    }
  };

  const startPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
    }

    setIsPolling(true);
    pollingIntervalRef.current = setInterval(checkForNewMessages, 2000); // Poll every 2 seconds
  };

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
    setIsPolling(false);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const messageContent = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    // Add user message to UI immediately for better UX
    const tempUserMessage: MessageResponse = {
      id: Date.now(), // Temporary ID
      conversation_id: currentConversationId || 'temp',
      role: 'user',
      content: messageContent,
      message_type: 'user_input',
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, tempUserMessage]);

    try {
      let response;
      if (currentConversationId) {
        response = await chatApi.continueConversation(
          currentConversationId,
          messageContent
        );
      } else {
        response = await chatApi.startNewConversation(messageContent);
        setCurrentConversationId(response.conversation_id);
      }

      // Reload messages from backend to ensure correct ordering and get real message IDs
      await loadMessages(response.conversation_id);

      // Start polling for real AI response if we got a placeholder
      if (
        response.ai_message.content === 'Processing your request...' &&
        response.ai_message.id === 0
      ) {
        startPolling();
      }

      // Reload conversations to include the new one
      if (!currentConversationId) {
        loadConversations();
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      setError('Failed to send message');
      // Remove the temporary user message on error
      setMessages(prev => prev.filter(msg => msg.id !== tempUserMessage.id));
      // Restore input message on error
      setInputMessage(messageContent);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startNewConversation = () => {
    stopPolling(); // Stop any ongoing polling
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
    setLastMessageCount(0);
  };

  const deleteConversation = async (conversationId: string) => {
    try {
      await chatApi.deleteConversation(conversationId);
      if (currentConversationId === conversationId) {
        startNewConversation();
      }
      loadConversations();
    } catch (error: any) {
      console.error('Error deleting conversation:', error);
      setError('Failed to delete conversation');
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getConversationTitle = (conversation: ConversationResponse) => {
    if (conversation.user_input) {
      return conversation.user_input.length > 50
        ? conversation.user_input.substring(0, 50) + '...'
        : conversation.user_input;
    }
    return 'New Conversation';
  };

  return (
    <div className="flex h-[calc(100vh-90px)] space-x-4 -m-6 p-6">
      {/* Conversation Sidebar */}
      <div className="w-1/4 border-r border-gray-200 bg-gray-50 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={startNewConversation}
            className="w-full bg-accent text-white px-4 py-2 rounded-lg hover:bg-accent-light transition-colors flex items-center justify-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>New Conversation</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="px-4 py-2">
            <h3 className="font-semibold text-gray-700 mb-3">Conversations</h3>
            {isLoadingConversations ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="ml-2 text-sm text-gray-500">Loading...</span>
              </div>
            ) : (
              <div className="space-y-2">
                {conversations.map(conv => (
                  <div
                    key={conv.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors group ${
                      currentConversationId === conv.conversation_id
                        ? 'bg-accent/10 border border-accent/20'
                        : 'hover:bg-gray-100'
                    }`}
                    onClick={() =>
                      setCurrentConversationId(conv.conversation_id)
                    }
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-sm text-gray-900 truncate">
                          {getConversationTitle(conv)}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {conv.message_count} messages •{' '}
                          {formatTimestamp(conv.updated_at)}
                        </div>
                      </div>
                      <button
                        onClick={e => {
                          e.stopPropagation();
                          deleteConversation(conv.conversation_id);
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 rounded transition-all"
                        title="Delete conversation"
                      >
                        <Trash2 className="w-3 h-3 text-red-500" />
                      </button>
                    </div>
                  </div>
                ))}
                {conversations.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No conversations yet</p>
                    <p className="text-xs">
                      Start a new conversation to begin!
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="flex items-center space-x-3 pb-4 border-b border-gray-200 mb-4 px-4 flex-shrink-0">
          <div className="w-10 h-10 bg-accent/10 rounded-full flex items-center justify-center">
            <Bot className="w-5 h-5 text-accent" />
          </div>
          <div>
            <h3 className="font-medium text-primary">AI Assistant</h3>
            <p className="text-sm text-gray-500">
              {currentConversationId ? 'Active conversation' : 'Ready to help'}
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mx-4 mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-2 py-4">
          {messages.length === 0 && !isLoading && (
            <div className="text-center py-12">
              <Bot className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Start a conversation
              </h3>
              <p className="text-gray-500">
                Ask me anything! I can help with tasks, organization, and more.
              </p>
            </div>
          )}

          {messages.map(message => (
            <MessageBubble
              key={message.id}
              message={message}
              formatTimestamp={formatTimestamp}
            />
          ))}

          {isLoading && (
            <div className="flex justify-start mb-3">
              <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-2xl">
                <div className="flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 px-1 py-4 flex-shrink-0 bg-white">
          <div className="flex space-x-2">
            <Input
              type="text"
              value={inputMessage}
              onChange={e => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="flex-1 min-w-0 w-full"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="px-6 py-3 bg-accent text-white rounded-2xl hover:bg-accent-light focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 transition-colors duration-200 flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
