import logging
import os
import unittest
from unittest.mock import AsyncMock, Mock, patch

from dotenv import load_dotenv
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse

from .....communication.twilio_client import (
    TwilioService,
)
from .....core import AgentCore

# Load environment variables from config file
load_dotenv(
    dotenv_path=f'config/{os.getenv("ENVIRONMENT", "development")}.env')
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))  # Debugging line

# Configure logging for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import after loading environment variables


class TestTwilioService(unittest.IsolatedAsyncioTestCase):

    @patch('communication.twilio_integration.twilio_client.Client')
    async def asyncSetUp(self, MockClient):
        # Mock the Twilio Client
        self.mock_client = MockClient.return_value
        self.mock_client.messages.create.return_value.sid = 'SM1234567890'

        # Create a mock AgentCore with async run method
        self.mock_agent = Mock(spec=AgentCore)
        self.mock_agent.run = AsyncMock(return_value="Mock response from LLM")

        # Initialize TwilioService with the mock agent
        self.twilio_service = TwilioService(agent_core=self.mock_agent)
        logger.info("TwilioService initialized for testing.")

    async def test_handle_sms_webhook(self):
        # Simulate an incoming message
        body = "Hello"
        from_number = "+1234567890"

        # Call the method
        response = await self.twilio_service.handle_sms_webhook(body, from_number)
        logger.info("Testing handle_sms_webhook with message: 'Hello'")

        # Verify AgentCore.run was called with the message
        self.mock_agent.run.assert_called_once_with(body)

        # Check the response
        self.assertIsInstance(response, MessagingResponse)
        self.assertIn("Mock response from LLM", str(response))

    async def test_send_sms(self):
        # Simulate sending a message
        to_number = "+0987654321"
        message = "Test message"

        # Call the method
        message_sid = await self.twilio_service.send_sms(to_number, message)
        logger.info(
            f"Testing send_sms with message: '{message}' to {to_number}")

        # Check the message SID
        self.assertEqual(message_sid, 'SM1234567890')
        self.mock_client.messages.create.assert_called_once_with(
            body=message,
            from_=self.twilio_service.from_number,
            to=to_number
        )

    @patch('communication.twilio_integration.twilio_client.Client')
    async def test_send_sms_twilio_exception(self, MockClient):
        # Mock AgentCore for this specific test
        mock_agent = Mock(spec=AgentCore)

        # Create a new TwilioService instance with the mocked client and agent
        self.twilio_service = TwilioService(agent_core=mock_agent)

        # Configure the mock to raise the exception
        self.twilio_service.client.messages.create.side_effect = TwilioRestException(
            status=400,
            uri="fake://uri",
            msg="Error sending message",
            code=21211  # Common Twilio error code for invalid phone number
        )

        # Simulate sending a message with a Twilio exception
        to_number = "+14388290590"
        message = "Test message"

        logger.info("Testing send_sms with TwilioRestException")
        with self.assertRaises(TwilioRestException):
            await self.twilio_service.send_sms(to_number, message)


if __name__ == '__main__':
    unittest.main()
