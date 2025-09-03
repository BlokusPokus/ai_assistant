import logging
import os

from dotenv import load_dotenv
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from ...core import AgentCore

# adjust import as needed
from ...sms_router.services.user_identification import UserIdentificationService

# Load environment variables from config file
load_dotenv(dotenv_path=f'config/{os.getenv("ENVIRONMENT", "development")}.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwilioService:
    def __init__(self, agent_core: AgentCore):
        """Initialize TwilioService with Twilio credentials and an AgentCore instance.

        Args:
            agent_core (AgentCore): Pre-configured instance of AgentCore to handle messages
        """
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")
        self.to_number = os.getenv("TWILIO_TO_NUMBER")

        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("✅ Twilio credentials verified")
        except TwilioRestException as e:
            logger.error(f"Failed to initialize Twilio: {str(e)}")
            raise ValueError(f"Failed to initialize Twilio: {str(e)}")

        self.agent = agent_core
        # Initialize user identification service for enhanced guidance
        self.user_identification = UserIdentificationService()

    async def handle_sms_webhook(
        self, body: str, from_number: str
    ) -> MessagingResponse:
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

            # MessagingResponse is a Twilio helper class for generating TwiML (XML) responses to SMS messages.
            # It allows you to easily construct replies that Twilio will send back to the user.
            response = MessagingResponse()

            if message:
                # Use enhanced user identification service for better context
                user_info = await self.user_identification.identify_user_by_phone(
                    from_number
                )

                if user_info is None:
                    # Enhanced guidance for unregistered users
                    return self._create_helpful_guidance_response(from_number)

                # Process message with existing logic for registered users
                result = await self.agent.run(message, user_info["id"])
                logger.info(f"Generated response: '{result}'")
                response.message(result)
            else:
                response.message("Please provide a valid input.")

            return response

        except Exception as e:
            logger.error(f"Error handling SMS webhook: {str(e)}")
            response = MessagingResponse()
            response.message(
                "Sorry, there was an error processing your message. Please try again."
            )
            return response

    def _create_helpful_guidance_response(self, phone_number: str) -> MessagingResponse:
        """Create a helpful guidance response for unregistered phone numbers.

        Args:
            phone_number (str): The unregistered phone number

        Returns:
            MessagingResponse: Helpful guidance response
        """
        response = MessagingResponse()

        # Format phone number for better readability
        formatted_phone = self._format_phone_number(phone_number)

        guidance_message = (
            f"Welcome! Your phone number {formatted_phone} is not registered yet.\n\n"
            "To get started with SMS service:\n"
            "1. Visit your dashboard\n"
            "2. Add this phone number to your profile\n"
            "3. Start texting!\n\n"
            "Need help? Contact support at help@personalassistant.com"
        )

        response.message(guidance_message)
        logger.info(f"Sent helpful guidance to unregistered phone: {phone_number}")
        return response

    def _format_phone_number(self, phone_number: str) -> str:
        """Format phone number for better readability.

        Args:
            phone_number (str): Raw phone number

        Returns:
            str: Formatted phone number
        """
        # Remove any non-digit characters except +
        cleaned = "".join(c for c in phone_number if c.isdigit() or c == "+")

        # Add + if not present and format as +1 (XXX) XXX-XXXX for US numbers
        if not cleaned.startswith("+"):
            if len(cleaned) == 10:
                return f"+1 ({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
            elif len(cleaned) == 11 and cleaned.startswith("1"):
                return f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
            else:
                return f"+{cleaned}"
        else:
            # Already has +, format if it's a US number
            if len(cleaned) == 12 and cleaned.startswith("+1"):
                digits = cleaned[2:]
                return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            else:
                return cleaned

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
                body=message, from_=self.from_number, to=to
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

    async def send_verification_sms(self, to: str, verification_code: str) -> str:
        """Send SMS verification code to a phone number.

        Args:
            to (str): The recipient's phone number
            verification_code (str): The verification code to send

        Returns:
            str: The message SID if successful

        Raises:
            TwilioRestException: If there's an error with the Twilio service
            Exception: For other unexpected errors
        """
        try:
            message_text = (
                f"Your Personal Assistant verification code is: {verification_code}\n\n"
                "This code will expire in 10 minutes. If you didn't request this code, "
                "please ignore this message."
            )

            message = self.client.messages.create(
                body=message_text, from_=self.from_number, to=to
            )

            logger.info(f"Verification SMS sent successfully. SID: {message.sid}")
            return message.sid

        except TwilioRestException as e:
            logger.error(f"Twilio error sending verification SMS: {e.code} - {e.msg}")
            raise
        except Exception as e:
            logger.error(f"Error sending verification SMS: {str(e)}")
            raise
