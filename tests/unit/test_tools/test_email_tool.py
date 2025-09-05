"""
Unit tests for Email Tool.

This module tests the Email tool functionality including
email reading, sending, deletion, content retrieval, searching,
and moving emails via Microsoft Graph API.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any

from personal_assistant.tools.emails.email_tool import EmailTool
from tests.utils.test_helpers import TestHelper
from tests.utils.test_data_generators import ToolDataGenerator


@pytest.fixture(autouse=True)
def mock_email_environment():
    """Mock email environment variables and token initialization to avoid validation errors in tests."""
    with patch('personal_assistant.tools.emails.email_internal.validate_environment_variables') as mock_validate, \
         patch('personal_assistant.tools.emails.email_internal.get_environment_error_message') as mock_error, \
         patch('personal_assistant.tools.emails.email_tool.EmailTool._initialize_token') as mock_init_token, \
         patch('personal_assistant.tools.emails.ms_graph.get_access_token') as mock_get_token, \
         patch.dict('os.environ', {
             'MICROSOFT_APPLICATION_ID': 'test-app-id',
             'MICROSOFT_CLIENT_SECRET': 'test-client-secret'
         }):
        
        # Mock the validation to return success
        mock_validate.return_value = (True, 'test-app-id', 'test-client-secret')
        mock_error.return_value = "Test error message"
        mock_get_token.return_value = "test-access-token"
        
        yield mock_validate


class TestEmailTool:
    """Test cases for Email Tool."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.email_tool = EmailTool()
        self.test_message_id = "test-message-id-123"
        self.test_recipients = "test@example.com, another@example.com"
        self.test_subject = "Test Email Subject"
        self.test_body = "This is a test email body content."
        self.test_count = 10
        self.test_batch_size = 5

    def test_email_tool_initialization(self):
        """Test Email tool initialization."""
        assert self.email_tool is not None
        assert hasattr(self.email_tool, 'read_emails_tool')
        assert hasattr(self.email_tool, 'send_email_tool')
        assert hasattr(self.email_tool, 'delete_email_tool')
        assert hasattr(self.email_tool, 'get_email_content_tool')
        assert hasattr(self.email_tool, 'get_sent_emails_tool')
        assert hasattr(self.email_tool, 'search_emails_tool')
        assert hasattr(self.email_tool, 'move_email_tool')
        assert self.email_tool.ms_graph_url == "https://graph.microsoft.com/v1.0"
        assert self.email_tool.scopes == ["Mail.Read", "Mail.ReadWrite", "Mail.Send", "User.Read"]

    def test_email_tool_iteration(self):
        """Test that Email tool is iterable and returns all tools."""
        tools = list(self.email_tool)
        assert len(tools) == 7
        
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "read_emails",
            "send_email",
            "delete_email",
            "get_email_content",
            "get_sent_emails",
            "search_emails",
            "move_email"
        ]
        
        for expected_name in expected_names:
            assert expected_name in tool_names

    def test_read_emails_tool_properties(self):
        """Test read emails tool properties."""
        tool = self.email_tool.read_emails_tool
        assert tool.name == "read_emails"
        assert "Read recent emails from your inbox" in tool.description
        assert "count" in tool.parameters
        assert "batch_size" in tool.parameters

    def test_send_email_tool_properties(self):
        """Test send email tool properties."""
        tool = self.email_tool.send_email_tool
        assert tool.name == "send_email"
        assert "Send an email to one or more recipients" in tool.description
        assert "to_recipients" in tool.parameters
        assert "subject" in tool.parameters
        assert "body" in tool.parameters
        assert "is_html" in tool.parameters

    def test_delete_email_tool_properties(self):
        """Test delete email tool properties."""
        tool = self.email_tool.delete_email_tool
        assert tool.name == "delete_email"
        assert "Delete an email by its ID" in tool.description
        assert "message_id" in tool.parameters

    def test_get_email_content_tool_properties(self):
        """Test get email content tool properties."""
        tool = self.email_tool.get_email_content_tool
        assert tool.name == "get_email_content"
        assert "Get the full content of a specific email by its ID" in tool.description
        assert "message_id" in tool.parameters

    def test_get_sent_emails_tool_properties(self):
        """Test get sent emails tool properties."""
        tool = self.email_tool.get_sent_emails_tool
        assert tool.name == "get_sent_emails"
        assert "Read recent emails you have sent" in tool.description
        assert "count" in tool.parameters
        assert "batch_size" in tool.parameters

    def test_search_emails_tool_properties(self):
        """Test search emails tool properties."""
        tool = self.email_tool.search_emails_tool
        assert tool.name == "search_emails"
        assert "Search emails by query" in tool.description
        assert "query" in tool.parameters
        assert "count" in tool.parameters
        assert "date_from" in tool.parameters
        assert "date_to" in tool.parameters
        assert "folder" in tool.parameters

    def test_move_email_tool_properties(self):
        """Test move email tool properties."""
        tool = self.email_tool.move_email_tool
        assert tool.name == "move_email"
        assert "Move an email from one folder to another folder" in tool.description
        assert "message_id" in tool.parameters
        assert "destination_folder" in tool.parameters

    def test_tool_parameter_types(self):
        """Test that tool parameters have correct types."""
        # Test read_emails_tool parameters
        read_params = self.email_tool.read_emails_tool.parameters
        assert read_params["count"]["type"] == "integer"
        assert read_params["batch_size"]["type"] == "integer"
        
        # Test send_email_tool parameters
        send_params = self.email_tool.send_email_tool.parameters
        assert send_params["to_recipients"]["type"] == "string"
        assert send_params["subject"]["type"] == "string"
        assert send_params["body"]["type"] == "string"
        assert send_params["is_html"]["type"] == "boolean"
        
        # Test search_emails_tool parameters
        search_params = self.email_tool.search_emails_tool.parameters
        assert search_params["query"]["type"] == "string"
        assert search_params["count"]["type"] == "integer"
        assert search_params["date_from"]["type"] == "string"
        assert search_params["date_to"]["type"] == "string"
        assert search_params["folder"]["type"] == "string"

    @pytest.mark.asyncio
    async def test_get_emails_success(self):
        """Test successful email retrieval."""
        mock_emails = [
            {
                "id": "email1",
                "subject": "Test Email 1",
                "bodyPreview": "Preview of email 1",
                "receivedDateTime": "2024-01-01T10:00:00Z",
                "from": {"emailAddress": {"address": "sender1@example.com"}},
                "isDraft": False
            },
            {
                "id": "email2",
                "subject": "Test Email 2",
                "bodyPreview": "Preview of email 2",
                "receivedDateTime": "2024-01-01T11:00:00Z",
                "from": {"emailAddress": {"address": "sender2@example.com"}},
                "isDraft": False
            }
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": mock_emails}
        
        with patch('personal_assistant.tools.emails.email_tool.validate_email_parameters') as mock_validate, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.build_email_params') as mock_params, \
             patch('personal_assistant.tools.emails.email_tool.parse_email_response') as mock_parse, \
             patch('personal_assistant.tools.emails.email_tool.format_email_list_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (self.test_count, self.test_batch_size)
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_params.return_value = {"$top": 5}
            mock_parse.side_effect = lambda x: x  # Return the email as-is
            mock_format.return_value = "Formatted email list"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.get_emails(self.test_count, self.test_batch_size)
            
            assert result == "Formatted email list"
            mock_validate.assert_called_once_with(self.test_count, self.test_batch_size)

    @pytest.mark.asyncio
    async def test_get_emails_http_error(self):
        """Test email retrieval with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        with patch('personal_assistant.tools.emails.email_tool.validate_email_parameters') as mock_validate, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.build_email_params') as mock_params, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (self.test_count, self.test_batch_size)
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_params.return_value = {"$top": 5}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.get_emails(self.test_count, self.test_batch_size)
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test successful email sending."""
        mock_response = Mock()
        mock_response.status_code = 202  # Accepted
        
        with patch('personal_assistant.tools.emails.email_tool.validate_recipients') as mock_validate_recipients, \
             patch('personal_assistant.tools.emails.email_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.emails.email_tool.validate_body') as mock_validate_body, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.clean_recipients_string') as mock_clean, \
             patch('personal_assistant.tools.emails.email_tool.build_email_message_data') as mock_build, \
             patch('personal_assistant.tools.emails.email_tool.format_send_email_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate_recipients.return_value = (True, "")
            mock_validate_subject.return_value = (True, "")
            mock_validate_body.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_clean.return_value = [{"emailAddress": {"address": "test@example.com"}}]
            mock_build.return_value = {"message": "data"}
            mock_format.return_value = {"success": True, "message": "Email sent successfully"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.send_email(
                self.test_recipients,
                self.test_subject,
                self.test_body,
                False
            )
            
            assert result["success"] is True
            assert "Email sent successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_send_email_invalid_recipients(self):
        """Test email sending with invalid recipients."""
        with patch('personal_assistant.tools.emails.email_tool.validate_recipients') as mock_validate:
            mock_validate.return_value = (False, "Invalid email format")
            
            result = await self.email_tool.send_email(
                "invalid-email",
                self.test_subject,
                self.test_body
            )
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    @pytest.mark.asyncio
    async def test_send_email_invalid_subject(self):
        """Test email sending with invalid subject."""
        with patch('personal_assistant.tools.emails.email_tool.validate_recipients') as mock_validate_recipients, \
             patch('personal_assistant.tools.emails.email_tool.validate_subject') as mock_validate_subject:
            
            mock_validate_recipients.return_value = (True, "")
            mock_validate_subject.return_value = (False, "Subject cannot be empty")
            
            result = await self.email_tool.send_email(
                self.test_recipients,
                "",
                self.test_body
            )
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    @pytest.mark.asyncio
    async def test_send_email_invalid_body(self):
        """Test email sending with invalid body."""
        with patch('personal_assistant.tools.emails.email_tool.validate_recipients') as mock_validate_recipients, \
             patch('personal_assistant.tools.emails.email_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.emails.email_tool.validate_body') as mock_validate_body:
            
            mock_validate_recipients.return_value = (True, "")
            mock_validate_subject.return_value = (True, "")
            mock_validate_body.return_value = (False, "Body cannot be empty")
            
            result = await self.email_tool.send_email(
                self.test_recipients,
                self.test_subject,
                ""
            )
            
            # Should return error response
            if isinstance(result, dict):
                assert result.get("error", False)
            else:
                assert "Error" in result

    @pytest.mark.asyncio
    async def test_delete_email_success(self):
        """Test successful email deletion."""
        mock_response = Mock()
        mock_response.status_code = 204  # No content on successful deletion
        
        with patch('personal_assistant.tools.emails.email_tool.validate_message_id') as mock_validate, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.format_delete_email_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_format.return_value = {"success": True, "message": "Email deleted successfully"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.delete.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.delete_email(self.test_message_id)
            
            assert result["success"] is True
            assert "Successfully deleted email with ID:" in result["message"]

    @pytest.mark.asyncio
    async def test_delete_email_not_found(self):
        """Test email deletion when email not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch('personal_assistant.tools.emails.email_tool.validate_message_id') as mock_validate, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.handle_email_not_found') as mock_handle, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_handle.return_value = {"error": True, "message": "Email not found"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.delete.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.delete_email(self.test_message_id)
            
            assert result["error"] is True
            assert "Email not found" in result["message"]

    @pytest.mark.asyncio
    async def test_get_email_content_success(self):
        """Test successful email content retrieval."""
        mock_email_data = {
            "id": self.test_message_id,
            "subject": "Test Subject",
            "body": {"content": "<p>Test email content</p>"},
            "receivedDateTime": "2024-01-01T10:00:00Z",
            "from": {"emailAddress": {"address": "sender@example.com"}},
            "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}]
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_email_data
        
        with patch('personal_assistant.tools.emails.email_tool.validate_message_id') as mock_validate, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.build_email_params') as mock_params, \
             patch('personal_assistant.tools.emails.email_tool.parse_email_content_response') as mock_parse, \
             patch('personal_assistant.tools.emails.email_tool.format_email_content_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_params.return_value = {"$select": "id,subject,body"}
            mock_parse.return_value = {"subject": "Test Subject", "body": "Test email content"}
            mock_format.return_value = {"success": True, "content": "Test email content"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.get_email_content(self.test_message_id)
            
            assert result["success"] is True
            assert "Test email content" in result["data"]["body"]

    @pytest.mark.asyncio
    async def test_get_sent_emails_success(self):
        """Test successful sent emails retrieval."""
        mock_sent_emails = [
            {
                "id": "sent1",
                "subject": "Sent Email 1",
                "bodyPreview": "Preview of sent email 1",
                "sentDateTime": "2024-01-01T10:00:00Z",
                "toRecipients": [{"emailAddress": {"address": "recipient1@example.com"}}],
                "isDraft": False
            }
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": mock_sent_emails}
        
        with patch('personal_assistant.tools.emails.email_tool.validate_email_parameters') as mock_validate, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.build_email_params') as mock_params, \
             patch('personal_assistant.tools.emails.email_tool.format_email_list_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.return_value = (self.test_count, self.test_batch_size)
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_params.return_value = {"$top": 5}
            mock_format.return_value = "Formatted sent emails list"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.get_sent_emails(self.test_count, self.test_batch_size)
            
            assert result == "Formatted sent emails list"

    @pytest.mark.asyncio
    async def test_search_emails_success(self):
        """Test successful email search."""
        mock_search_results = [
            {
                "id": "search1",
                "subject": "Search Result 1",
                "bodyPreview": "Preview of search result 1",
                "receivedDateTime": "2024-01-01T10:00:00Z",
                "from": {"emailAddress": {"address": "sender@example.com"}},
                "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}],
                "isDraft": False,
                "importance": "normal"
            }
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": mock_search_results}
        
        with patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.format_email_list_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_format.return_value = "Formatted search results"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.search_emails("test query", 10)
            
            assert result == "Formatted search results"

    @pytest.mark.asyncio
    async def test_search_emails_empty_query(self):
        """Test email search with empty query."""
        result = await self.email_tool.search_emails("")
        
        # Should return error response
        if isinstance(result, dict):
            assert result.get("error", False)
        else:
            assert "general_error" in result

    @pytest.mark.asyncio
    async def test_move_email_success(self):
        """Test successful email move."""
        mock_move_response = Mock()
        mock_move_response.status_code = 200
        mock_move_response.json.return_value = {"subject": "Test Email"}
        
        mock_message_response = Mock()
        mock_message_response.status_code = 200
        mock_message_response.json.return_value = {"parentFolderId": "folder123"}
        
        mock_folder_response = Mock()
        mock_folder_response.status_code = 200
        mock_folder_response.json.return_value = {"displayName": "Inbox"}
        
        with patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.format_move_email_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_format.return_value = {"success": True, "message": "Email moved successfully"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.side_effect = [mock_message_response, mock_folder_response]
            mock_client_instance.post.return_value = mock_move_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.move_email(self.test_message_id, "Archive")
            
            assert result["success"] is True
            assert "Email moved successfully" in result["message"]

    @pytest.mark.asyncio
    async def test_move_email_empty_message_id(self):
        """Test email move with empty message ID."""
        result = await self.email_tool.move_email("", "Archive")
        
        # Should return error response
        if isinstance(result, dict):
            assert result.get("error", False)
        else:
            assert "general_error" in result

    @pytest.mark.asyncio
    async def test_move_email_empty_destination(self):
        """Test email move with empty destination folder."""
        result = await self.email_tool.move_email(self.test_message_id, "")
        
        # Should return error response
        if isinstance(result, dict):
            assert result.get("error", False)
        else:
            assert "general_error" in result

    def test_tool_categories(self):
        """Test that tools can have categories set."""
        tool = self.email_tool.send_email_tool
        tool.set_category("Email")
        assert tool.category == "Email"
        
        # Test that category is returned correctly
        assert tool.category == "Email"

    def test_tool_user_intent_tracking(self):
        """Test that tools can track user intent."""
        tool = self.email_tool.send_email_tool
        
        # Test setting user intent
        tool.set_user_intent("Send an important email")
        assert tool.get_user_intent() == "Send an important email"
        
        # Test default user intent
        new_tool = EmailTool().send_email_tool
        assert new_tool.get_user_intent() == "Unknown user intent"

    def test_email_tool_token_management(self):
        """Test email tool token management methods."""
        # Test token validation
        assert hasattr(self.email_tool, '_is_token_valid')
        assert hasattr(self.email_tool, '_get_valid_token')
        
        # Test that these methods exist and are callable
        assert callable(self.email_tool._is_token_valid)
        assert callable(self.email_tool._get_valid_token)

    def test_email_tool_html_cleaning(self):
        """Test email tool HTML content cleaning."""
        assert hasattr(self.email_tool, '_clean_html_content')
        assert callable(self.email_tool._clean_html_content)
        
        # Test with sample HTML content
        html_content = "<p>This is <b>bold</b> text with <a href='#'>links</a></p>"
        result = self.email_tool._clean_html_content(html_content)
        assert isinstance(result, str)
        assert "bold" in result  # Should extract text content

    def test_email_tool_parameter_validation(self):
        """Test that tool parameters are properly defined."""
        # Test send_email_tool parameters
        send_params = self.email_tool.send_email_tool.parameters
        assert send_params["to_recipients"]["type"] == "string"
        assert send_params["subject"]["type"] == "string"
        assert send_params["body"]["type"] == "string"
        assert send_params["is_html"]["type"] == "boolean"
        
        # Test search_emails_tool parameters
        search_params = self.email_tool.search_emails_tool.parameters
        assert search_params["query"]["type"] == "string"
        assert search_params["count"]["type"] == "integer"
        assert search_params["date_from"]["type"] == "string"
        assert search_params["date_to"]["type"] == "string"
        assert search_params["folder"]["type"] == "string"

    def test_email_tool_descriptions(self):
        """Test that tool descriptions are informative."""
        # Test that descriptions contain key information
        assert "emails" in self.email_tool.read_emails_tool.description.lower()
        assert "send" in self.email_tool.send_email_tool.description.lower()
        assert "delete" in self.email_tool.delete_email_tool.description.lower()
        assert "content" in self.email_tool.get_email_content_tool.description.lower()
        assert "sent" in self.email_tool.get_sent_emails_tool.description.lower()
        assert "search" in self.email_tool.search_emails_tool.description.lower()
        assert "move" in self.email_tool.move_email_tool.description.lower()

    @pytest.mark.asyncio
    async def test_get_emails_with_different_parameters(self):
        """Test get_emails with various parameter combinations."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        
        test_cases = [
            {"count": 5, "batch_size": 2},
            {"count": 20, "batch_size": 10},
            {"count": 1, "batch_size": 1},
        ]
        
        with patch('personal_assistant.tools.emails.email_tool.validate_email_parameters') as mock_validate, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.build_email_params') as mock_params, \
             patch('personal_assistant.tools.emails.email_tool.format_email_list_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate.side_effect = lambda c, b: (c, b)
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_params.return_value = {"$top": 5}
            mock_format.return_value = "Formatted email list"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            for case in test_cases:
                result = await self.email_tool.get_emails(case["count"], case["batch_size"])
                assert result == "Formatted email list"

    @pytest.mark.asyncio
    async def test_send_email_with_html_content(self):
        """Test sending email with HTML content."""
        mock_response = Mock()
        mock_response.status_code = 202
        
        with patch('personal_assistant.tools.emails.email_tool.validate_recipients') as mock_validate_recipients, \
             patch('personal_assistant.tools.emails.email_tool.validate_subject') as mock_validate_subject, \
             patch('personal_assistant.tools.emails.email_tool.validate_body') as mock_validate_body, \
             patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.clean_recipients_string') as mock_clean, \
             patch('personal_assistant.tools.emails.email_tool.build_email_message_data') as mock_build, \
             patch('personal_assistant.tools.emails.email_tool.format_send_email_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_validate_recipients.return_value = (True, "")
            mock_validate_subject.return_value = (True, "")
            mock_validate_body.return_value = (True, "")
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_clean.return_value = [{"emailAddress": {"address": "test@example.com"}}]
            mock_build.return_value = {"message": "data"}
            mock_format.return_value = {"success": True, "message": "HTML email sent successfully"}
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            html_body = "<h1>Test HTML Email</h1><p>This is <b>bold</b> text.</p>"
            result = await self.email_tool.send_email(
                self.test_recipients,
                self.test_subject,
                html_body,
                is_html=True
            )
            
            assert result["success"] is True
            assert "Email sent successfully to" in result["message"]
            # Verify that build_email_message_data was called with is_html=True
            mock_build.assert_called_once()
            call_args = mock_build.call_args[0]
            assert call_args[3] is True  # is_html parameter

    @pytest.mark.asyncio
    async def test_search_emails_with_date_range(self):
        """Test email search with date range parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        
        with patch('personal_assistant.tools.emails.email_tool.build_email_headers') as mock_headers, \
             patch('personal_assistant.tools.emails.email_tool.format_email_list_response') as mock_format, \
             patch('httpx.AsyncClient') as mock_client:
            
            mock_headers.return_value = {"Authorization": "Bearer token"}
            mock_format.return_value = "Formatted search results with date range"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await self.email_tool.search_emails(
                "test query",
                count=15,
                date_from="2024-01-01",
                date_to="2024-01-31",
                folder="inbox"
            )
            
            assert result == "Formatted search results with date range"

