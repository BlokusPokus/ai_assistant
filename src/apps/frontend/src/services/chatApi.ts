/**
 * Chat API service for Task 073: Chat Integration with Agent Service.
 *
 * This service provides TypeScript interfaces and functions for communicating
 * with the chat API endpoints.
 */

import api from './api';

// TypeScript interfaces matching the backend Pydantic models
export interface MessageCreate {
  content: string;
  conversation_id?: string;
}

export interface MessageResponse {
  id: number;
  conversation_id: string;
  role: string;
  content: string;
  message_type?: string;
  tool_name?: string;
  tool_success?: string;
  timestamp: string;
  additional_data?: any;
}

export interface ConversationResponse {
  id: number;
  conversation_id: string;
  user_id: number;
  user_input?: string;
  focus_areas?: any;
  step_count: number;
  last_tool_result?: any;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationListResponse {
  conversations: ConversationResponse[];
  total: number;
  page: number;
  per_page: number;
}

export interface SendMessageResponse {
  user_message: MessageResponse;
  ai_message: MessageResponse;
  conversation_id: string;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
}

class ChatApiService {
  /**
   * Send a message to the AI agent
   */
  async sendMessage(messageData: MessageCreate): Promise<SendMessageResponse> {
    try {
      const response = await api.post('/chat/messages', messageData);
      return response.data;
    } catch (error: any) {
      console.error('Error sending message:', error);
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  }

  /**
   * Get user's conversations with pagination
   */
  async getConversations(
    page = 1,
    perPage = 20
  ): Promise<ConversationListResponse> {
    try {
      const response = await api.get('/chat/conversations', {
        params: { page, per_page: perPage },
      });
      return response.data;
    } catch (error: any) {
      console.error('Error getting conversations:', error);
      throw new Error(
        error.response?.data?.detail || 'Failed to get conversations'
      );
    }
  }

  /**
   * Get messages for a specific conversation
   */
  async getConversationMessages(
    conversationId: string,
    limit = 50
  ): Promise<MessageResponse[]> {
    try {
      const response = await api.get(
        `/chat/conversations/${conversationId}/messages`,
        {
          params: { limit },
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error getting conversation messages:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get messages');
    }
  }

  /**
   * Delete a conversation
   */
  async deleteConversation(
    conversationId: string
  ): Promise<{ message: string }> {
    try {
      const response = await api.delete(
        `/chat/conversations/${conversationId}`
      );
      return response.data;
    } catch (error: any) {
      console.error('Error deleting conversation:', error);
      throw new Error(
        error.response?.data?.detail || 'Failed to delete conversation'
      );
    }
  }

  /**
   * Start a new conversation (sends first message)
   */
  async startNewConversation(content: string): Promise<SendMessageResponse> {
    return this.sendMessage({ content });
  }

  /**
   * Continue an existing conversation
   */
  async continueConversation(
    conversationId: string,
    content: string
  ): Promise<SendMessageResponse> {
    return this.sendMessage({ content, conversation_id: conversationId });
  }
}

// Export singleton instance
export const chatApi = new ChatApiService();

// Export the class for testing
export default ChatApiService;
