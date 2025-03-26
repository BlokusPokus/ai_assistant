from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.twiml.messaging_response import MessagingResponse
import os
import logging
from dotenv import load_dotenv
from agent_core.core import AgentCore
from agent_core.memory.memory import Memory
from agent_core.memory.client import MockMemoryDBClient
from agent_core.tools import ToolRegistry, WeatherTool, CalculatorTool
from agent_core.llm.gemini import GeminiLLM
from agent_core.config import GEMINI_API_KEY

# Load environment variables from .env file
load_dotenv(dotenv_path='agent_core/.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwilioService:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_FROM_NUMBER')
        self.to_number = os.getenv('TWILIO_TO_NUMBER')

        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("✅ Twilio credentials verified")
        except TwilioRestException as e:
            logger.error(f"Failed to initialize Twilio: {str(e)}")
            raise ValueError(f"Failed to initialize Twilio: {str(e)}")

        # Initialize the agent core components
        memory = Memory(MockMemoryDBClient())
        tool_registry = ToolRegistry()
        tool_registry.register(WeatherTool)
        tool_registry.register(CalculatorTool)
        llm_client = GeminiLLM(api_key=GEMINI_API_KEY)
        self.agent = AgentCore(
            memory=memory, tools=tool_registry, llm=llm_client)

    async def handle_sms_webhook(self, body: str, from_number: str) -> MessagingResponse:
        """Handle incoming SMS webhook and return appropriate response.

        Args:
            body (str): The message body
            from_number (str): The sender's phone number

        Returns:
            MessagingResponse: The Twilio response object
        """
        try:
            message = body.strip()
            logger.info(f"Received message: '{message}' from {from_number}")

            response = MessagingResponse()

            if message:
                result = self.agent.run(message)
                logger.info(f"Generated response: '{result}'")
                response.message(result)
            else:
                response.message("Please provide a valid input.")

            return response

        except Exception as e:
            logger.error(f"Error handling SMS webhook: {str(e)}")
            response = MessagingResponse()
            response.message(
                "Sorry, there was an error processing your message. Please try again.")
            return response

    async def send_sms(self, to: str, message: str) -> str:
        """Sends a simple SMS message.

        Args:
            to (str): The recipient's phone number
            message (str): The message content

        Returns:
            str: The message SID if successful

        Raises:
            TwilioRestException: If there's an error with the Twilio service
            Exception: For other unexpected errors
        """
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to
            )

            logger.info(f"Message sent successfully. SID: {message.sid}")
            logger.info(f"Message status: {message.status}")
            return message.sid

        except TwilioRestException as e:
            logger.error(f"Twilio error: {e.code} - {e.msg}")
            raise
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise


# Create a singleton instance
twilio_service = TwilioService()
