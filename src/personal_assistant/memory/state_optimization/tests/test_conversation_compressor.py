"""
Tests for ConversationCompressor class.
"""

import pytest

from ..conversation_compressor import ConversationCompressor


class TestConversationCompressor:
    """Test cases for ConversationCompressor"""

    def setup_method(self):
        """Set up test fixtures"""
        self.compressor = ConversationCompressor()

    def test_compress_short_history_no_compression(self):
        """Test that short history doesn't get compressed"""
        short_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        result = self.compressor.compress_conversation_history(short_history)

        assert len(result) == 2
        assert result == short_history

    def test_remove_duplicate_tool_calls(self):
        """Test removal of duplicate tool calls"""
        history = [
            {"role": "user", "content": "Create a note"},
            {"role": "assistant", "content": "I'll help you"},
            {
                "role": "tool",
                "name": "create_note",
                "content": "Error: validation failed",
            },
            {"role": "assistant", "content": "Let me try again"},
            {"role": "tool", "name": "create_note", "content": "Success: note created"},
        ]

        result = self.compressor.compress_conversation_history(history)

        # Should have 4 items (user, assistant, tool, assistant)
        assert len(result) == 4

        # Check that only the last tool call remains
        tool_calls = [item for item in result if item.get("role") == "tool"]
        assert len(tool_calls) == 1
        assert "Success: note created" in tool_calls[0]["content"]

    def test_filter_failed_attempts_after_success(self):
        """Test filtering of failed attempts after successful ones"""
        history = [
            {"role": "user", "content": "Create a note"},
            {
                "role": "tool",
                "name": "create_note",
                "content": "Error: validation failed",
            },
            {"role": "tool", "name": "create_note", "content": "Success: note created"},
            {"role": "user", "content": "Create another note"},
            {
                "role": "tool",
                "name": "create_note",
                "content": "Error: permission denied",
            },
        ]

        result = self.compressor.compress_conversation_history(history)

        # Should have 3 items (user, successful tool, user)
        assert len(result) == 3

        # Check that failed attempts after success are filtered
        tool_calls = [item for item in result if item.get("role") == "tool"]
        assert len(tool_calls) == 1
        assert "Success: note created" in tool_calls[0]["content"]

    def test_error_type_categorization(self):
        """Test error type categorization"""
        validation_error = {
            "role": "tool",
            "name": "test",
            "content": "Error: validation failed",
        }
        permission_error = {
            "role": "tool",
            "name": "test",
            "content": "Error: permission denied",
        }
        connection_error = {
            "role": "tool",
            "name": "test",
            "content": "Error: connection timeout",
        }

        validation_key = self.compressor._create_tool_key(validation_error)
        permission_key = self.compressor._create_tool_key(permission_error)
        connection_key = self.compressor._create_tool_key(connection_error)

        assert "validation_error" in validation_key
        assert "permission_error" in permission_key
        assert "execution_error" in connection_key

    def test_compression_statistics(self):
        """Test compression statistics calculation"""
        original_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "tool", "name": "test", "content": "Error: failed"},
            {"role": "tool", "name": "test", "content": "Success"},
        ]

        compressed_history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "tool", "name": "test", "content": "Success"},
        ]

        stats = self.compressor.get_compression_stats(
            original_history, compressed_history
        )

        assert stats["original_length"] == 4
        assert stats["compressed_length"] == 3
        assert stats["compression_ratio"] == 4 / 3
        assert stats["reduction_percentage"] == 25.0

    def test_remove_redundant_assistant_messages(self):
        """Test removal of redundant assistant messages"""
        history = [
            {"role": "user", "content": "Create a note"},
            {"role": "assistant", "content": "I'll help you create a note"},
            {"role": "tool", "name": "create_note", "content": "Success"},
            {
                "role": "assistant",
                "content": "I'll help you create a note",
            },  # Redundant
            {"role": "user", "content": "Thanks"},
        ]

        result = self.compressor.compress_conversation_history(history)

        # Should remove redundant assistant message
        assistant_messages = [
            item for item in result if item.get("role") == "assistant"
        ]
        assert len(assistant_messages) == 1

    def test_tool_name_extraction(self):
        """Test extraction of tool names from content"""
        content1 = "I'll help you with the create_note_tool"
        content2 = "Using the read_email_tool and send_message_tool"

        tools1 = self.compressor._extract_tool_names(content1)
        tools2 = self.compressor._extract_tool_names(content2)

        assert "create_note" in tools1
        assert "read_email" in tools2
        assert "send_message" in tools2


if __name__ == "__main__":
    pytest.main([__file__])
