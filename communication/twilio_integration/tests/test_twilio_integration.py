import unittest
import asyncio
from dotenv import load_dotenv
import os
import logging
from communication.twilio_integration.twilio_client import TwilioService

# Load environment variables from .env file
load_dotenv(dotenv_path='agent_core/.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestTwilioIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Verify environment variables are set
        required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN',
                         'TWILIO_FROM_NUMBER', 'TWILIO_TO_NUMBER']
        missing_vars = [var for var in required_vars if not os.getenv(var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}")

        self.twilio_service = TwilioService()
        # Your verified number for testing
        self.test_number = os.getenv('TWILIO_TO_NUMBER')
        logger.info("TwilioService initialized for integration testing")

    async def test_real_sms_send(self):
        """
        Integration test: Sends an actual SMS using Twilio
        Note: This will incur charges on your Twilio account
        """
        message = "🤖 This is a test message from your AI agent integration test!"

        logger.info(f"Attempting to send SMS to {self.test_number}")
        message_sid = await self.twilio_service.send_sms(
            to=self.test_number,
            message=message
        )

        logger.info(f"Message sent successfully with SID: {message_sid}")
        self.assertIsNotNone(message_sid)
        # Twilio message SIDs start with 'SM'
        self.assertTrue(message_sid.startswith('SM'))


if __name__ == '__main__':
    unittest.main()
