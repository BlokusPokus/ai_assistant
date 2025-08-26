import logging
import os
import unittest
from unittest.mock import AsyncMock, Mock, patch

from dotenv import load_dotenv
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse

from personal_assistant.communication.twilio_integration.twilio_client import (
    TwilioService,
)
from personal_assistant.core import AgentCore

# Load environment variables from config file
load_dotenv(
    dotenv_path=f'config/{os.getenv("ENVIRONMENT", "development")}.env')
print("GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))  # Debugging line

# Configure logging for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import after loading environment variables


class TestTwilioService(unittest.IsolatedAsyncioTestCase):

    @patch('personal_assistant.communication.twilio_integration.twilio_client.Client')
    @patch('personal_assistant.communication.twilio_integration.twilio_client.UserIdentificationService')
    async def asyncSetUp(self, MockUserIdentification, MockClient):
        # Mock the Twilio Client
        self.mock_client = MockClient.return_value
        self.mock_client.messages.create.return_value.sid = 'SM1234567890'

        # Create a mock AgentCore with async run method
        self.mock_agent = Mock(spec=AgentCore)
        self.mock_agent.run = AsyncMock(return_value="Mock response from LLM")

        # Mock UserIdentificationService
        self.mock_user_identification = MockUserIdentification.return_value
        self.mock_user_identification.identify_user_by_phone = AsyncMock()

        # Initialize TwilioService with the mock agent
        self.twilio_service = TwilioService(agent_core=self.mock_agent)
        logger.info("TwilioService initialized for testing.")

    async def test_handle_sms_webhook_with_registered_user(self):
        """Test SMS webhook handling with a registered user."""
        # Mock user identification returning a valid user
        self.mock_user_identification.identify_user_by_phone.return_value = {
            'id': 123,
            'email': 'test@example.com',
            'full_name': 'Test User'
        }

        # Simulate an incoming message
        body = "Hello"
        from_number = "+1234567890"

        # Call the method
        response = await self.twilio_service.handle_sms_webhook(body, from_number)
        logger.info("Testing handle_sms_webhook with registered user")

        # Verify UserIdentificationService was called
        self.mock_user_identification.identify_user_by_phone.assert_called_once_with(from_number)

        # Verify AgentCore.run was called with the message and user ID
        self.mock_agent.run.assert_called_once_with(body, 123)

        # Check the response
        self.assertIsInstance(response, MessagingResponse)
        self.assertIn("Mock response from LLM", str(response))

    async def test_handle_sms_webhook_with_unregistered_user(self):
        """Test SMS webhook handling with an unregistered user."""
        # Mock user identification returning None (unregistered user)
        self.mock_user_identification.identify_user_by_phone.return_value = None

        # Simulate an incoming message
        body = "Hello"
        from_number = "+1234567890"

        # Call the method
        response = await self.twilio_service.handle_sms_webhook(body, from_number)
        logger.info("Testing handle_sms_webhook with unregistered user")

        # Verify UserIdentificationService was called
        self.mock_user_identification.identify_user_by_phone.assert_called_once_with(from_number)

        # Verify AgentCore.run was NOT called
        self.mock_agent.run.assert_not_called()

        # Check the response contains helpful guidance
        self.assertIsInstance(response, MessagingResponse)
        response_str = str(response)
        self.assertIn("Welcome!", response_str)
        self.assertIn("not registered yet", response_str)
        self.assertIn("To get started with SMS service", response_str)
        self.assertIn("Visit your dashboard", response_str)

    async def test_handle_sms_webhook_empty_message(self):
        """Test SMS webhook handling with empty message."""
        # Mock user identification returning None
        self.mock_user_identification.identify_user_by_phone.return_value = None

        # Simulate an empty message
        body = ""
        from_number = "+1234567890"

        # Call the method
        response = await self.twilio_service.handle_sms_webhook(body, from_number)
        logger.info("Testing handle_sms_webhook with empty message")

        # Check the response
        self.assertIsInstance(response, MessagingResponse)
        self.assertIn("Please provide a valid input", str(response))

    async def test_handle_sms_webhook_whitespace_message(self):
        """Test SMS webhook handling with whitespace-only message."""
        # Mock user identification returning None
        self.mock_user_identification.identify_user_by_phone.return_value = None

        # Simulate a whitespace-only message
        body = "   "
        from_number = "+1234567890"

        # Call the method
        response = await self.twilio_service.handle_sms_webhook(body, from_number)
        logger.info("Testing handle_sms_webhook with whitespace message")

        # Check the response
        self.assertIsInstance(response, MessagingResponse)
        self.assertIn("Please provide a valid input", str(response))

    async def test_handle_sms_webhook_exception_handling(self):
        """Test SMS webhook exception handling."""
        # Mock user identification raising an exception
        self.mock_user_identification.identify_user_by_phone.side_effect = Exception("Database error")

        # Simulate an incoming message
        body = "Hello"
        from_number = "+1234567890"

        # Call the method
        response = await self.twilio_service.handle_sms_webhook(body, from_number)
        logger.info("Testing handle_sms_webhook exception handling")

        # Check the response contains error message
        self.assertIsInstance(response, MessagingResponse)
        response_str = str(response)
        self.assertIn("Sorry, there was an error", response_str)
        self.assertIn("Please try again", response_str)

    def test_format_phone_number_us_10_digits(self):
        """Test phone number formatting for US 10-digit numbers."""
        phone = "5551234567"
        formatted = self.twilio_service._format_phone_number(phone)
        self.assertEqual(formatted, "+1 (555) 123-4567")

    def test_format_phone_number_us_11_digits(self):
        """Test phone number formatting for US 11-digit numbers starting with 1."""
        phone = "15551234567"
        formatted = self.twilio_service._format_phone_number(phone)
        self.assertEqual(formatted, "+1 (555) 123-4567")

    def test_format_phone_number_already_plus(self):
        """Test phone number formatting for numbers already starting with +."""
        phone = "+15551234567"
        formatted = self.twilio_service._format_phone_number(phone)
        self.assertEqual(formatted, "+1 (555) 123-4567")

    def test_format_phone_number_international(self):
        """Test phone number formatting for international numbers."""
        phone = "+44123456789"
        formatted = self.twilio_service._format_phone_number(phone)
        self.assertEqual(formatted, "+44123456789")

    def test_format_phone_number_with_dashes_and_spaces(self):
        """Test phone number formatting with dashes and spaces."""
        phone = "555-123-4567"
        formatted = self.twilio_service._format_phone_number(phone)
        self.assertEqual(formatted, "+1 (555) 123-4567")

    def test_format_phone_number_with_parentheses(self):
        """Test phone number formatting with parentheses."""
        phone = "(555) 123-4567"
        formatted = self.twilio_service._format_phone_number(phone)
        self.assertEqual(formatted, "+1 (555) 123-4567")

    def test_create_helpful_guidance_response(self):
        """Test creation of helpful guidance response."""
        phone_number = "+1234567890"
        response = self.twilio_service._create_helpful_guidance_response(phone_number)
        
        self.assertIsInstance(response, MessagingResponse)
        response_str = str(response)
        
        # Check that the response contains helpful guidance
        self.assertIn("Welcome!", response_str)
        self.assertIn("not registered yet", response_str)
        self.assertIn("To get started with SMS service", response_str)
        self.assertIn("Visit your dashboard", response_str)
        self.assertIn("Add this phone number", response_str)
        self.assertIn("Start texting", response_str)
        self.assertIn("Need help?", response_str)

    async def test_send_sms(self):
        """Test sending SMS message."""
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

    @patch('personal_assistant.communication.twilio_integration.twilio_client.Client')
    async def test_send_sms_twilio_exception(self, MockClient):
        """Test SMS sending with Twilio exception."""
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

    async def test_send_verification_sms(self):
        """Test sending verification SMS."""
        # Simulate sending verification code
        to_number = "+1234567890"
        verification_code = "123456"

        # Call the method
        message_sid = await self.twilio_service.send_verification_sms(to_number, verification_code)
        logger.info(f"Testing send_verification_sms to {to_number}")

        # Check the message SID
        self.assertEqual(message_sid, 'SM1234567890')
        
        # Verify the message was created with verification content
        self.mock_client.messages.create.assert_called_once()
        call_args = self.mock_client.messages.create.call_args
        self.assertEqual(call_args[1]['to'], to_number)
        self.assertEqual(call_args[1]['from_'], self.twilio_service.from_number)
        
        # Check that the message contains verification content
        message_body = call_args[1]['body']
        self.assertIn(verification_code, message_body)
        self.assertIn("verification code", message_body)
        self.assertIn("expire in 10 minutes", message_body)

    @patch('personal_assistant.communication.twilio_integration.twilio_client.Client')
    async def test_send_verification_sms_twilio_exception(self, MockClient):
        """Test verification SMS sending with Twilio exception."""
        # Mock AgentCore for this specific test
        mock_agent = Mock(spec=AgentCore)

        # Create a new TwilioService instance with the mocked client and agent
        self.twilio_service = TwilioService(agent_core=mock_agent)

        # Configure the mock to raise the exception
        self.twilio_service.client.messages.create.side_effect = TwilioRestException(
            status=400,
            uri="fake://uri",
            msg="Error sending verification message",
            code=21211
        )

        # Simulate sending verification SMS with a Twilio exception
        to_number = "+1234567890"
        verification_code = "123456"

        logger.info("Testing send_verification_sms with TwilioRestException")
        with self.assertRaises(TwilioRestException):
            await self.twilio_service.send_verification_sms(to_number, verification_code)


if __name__ == '__main__':
    unittest.main()
