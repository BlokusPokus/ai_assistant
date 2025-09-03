"""
Network Request Mock Implementations

This module provides comprehensive mocks for network operations including
HTTP requests, WebSocket connections, and network utilities.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

# Optional imports for network libraries
try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    import httpx
except ImportError:
    httpx = None

try:
    import websockets
except ImportError:
    websockets = None


class MockHTTPResponse:
    """Mock implementation for HTTP responses."""
    
    def __init__(self, status: int = 200, headers: Dict[str, str] = None, 
                 content: Union[str, bytes, Dict] = None, url: str = ""):
        self.status = status
        self.headers = headers or {}
        self._content = content
        self.url = url
        self._json_data = None
        self._text_data = None
        self._bytes_data = None
    
    async def json(self) -> Dict[str, Any]:
        """Mock JSON response."""
        if self._json_data is None:
            if isinstance(self._content, dict):
                self._json_data = self._content
            elif isinstance(self._content, str):
                try:
                    self._json_data = json.loads(self._content)
                except json.JSONDecodeError:
                    self._json_data = {}
            else:
                self._json_data = {}
        return self._json_data
    
    async def text(self) -> str:
        """Mock text response."""
        if self._text_data is None:
            if isinstance(self._content, str):
                self._text_data = self._content
            elif isinstance(self._content, bytes):
                self._text_data = self._content.decode('utf-8')
            elif isinstance(self._content, dict):
                self._text_data = json.dumps(self._content)
            else:
                self._text_data = ""
        return self._text_data
    
    async def content(self) -> bytes:
        """Mock content response."""
        if self._bytes_data is None:
            if isinstance(self._content, bytes):
                self._bytes_data = self._content
            elif isinstance(self._content, str):
                self._bytes_data = self._content.encode('utf-8')
            elif isinstance(self._content, dict):
                self._bytes_data = json.dumps(self._content).encode('utf-8')
            else:
                self._bytes_data = b""
        return self._bytes_data
    
    def raise_for_status(self):
        """Mock raise_for_status."""
        if self.status >= 400:
            if aiohttp:
                raise aiohttp.ClientResponseError(
                    request_info=None,
                    history=None,
                    status=self.status,
                    message=f"HTTP {self.status}"
                )
            else:
                raise Exception(f"HTTP {self.status}")
    
    def close(self):
        """Mock close."""
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.close()


class MockHTTPXResponse:
    """Mock implementation for HTTPX responses."""
    
    def __init__(self, status_code: int = 200, headers: Dict[str, str] = None,
                 content: Union[str, bytes, Dict] = None, url: str = ""):
        self.status_code = status_code
        self.headers = headers or {}
        self._content = content
        self.url = url
        self._json_data = None
        self._text_data = None
    
    def json(self) -> Dict[str, Any]:
        """Mock JSON response."""
        if self._json_data is None:
            if isinstance(self._content, dict):
                self._json_data = self._content
            elif isinstance(self._content, str):
                try:
                    self._json_data = json.loads(self._content)
                except json.JSONDecodeError:
                    self._json_data = {}
            else:
                self._json_data = {}
        return self._json_data
    
    @property
    def text(self) -> str:
        """Mock text response."""
        if self._text_data is None:
            if isinstance(self._content, str):
                self._text_data = self._content
            elif isinstance(self._content, bytes):
                self._text_data = self._content.decode('utf-8')
            elif isinstance(self._content, dict):
                self._text_data = json.dumps(self._content)
            else:
                self._text_data = ""
        return self._text_data
    
    @property
    def content(self) -> bytes:
        """Mock content response."""
        if isinstance(self._content, bytes):
            return self._content
        elif isinstance(self._content, str):
            return self._content.encode('utf-8')
        elif isinstance(self._content, dict):
            return json.dumps(self._content).encode('utf-8')
        else:
            return b""
    
    def raise_for_status(self):
        """Mock raise_for_status."""
        if self.status_code >= 400:
            if httpx:
                raise httpx.HTTPStatusError(
                    message=f"HTTP {self.status_code}",
                    request=None,
                    response=self
                )
            else:
                raise Exception(f"HTTP {self.status_code}")


class MockWebSocket:
    """Mock implementation for WebSocket connections."""
    
    def __init__(self, url: str = ""):
        self.url = url
        self._closed = False
        self._messages = []
        self._sent_messages = []
        self._connected = True
    
    async def send(self, message: Union[str, bytes]):
        """Mock send operation."""
        if self._closed:
            if websockets:
                raise websockets.exceptions.ConnectionClosed(None, None)
            else:
                raise ConnectionError("Connection is closed")
        
        self._sent_messages.append({
            "message": message,
            "timestamp": datetime.now()
        })
    
    async def recv(self) -> Union[str, bytes]:
        """Mock receive operation."""
        if self._closed:
            if websockets:
                raise websockets.exceptions.ConnectionClosed(None, None)
            else:
                raise ConnectionError("Connection is closed")
        
        if self._messages:
            return self._messages.pop(0)
        else:
            # Simulate waiting for message
            await asyncio.sleep(0.1)
            return "mock message"
    
    async def close(self, code: int = 1000, reason: str = ""):
        """Mock close operation."""
        self._closed = True
        self._connected = False
    
    def add_message(self, message: Union[str, bytes]):
        """Add message to receive queue."""
        self._messages.append(message)
    
    def get_sent_messages(self) -> List[Dict[str, Any]]:
        """Get sent messages."""
        return self._sent_messages.copy()
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._connected and not self._closed
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class MockAIOHTTPSession:
    """Mock implementation for aiohttp ClientSession."""
    
    def __init__(self):
        self._responses = {}
        self._requests = []
        self._closed = False
    
    def set_response(self, url: str, response: MockHTTPResponse):
        """Set mock response for URL."""
        self._responses[url] = response
    
    def set_json_response(self, url: str, data: Dict[str, Any], status: int = 200):
        """Set JSON response for URL."""
        response = MockHTTPResponse(status=status, content=data)
        self.set_response(url, response)
    
    def set_text_response(self, url: str, text: str, status: int = 200):
        """Set text response for URL."""
        response = MockHTTPResponse(status=status, content=text)
        self.set_response(url, response)
    
    def set_error_response(self, url: str, status: int = 500, message: str = "Internal Server Error"):
        """Set error response for URL."""
        response = MockHTTPResponse(status=status, content={"error": message})
        self.set_response(url, response)
    
    async def get(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock GET request."""
        return await self._make_request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock POST request."""
        return await self._make_request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock PUT request."""
        return await self._make_request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock DELETE request."""
        return await self._make_request("DELETE", url, **kwargs)
    
    async def patch(self, url: str, **kwargs) -> MockHTTPResponse:
        """Mock PATCH request."""
        return await self._make_request("PATCH", url, **kwargs)
    
    async def _make_request(self, method: str, url: str, **kwargs) -> MockHTTPResponse:
        """Make mock request."""
        if self._closed:
            raise aiohttp.ClientError("Session is closed")
        
        # Record request
        self._requests.append({
            "method": method,
            "url": url,
            "kwargs": kwargs,
            "timestamp": datetime.now()
        })
        
        # Return mock response
        if url in self._responses:
            return self._responses[url]
        else:
            # Default response
            return MockHTTPResponse(
                status=200,
                content={"message": "Mock response"},
                url=url
            )
    
    async def close(self):
        """Mock close session."""
        self._closed = True
    
    def get_requests(self) -> List[Dict[str, Any]]:
        """Get all requests made."""
        return self._requests.copy()
    
    def clear_requests(self):
        """Clear request history."""
        self._requests.clear()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


class MockHTTPXClient:
    """Mock implementation for HTTPX client."""
    
    def __init__(self):
        self._responses = {}
        self._requests = []
        self._closed = False
    
    def set_response(self, url: str, response: MockHTTPXResponse):
        """Set mock response for URL."""
        self._responses[url] = response
    
    def set_json_response(self, url: str, data: Dict[str, Any], status_code: int = 200):
        """Set JSON response for URL."""
        response = MockHTTPXResponse(status_code=status_code, content=data)
        self.set_response(url, response)
    
    def set_text_response(self, url: str, text: str, status_code: int = 200):
        """Set text response for URL."""
        response = MockHTTPXResponse(status_code=status_code, content=text)
        self.set_response(url, response)
    
    def set_error_response(self, url: str, status_code: int = 500, message: str = "Internal Server Error"):
        """Set error response for URL."""
        response = MockHTTPXResponse(status_code=status_code, content={"error": message})
        self.set_response(url, response)
    
    def get(self, url: str, **kwargs) -> MockHTTPXResponse:
        """Mock GET request."""
        return self._make_request("GET", url, **kwargs)
    
    def post(self, url: str, **kwargs) -> MockHTTPXResponse:
        """Mock POST request."""
        return self._make_request("POST", url, **kwargs)
    
    def put(self, url: str, **kwargs) -> MockHTTPXResponse:
        """Mock PUT request."""
        return self._make_request("PUT", url, **kwargs)
    
    def delete(self, url: str, **kwargs) -> MockHTTPXResponse:
        """Mock DELETE request."""
        return self._make_request("DELETE", url, **kwargs)
    
    def patch(self, url: str, **kwargs) -> MockHTTPXResponse:
        """Mock PATCH request."""
        return self._make_request("PATCH", url, **kwargs)
    
    def _make_request(self, method: str, url: str, **kwargs) -> MockHTTPXResponse:
        """Make mock request."""
        if self._closed:
            raise httpx.RequestError("Client is closed")
        
        # Record request
        self._requests.append({
            "method": method,
            "url": url,
            "kwargs": kwargs,
            "timestamp": datetime.now()
        })
        
        # Return mock response
        if url in self._responses:
            return self._responses[url]
        else:
            # Default response
            return MockHTTPXResponse(
                status_code=200,
                content={"message": "Mock response"},
                url=url
            )
    
    def close(self):
        """Mock close client."""
        self._closed = True
    
    def get_requests(self) -> List[Dict[str, Any]]:
        """Get all requests made."""
        return self._requests.copy()
    
    def clear_requests(self):
        """Clear request history."""
        self._requests.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class MockWebSocketServer:
    """Mock implementation for WebSocket server."""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self._connections = []
        self._running = False
    
    async def start(self):
        """Start mock WebSocket server."""
        self._running = True
    
    async def stop(self):
        """Stop mock WebSocket server."""
        self._running = False
        for connection in self._connections:
            await connection.close()
        self._connections.clear()
    
    async def connect(self, url: str) -> MockWebSocket:
        """Mock WebSocket connection."""
        if not self._running:
            raise ConnectionError("Server is not running")
        
        connection = MockWebSocket(url)
        self._connections.append(connection)
        return connection
    
    def get_connections(self) -> List[MockWebSocket]:
        """Get all connections."""
        return self._connections.copy()
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running


class NetworkMockManager:
    """Manager for all network mocks."""
    
    def __init__(self):
        self.aiohttp_session = MockAIOHTTPSession()
        self.httpx_client = MockHTTPXClient()
        self.websocket_server = MockWebSocketServer()
        self._patches = []
    
    def start_mocking(self):
        """Start network mocking."""
        # Mock aiohttp
        self._patches.append(patch('aiohttp.ClientSession', return_value=self.aiohttp_session))
        
        # Mock httpx
        self._patches.append(patch('httpx.Client', return_value=self.httpx_client))
        
        # Mock websockets
        if websockets:
            self._patches.append(patch('websockets.connect', side_effect=self._mock_websocket_connect))
        
        # Start all patches
        for patch_obj in self._patches:
            patch_obj.start()
    
    def stop_mocking(self):
        """Stop network mocking."""
        for patch_obj in self._patches:
            patch_obj.stop()
        self._patches.clear()
    
    async def _mock_aiohttp_get(self, url: str, **kwargs):
        """Mock aiohttp get."""
        return await self.aiohttp_session.get(url, **kwargs)
    
    async def _mock_aiohttp_post(self, url: str, **kwargs):
        """Mock aiohttp post."""
        return await self.aiohttp_session.post(url, **kwargs)
    
    def _mock_httpx_get(self, url: str, **kwargs):
        """Mock httpx get."""
        return self.httpx_client.get(url, **kwargs)
    
    def _mock_httpx_post(self, url: str, **kwargs):
        """Mock httpx post."""
        return self.httpx_client.post(url, **kwargs)
    
    async def _mock_websocket_connect(self, url: str, **kwargs):
        """Mock websocket connect."""
        return await self.websocket_server.connect(url)
    
    def reset_all_mocks(self):
        """Reset all network mocks."""
        self.aiohttp_session.clear_requests()
        self.httpx_client.clear_requests()
        self.websocket_server.get_connections().clear()
    
    def get_mock_statistics(self) -> Dict[str, Any]:
        """Get mock usage statistics."""
        return {
            "aiohttp": {
                "requests_made": len(self.aiohttp_session.get_requests()),
                "responses_configured": len(self.aiohttp_session._responses)
            },
            "httpx": {
                "requests_made": len(self.httpx_client.get_requests()),
                "responses_configured": len(self.httpx_client._responses)
            },
            "websockets": {
                "connections": len(self.websocket_server.get_connections()),
                "server_running": self.websocket_server.is_running()
            }
        }


# Global network mock manager instance
network_mock_manager = NetworkMockManager()


def get_aiohttp_session_mock():
    """Get aiohttp session mock."""
    return network_mock_manager.aiohttp_session


def get_httpx_client_mock():
    """Get httpx client mock."""
    return network_mock_manager.httpx_client


def get_websocket_server_mock():
    """Get WebSocket server mock."""
    return network_mock_manager.websocket_server


def start_network_mocking():
    """Start network mocking."""
    network_mock_manager.start_mocking()


def stop_network_mocking():
    """Stop network mocking."""
    network_mock_manager.stop_mocking()


def reset_network_mocks():
    """Reset all network mocks."""
    network_mock_manager.reset_all_mocks()


def get_network_mock_statistics():
    """Get network mock usage statistics."""
    return network_mock_manager.get_mock_statistics()


# Context manager for easy mocking
class MockNetworkContext:
    """Context manager for network mocking."""
    
    def __init__(self):
        self.network_mock = network_mock_manager
    
    def __enter__(self):
        """Enter context."""
        self.network_mock.start_mocking()
        return self.network_mock
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        self.network_mock.stop_mocking()


def mock_network():
    """Get network mock context manager."""
    return MockNetworkContext()
