import type { MessageResponse } from '@/services/chatApi';

/**
 * Utility functions for message filtering and processing
 */

/**
 * Check if a message should be hidden from the user interface
 */
export function shouldHideMessage(message: MessageResponse): boolean {
  // Hide system messages
  if (
    message.message_type === 'system' ||
    message.message_type === 'internal'
  ) {
    return true;
  }

  // Hide messages with debug information
  if (
    message.content.includes('Conversation:') &&
    message.content.includes('User Input:')
  ) {
    return true;
  }

  // Hide messages containing conversation IDs (UUID pattern)
  const uuidPattern =
    /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;
  if (uuidPattern.test(message.content)) {
    return true;
  }

  // Hide messages with focus areas or debug info
  if (
    message.content.includes('Focus Areas:') ||
    message.content.includes('Debug:')
  ) {
    return true;
  }

  return false;
}

/**
 * Filter messages to only show user and assistant messages
 */
export function filterVisibleMessages(
  messages: MessageResponse[]
): MessageResponse[] {
  return messages.filter(message => {
    // Only show user and assistant messages
    if (message.role !== 'user' && message.role !== 'assistant') {
      return false;
    }

    // Hide system/debug messages
    if (shouldHideMessage(message)) {
      return false;
    }

    return true;
  });
}

/**
 * Remove duplicate messages based on ID
 */
export function removeDuplicateMessages(
  messages: MessageResponse[]
): MessageResponse[] {
  const seen = new Set<number>();
  return messages.filter(message => {
    if (seen.has(message.id)) {
      return false;
    }
    seen.add(message.id);
    return true;
  });
}

/**
 * Check if a message is a duplicate of another message
 */
export function isDuplicateMessage(
  message: MessageResponse,
  existingMessages: MessageResponse[]
): boolean {
  return existingMessages.some(
    existing =>
      existing.id === message.id ||
      (existing.content === message.content &&
        existing.role === message.role &&
        Math.abs(
          new Date(existing.timestamp).getTime() -
            new Date(message.timestamp).getTime()
        ) < 1000)
  );
}

/**
 * Format message content for display
 */
export function formatMessageContent(content: string): string {
  // Remove any trailing whitespace
  return content.trim();
}

/**
 * Check if a message is empty or contains only whitespace
 */
export function isEmptyMessage(message: MessageResponse): boolean {
  return !message.content || message.content.trim().length === 0;
}
