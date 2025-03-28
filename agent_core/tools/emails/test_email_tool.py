import asyncio
from agent_core.tools.emails.email_tool import EmailTool


async def test_email_tool():
    try:
        # Initialize the tool
        email_tool = EmailTool()

        # Try reading emails
        emails = await email_tool.read_recent_emails(count=3)

        print("\nRecent Emails:")
        print("-------------")
        for email in emails:
            print(f"From: {email['from_name']} <{email['from_email']}>")
            print(f"Subject: {email['subject']}")
            print(f"Preview: {email['preview']}")
            print(f"Received: {email['received']}")
            print("-------------\n")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_email_tool())
