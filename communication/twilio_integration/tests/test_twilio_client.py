from twilio.twiml.messaging_response import MessagingResponse
from twilio.base.exceptions import TwilioRestException
from communication.twilio_integration.twilio_client import TwilioService
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
import os
import logging
import asyncio

# Load environment variables from .env file
load_dotenv(dotenv_path='agent_core/.env')
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))  # Debugging line

# Configure logging for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import after loading environment variables


class TestTwilioService(unittest.IsolatedAsyncioTestCase):

    @patch('communication.twilio_integration.twilio_client.Client')
    @patch('communication.twilio_integration.twilio_client.AgentCore')
    async def asyncSetUp(self, MockAgentCore, MockClient):
        # Mock the Twilio Client
        self.mock_client = MockClient.return_value
        self.mock_client.messages.create.return_value.sid = 'SM1234567890'

        # Mock the AgentCore
        self.mock_agent = MockAgentCore.return_value
        self.mock_agent.run.return_value = "Mock response from LLM"

        # Initialize TwilioService
        self.twilio_service = TwilioService()
        logger.info("TwilioService initialized for testing.")

    async def test_handle_sms_webhook(self):
        # Simulate an incoming message
        body = "Hello"
        from_number = "+1234567890"

        # Call the method
        response = await self.twilio_service.handle_sms_webhook(body, from_number)
        logger.info("Testing handle_sms_webhook with message: 'Hello'")

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
        # Create a new TwilioService instance with the mocked client
        self.twilio_service = TwilioService()

        # Configure the mock to raise the exception
        self.twilio_service.client.messages.create.side_effect = TwilioRestException(
            status=400,  # Added status parameter
            uri="fake://uri",
            msg="Error sending message",
            code=21211  # Common Twilio error code for invalid phone number
        )

        # Simulate sending a message with a Twilio exception
        to_number = "+0987654321"
        message = "Test message"

        logger.info("Testing send_sms with TwilioRestException")
        with self.assertRaises(TwilioRestException):
            await self.twilio_service.send_sms(to_number, message)


if __name__ == '__main__':
    unittest.main()
