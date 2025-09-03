"""
Unit tests for mock implementations.

This module tests all mock implementations including
external APIs, database, file system, and network mocks.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, Mock

from tests.mocks.external_api_mocks import (
    get_twilio_sms_mock, get_oauth_provider_mock, get_email_service_mock,
    get_file_storage_mock, reset_all_external_mocks, get_mock_statistics
)
from tests.mocks.database_mocks import (
    get_async_session_mock, get_engine_mock, get_async_session_local_mock,
    reset_all_database_mocks, get_database_mock_statistics, mock_database
)
from tests.mocks.filesystem_mocks import (
    get_filesystem_mock, start_filesystem_mocking, stop_filesystem_mocking,
    reset_filesystem_mock, get_filesystem_statistics, mock_filesystem
)
from tests.mocks.network_mocks import (
    get_aiohttp_session_mock, get_httpx_client_mock, get_websocket_server_mock,
    start_network_mocking, stop_network_mocking, reset_network_mocks,
    get_network_mock_statistics, mock_network
)


class TestExternalAPIMocks:
    """Test external API mock implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_all_external_mocks()

    def test_twilio_sms_mock_creation(self):
        """Test Twilio SMS mock creation."""
        twilio_mock = get_twilio_sms_mock()
        
        assert twilio_mock is not None
        assert hasattr(twilio_mock, 'create_message')
        assert hasattr(twilio_mock, 'get_message')
        assert hasattr(twilio_mock, 'list_messages')

    def test_twilio_sms_message_creation(self):
        """Test Twilio SMS message creation."""
        twilio_mock = get_twilio_sms_mock()
        
        message = twilio_mock.create_message(
            to="+1234567890",
            from_="+0987654321",
            body="Test message"
        )
        
        assert message["to"] == "+1234567890"
        assert message["from_"] == "+0987654321"
        assert message["body"] == "Test message"
        assert message["status"] == "queued"
        assert "sid" in message

    def test_twilio_sms_message_retrieval(self):
        """Test Twilio SMS message retrieval."""
        twilio_mock = get_twilio_sms_mock()
        
        # Create a message
        message = twilio_mock.create_message(
            to="+1234567890",
            from_="+0987654321",
            body="Test message"
        )
        
        # Retrieve the message
        retrieved_message = twilio_mock.get_message(message["sid"])
        
        assert retrieved_message is not None
        assert retrieved_message["sid"] == message["sid"]
        assert retrieved_message["body"] == "Test message"

    def test_oauth_provider_mock_creation(self):
        """Test OAuth provider mock creation."""
        google_mock = get_oauth_provider_mock("google")
        
        assert google_mock is not None
        assert google_mock.provider_name == "google"
        assert hasattr(google_mock, 'get_authorization_url')
        assert hasattr(google_mock, 'exchange_code_for_token')

    def test_oauth_authorization_url_generation(self):
        """Test OAuth authorization URL generation."""
        google_mock = get_oauth_provider_mock("google")
        
        auth_url = google_mock.get_authorization_url(
            client_id="test_client_id",
            redirect_uri="http://localhost:8000/callback",
            scopes=["read", "write"],
            state="test_state"
        )
        
        assert "https://google.com/oauth/authorize" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "state=test_state" in auth_url

    def test_oauth_token_exchange(self):
        """Test OAuth token exchange."""
        google_mock = get_oauth_provider_mock("google")
        
        # Generate authorization URL first to create the authorization
        auth_url = google_mock.get_authorization_url(
            client_id="test_client_id",
            redirect_uri="http://localhost:8000/callback",
            scopes=["read", "write"]
        )
        
        # Get the code from the created authorization
        # The code is the key in the authorizations dict
        codes = list(google_mock.authorizations.keys())
        assert len(codes) > 0
        code = codes[-1]  # Get the most recent code
        
        # Exchange code for token
        token_data = google_mock.exchange_code_for_token(
            code=code,
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/callback"
        )
        
        assert "access_token" in token_data
        assert "refresh_token" in token_data
        assert token_data["token_type"] == "Bearer"
        assert token_data["expires_in"] == 3600

    def test_email_service_mock_creation(self):
        """Test email service mock creation."""
        email_mock = get_email_service_mock()
        
        assert email_mock is not None
        assert hasattr(email_mock, 'send_email')
        assert hasattr(email_mock, 'send_template_email')

    def test_email_sending(self):
        """Test email sending."""
        email_mock = get_email_service_mock()
        
        email = email_mock.send_email(
            to="test@example.com",
            subject="Test Subject",
            html="<h1>Test</h1>",
            text="Test"
        )
        
        assert email["to"] == "test@example.com"
        assert email["subject"] == "Test Subject"
        assert email["status"] == "sent"
        assert "id" in email

    def test_template_email_sending(self):
        """Test template email sending."""
        email_mock = get_email_service_mock()
        
        email = email_mock.send_template_email(
            to="test@example.com",
            template_name="welcome",
            template_data={"name": "John"}
        )
        
        assert email["to"] == "test@example.com"
        assert email["subject"] == "Welcome to Personal Assistant"
        assert email["status"] == "sent"

    def test_file_storage_mock_creation(self):
        """Test file storage mock creation."""
        storage_mock = get_file_storage_mock()
        
        assert storage_mock is not None
        assert hasattr(storage_mock, 'upload_file')
        assert hasattr(storage_mock, 'download_file')
        assert hasattr(storage_mock, 'delete_file')

    def test_file_upload(self):
        """Test file upload."""
        storage_mock = get_file_storage_mock()
        
        file_data = storage_mock.upload_file(
            file_path="test.txt",
            content=b"test content",
            bucket="user-uploads"
        )
        
        assert file_data["path"] == "test.txt"
        assert file_data["bucket"] == "user-uploads"
        assert file_data["size_bytes"] == 12
        assert "id" in file_data
        assert "url" in file_data

    def test_file_download(self):
        """Test file download."""
        storage_mock = get_file_storage_mock()
        
        # Upload a file first
        file_data = storage_mock.upload_file(
            file_path="test.txt",
            content=b"test content"
        )
        
        # Download the file
        download_data = storage_mock.download_file(file_data["id"])
        
        assert download_data["id"] == file_data["id"]
        assert "content" in download_data
        assert "metadata" in download_data

    def test_mock_statistics(self):
        """Test mock statistics."""
        # Use some mocks
        twilio_mock = get_twilio_sms_mock()
        twilio_mock.create_message("+1234567890", "+0987654321", "Test")
        
        email_mock = get_email_service_mock()
        email_mock.send_email("test@example.com", "Test", "Test")
        
        stats = get_mock_statistics()
        
        assert "twilio_sms" in stats
        assert "email_service" in stats
        assert stats["twilio_sms"]["messages_sent"] == 1
        assert stats["email_service"]["emails_sent"] == 1


class TestDatabaseMocks:
    """Test database mock implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_all_database_mocks()

    @pytest.mark.asyncio
    async def test_async_session_mock_creation(self):
        """Test async session mock creation."""
        session = get_async_session_mock()
        
        assert session is not None
        assert hasattr(session, 'add')
        assert hasattr(session, 'commit')
        assert hasattr(session, 'rollback')

    @pytest.mark.asyncio
    async def test_async_session_operations(self):
        """Test async session operations."""
        session = get_async_session_mock()
        
        # Test add operation
        mock_instance = Mock()
        mock_instance.id = None
        mock_instance.created_at = None
        mock_instance.updated_at = None
        
        await session.add(mock_instance)
        
        assert mock_instance.id is not None
        assert mock_instance.created_at is not None
        assert mock_instance.updated_at is not None

    @pytest.mark.asyncio
    async def test_async_session_commit_rollback(self):
        """Test async session commit and rollback."""
        session = get_async_session_mock()
        
        # Test commit
        await session.commit()
        assert session.is_committed()
        assert not session.is_rolled_back()
        
        # Test rollback
        await session.rollback()
        assert session.is_rolled_back()
        assert not session.is_committed()

    @pytest.mark.asyncio
    async def test_async_session_context_manager(self):
        """Test async session context manager."""
        async with get_async_session_mock() as session:
            assert session.is_active()
            await session.add(Mock())
        
        assert session.is_committed()

    def test_engine_mock_creation(self):
        """Test engine mock creation."""
        engine = get_engine_mock()
        
        assert engine is not None
        assert hasattr(engine, 'connect')
        assert hasattr(engine, 'execute')
        assert hasattr(engine, 'scalar')

    def test_engine_operations(self):
        """Test engine operations."""
        engine = get_engine_mock()
        
        # Test execute
        result = engine.execute("SELECT * FROM users")
        assert result is not None
        
        # Test scalar
        scalar_result = engine.scalar("SELECT COUNT(*) FROM users")
        assert scalar_result == "mock_scalar_result"

    def test_async_session_local_mock(self):
        """Test AsyncSessionLocal mock."""
        session_local = get_async_session_local_mock()
        
        assert session_local is not None
        assert callable(session_local)
        
        session = session_local()
        assert session is not None

    def test_database_mock_statistics(self):
        """Test database mock statistics."""
        # Create some sessions
        session1 = get_async_session_mock()
        session2 = get_async_session_mock()
        
        # Use engine
        engine = get_engine_mock()
        engine.execute("SELECT * FROM users")
        
        stats = get_database_mock_statistics()
        
        assert "sessions_created" in stats
        assert "queries_executed" in stats
        assert stats["sessions_created"] >= 2
        assert stats["queries_executed"] >= 1

    def test_database_mock_context_manager(self):
        """Test database mock context manager."""
        with mock_database() as db_mock:
            assert db_mock is not None
            session = db_mock.get_async_session()
            assert session is not None


class TestFileSystemMocks:
    """Test file system mock implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_filesystem_mock()

    def test_filesystem_mock_creation(self):
        """Test file system mock creation."""
        fs_mock = get_filesystem_mock()
        
        assert fs_mock is not None
        assert hasattr(fs_mock, 'add_file')
        assert hasattr(fs_mock, 'add_directory')
        assert hasattr(fs_mock, 'exists')

    def test_file_operations(self):
        """Test file operations."""
        fs_mock = get_filesystem_mock()
        
        # Add a file
        fs_mock.add_file("/test/file.txt", "test content", 12)
        
        assert fs_mock.exists("/test/file.txt")
        assert fs_mock.is_file("/test/file.txt")
        assert not fs_mock.is_dir("/test/file.txt")
        assert fs_mock.get_size("/test/file.txt") == 12
        assert fs_mock.get_content("/test/file.txt") == "test content"

    def test_directory_operations(self):
        """Test directory operations."""
        fs_mock = get_filesystem_mock()
        
        # Add a directory
        fs_mock.add_directory("/test")
        
        assert fs_mock.exists("/test")
        assert fs_mock.is_dir("/test")
        assert not fs_mock.is_file("/test")

    def test_file_system_mocking(self):
        """Test file system mocking."""
        with mock_filesystem() as fs_mock:
            # Add some files and directories
            fs_mock.add_file("/test/file1.txt", "content1")
            fs_mock.add_file("/test/file2.txt", "content2")
            fs_mock.add_directory("/test")
            fs_mock.add_directory("/test/subdir")
            
            # Test operations
            assert fs_mock.exists("/test/file1.txt")
            assert fs_mock.exists("/test/subdir")
            
            # Test statistics
            stats = fs_mock.get_statistics()
            assert stats["total_files"] == 2
            assert stats["total_directories"] == 2

    def test_filesystem_statistics(self):
        """Test file system statistics."""
        fs_mock = get_filesystem_mock()
        
        # Add some files
        fs_mock.add_file("/file1.txt", "content1", 10)
        fs_mock.add_file("/file2.txt", "content2", 20)
        fs_mock.add_directory("/dir1")
        
        stats = get_filesystem_statistics()
        
        assert stats["total_files"] == 2
        assert stats["total_directories"] == 1
        assert stats["total_size"] == 30


class TestNetworkMocks:
    """Test network mock implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_network_mocks()

    @pytest.mark.asyncio
    async def test_aiohttp_session_mock_creation(self):
        """Test aiohttp session mock creation."""
        session = get_aiohttp_session_mock()
        
        assert session is not None
        assert hasattr(session, 'get')
        assert hasattr(session, 'post')
        assert hasattr(session, 'close')

    @pytest.mark.asyncio
    async def test_aiohttp_requests(self):
        """Test aiohttp requests."""
        session = get_aiohttp_session_mock()
        
        # Set up mock response
        session.set_json_response("http://example.com/api", {"message": "success"})
        
        # Make request
        response = await session.get("http://example.com/api")
        assert response.status == 200
        data = await response.json()
        assert data["message"] == "success"

    @pytest.mark.asyncio
    async def test_aiohttp_error_response(self):
        """Test aiohttp error response."""
        session = get_aiohttp_session_mock()
        
        # Set up error response
        session.set_error_response("http://example.com/error", 404, "Not Found")
        
        # Make request
        response = await session.get("http://example.com/error")
        assert response.status == 404
        data = await response.json()
        assert data["error"] == "Not Found"

    def test_httpx_client_mock_creation(self):
        """Test httpx client mock creation."""
        client = get_httpx_client_mock()
        
        assert client is not None
        assert hasattr(client, 'get')
        assert hasattr(client, 'post')
        assert hasattr(client, 'close')

    def test_httpx_requests(self):
        """Test httpx requests."""
        client = get_httpx_client_mock()
        
        # Set up mock response
        client.set_json_response("http://example.com/api", {"message": "success"})
        
        # Make request
        response = client.get("http://example.com/api")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "success"

    def test_httpx_error_response(self):
        """Test httpx error response."""
        client = get_httpx_client_mock()
        
        # Set up error response
        client.set_error_response("http://example.com/error", 500, "Internal Server Error")
        
        # Make request
        response = client.get("http://example.com/error")
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "Internal Server Error"

    @pytest.mark.asyncio
    async def test_websocket_mock_creation(self):
        """Test WebSocket mock creation."""
        server = get_websocket_server_mock()
        
        assert server is not None
        assert hasattr(server, 'connect')
        assert hasattr(server, 'start')
        assert hasattr(server, 'stop')

    @pytest.mark.asyncio
    async def test_websocket_operations(self):
        """Test WebSocket operations."""
        server = get_websocket_server_mock()
        await server.start()
        
        # Connect WebSocket
        websocket = await server.connect("ws://localhost:8765")
        
        assert websocket is not None
        assert websocket.is_connected()
        
        # Send message
        await websocket.send("Hello, WebSocket!")
        
        # Check sent messages
        sent_messages = websocket.get_sent_messages()
        assert len(sent_messages) == 1
        assert sent_messages[0]["message"] == "Hello, WebSocket!"
        
        # Close connection
        await websocket.close()
        assert not websocket.is_connected()

    def test_network_mock_statistics(self):
        """Test network mock statistics."""
        # Use some mocks
        session = get_aiohttp_session_mock()
        session.set_json_response("http://example.com", {"test": "data"})
        
        client = get_httpx_client_mock()
        client.set_text_response("http://example.com", "test response")
        
        stats = get_network_mock_statistics()
        
        assert "aiohttp" in stats
        assert "httpx" in stats
        assert "websockets" in stats
        assert stats["aiohttp"]["responses_configured"] >= 1
        assert stats["httpx"]["responses_configured"] >= 1

    def test_network_mock_context_manager(self):
        """Test network mock context manager."""
        with mock_network() as network_mock:
            assert network_mock is not None
            session = network_mock.aiohttp_session
            assert session is not None


class TestMockIntegration:
    """Test integration of all mock implementations."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_all_external_mocks()
        reset_all_database_mocks()
        reset_filesystem_mock()
        reset_network_mocks()

    @pytest.mark.asyncio
    async def test_comprehensive_mock_workflow(self):
        """Test comprehensive mock workflow."""
        # Test external API mocks
        twilio_mock = get_twilio_sms_mock()
        message = twilio_mock.create_message("+1234567890", "+0987654321", "Test")
        assert message["status"] == "queued"
        
        # Test database mocks
        session = get_async_session_mock()
        await session.add(Mock())
        await session.commit()
        assert session.is_committed()
        
        # Test file system mocks
        with mock_filesystem() as fs_mock:
            fs_mock.add_file("/test.txt", "content")
            assert fs_mock.exists("/test.txt")
        
        # Test network mocks
        with mock_network() as network_mock:
            session = network_mock.aiohttp_session
            session.set_json_response("http://example.com", {"test": "data"})
            
            response = await session.get("http://example.com")
            data = await response.json()
            assert data["test"] == "data"

    def test_mock_statistics_integration(self):
        """Test mock statistics integration."""
        # Use all mocks
        twilio_mock = get_twilio_sms_mock()
        twilio_mock.create_message("+1234567890", "+0987654321", "Test")
        
        email_mock = get_email_service_mock()
        email_mock.send_email("test@example.com", "Test", "Test")
        
        session = get_async_session_mock()
        engine = get_engine_mock()
        engine.execute("SELECT * FROM users")
        
        fs_mock = get_filesystem_mock()
        fs_mock.add_file("/test.txt", "content")
        
        client = get_httpx_client_mock()
        client.set_json_response("http://example.com", {"test": "data"})
        
        # Get all statistics
        external_stats = get_mock_statistics()
        db_stats = get_database_mock_statistics()
        fs_stats = get_filesystem_statistics()
        network_stats = get_network_mock_statistics()
        
        # Verify statistics
        assert external_stats["twilio_sms"]["messages_sent"] == 1
        assert external_stats["email_service"]["emails_sent"] == 1
        assert db_stats["queries_executed"] == 1
        assert fs_stats["total_files"] == 1
        assert network_stats["httpx"]["responses_configured"] >= 1
