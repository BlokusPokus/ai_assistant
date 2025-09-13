/**
 * Frontend tests for Task 073: Chat Integration with Agent Service.
 *
 * This module tests the chat API service functions.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import axios from "axios";
import {
  chatApi,
  ChatApiService,
} from "../../src/apps/frontend/src/services/chatApi";

// Mock axios
vi.mock("axios");
const mockedAxios = vi.mocked(axios);

// Mock the api module
vi.mock("../../src/apps/frontend/src/services/api", () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    delete: vi.fn(),
  },
}));

describe("ChatApiService", () => {
  let chatService: ChatApiService;

  beforeEach(() => {
    chatService = new ChatApiService();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("sendMessage", () => {
    it("should send a message successfully", async () => {
      const mockResponse = {
        data: {
          user_message: {
            id: 1,
            conversation_id: "conv-123",
            role: "user",
            content: "Hello",
            message_type: "user_input",
            timestamp: "2024-01-01T10:00:00Z",
          },
          ai_message: {
            id: 2,
            conversation_id: "conv-123",
            role: "assistant",
            content: "Hi there!",
            message_type: "assistant_response",
            timestamp: "2024-01-01T10:00:01Z",
          },
          conversation_id: "conv-123",
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const result = await chatService.sendMessage({
        content: "Hello",
        conversation_id: "conv-123",
      });

      expect(api.post).toHaveBeenCalledWith("/chat/messages", {
        content: "Hello",
        conversation_id: "conv-123",
      });
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle send message errors", async () => {
      const mockError = {
        response: {
          data: {
            detail: "Failed to send message",
          },
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.post).mockRejectedValue(mockError);

      await expect(
        chatService.sendMessage({ content: "Hello" })
      ).rejects.toThrow("Failed to send message");
    });

    it("should handle network errors", async () => {
      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.post).mockRejectedValue(new Error("Network error"));

      await expect(
        chatService.sendMessage({ content: "Hello" })
      ).rejects.toThrow("Failed to send message");
    });
  });

  describe("getConversations", () => {
    it("should get conversations successfully", async () => {
      const mockResponse = {
        data: {
          conversations: [
            {
              id: 1,
              conversation_id: "conv-123",
              user_id: 1,
              user_input: "Hello",
              step_count: 1,
              created_at: "2024-01-01T10:00:00Z",
              updated_at: "2024-01-01T10:00:00Z",
              message_count: 2,
            },
          ],
          total: 1,
          page: 1,
          per_page: 20,
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      const result = await chatService.getConversations(1, 20);

      expect(api.get).toHaveBeenCalledWith("/chat/conversations", {
        params: { page: 1, per_page: 20 },
      });
      expect(result).toEqual(mockResponse.data);
    });

    it("should use default pagination parameters", async () => {
      const mockResponse = {
        data: {
          conversations: [],
          total: 0,
          page: 1,
          per_page: 20,
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      await chatService.getConversations();

      expect(api.get).toHaveBeenCalledWith("/chat/conversations", {
        params: { page: 1, per_page: 20 },
      });
    });

    it("should handle get conversations errors", async () => {
      const mockError = {
        response: {
          data: {
            detail: "Failed to get conversations",
          },
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.get).mockRejectedValue(mockError);

      await expect(chatService.getConversations()).rejects.toThrow(
        "Failed to get conversations"
      );
    });
  });

  describe("getConversationMessages", () => {
    it("should get conversation messages successfully", async () => {
      const mockResponse = {
        data: [
          {
            id: 1,
            conversation_id: "conv-123",
            role: "user",
            content: "Hello",
            message_type: "user_input",
            timestamp: "2024-01-01T10:00:00Z",
          },
          {
            id: 2,
            conversation_id: "conv-123",
            role: "assistant",
            content: "Hi there!",
            message_type: "assistant_response",
            timestamp: "2024-01-01T10:00:01Z",
          },
        ],
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      const result = await chatService.getConversationMessages("conv-123", 50);

      expect(api.get).toHaveBeenCalledWith(
        "/chat/conversations/conv-123/messages",
        {
          params: { limit: 50 },
        }
      );
      expect(result).toEqual(mockResponse.data);
    });

    it("should use default limit parameter", async () => {
      const mockResponse = { data: [] };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.get).mockResolvedValue(mockResponse);

      await chatService.getConversationMessages("conv-123");

      expect(api.get).toHaveBeenCalledWith(
        "/chat/conversations/conv-123/messages",
        {
          params: { limit: 50 },
        }
      );
    });

    it("should handle get messages errors", async () => {
      const mockError = {
        response: {
          data: {
            detail: "Failed to get messages",
          },
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.get).mockRejectedValue(mockError);

      await expect(
        chatService.getConversationMessages("conv-123")
      ).rejects.toThrow("Failed to get messages");
    });
  });

  describe("deleteConversation", () => {
    it("should delete conversation successfully", async () => {
      const mockResponse = {
        data: {
          message: "Conversation deleted successfully",
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.delete).mockResolvedValue(mockResponse);

      const result = await chatService.deleteConversation("conv-123");

      expect(api.delete).toHaveBeenCalledWith("/chat/conversations/conv-123");
      expect(result).toEqual(mockResponse.data);
    });

    it("should handle delete conversation errors", async () => {
      const mockError = {
        response: {
          data: {
            detail: "Failed to delete conversation",
          },
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.delete).mockRejectedValue(mockError);

      await expect(chatService.deleteConversation("conv-123")).rejects.toThrow(
        "Failed to delete conversation"
      );
    });
  });

  describe("startNewConversation", () => {
    it("should start a new conversation", async () => {
      const mockResponse = {
        data: {
          user_message: {
            id: 1,
            conversation_id: "conv-123",
            role: "user",
            content: "Hello",
            message_type: "user_input",
            timestamp: "2024-01-01T10:00:00Z",
          },
          ai_message: {
            id: 2,
            conversation_id: "conv-123",
            role: "assistant",
            content: "Hi there!",
            message_type: "assistant_response",
            timestamp: "2024-01-01T10:00:01Z",
          },
          conversation_id: "conv-123",
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const result = await chatService.startNewConversation("Hello");

      expect(api.post).toHaveBeenCalledWith("/chat/messages", {
        content: "Hello",
      });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe("continueConversation", () => {
    it("should continue an existing conversation", async () => {
      const mockResponse = {
        data: {
          user_message: {
            id: 3,
            conversation_id: "conv-123",
            role: "user",
            content: "How are you?",
            message_type: "user_input",
            timestamp: "2024-01-01T10:01:00Z",
          },
          ai_message: {
            id: 4,
            conversation_id: "conv-123",
            role: "assistant",
            content: "I am doing well, thank you!",
            message_type: "assistant_response",
            timestamp: "2024-01-01T10:01:01Z",
          },
          conversation_id: "conv-123",
        },
      };

      const { default: api } = await import(
        "../../src/apps/frontend/src/services/api"
      );
      vi.mocked(api.post).mockResolvedValue(mockResponse);

      const result = await chatService.continueConversation(
        "conv-123",
        "How are you?"
      );

      expect(api.post).toHaveBeenCalledWith("/chat/messages", {
        content: "How are you?",
        conversation_id: "conv-123",
      });
      expect(result).toEqual(mockResponse.data);
    });
  });
});

describe("chatApi singleton", () => {
  it("should export a singleton instance", async () => {
    const { chatApi } = await import(
      "../../src/apps/frontend/src/services/chatApi"
    );
    expect(chatApi).toBeInstanceOf(ChatApiService);
  });
});

