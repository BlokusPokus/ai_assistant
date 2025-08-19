# Personal Assistant

An AI-powered personal assistant with SMS integration, calendar management, and intelligent task processing.

## Features

- 🤖 AI-powered natural language processing
- 📱 SMS integration via Twilio
- 📅 Calendar management and event creation
- 🔄 Recurring event support
- 📧 Email management
- 💰 Expense tracking
- 🛒 Grocery list management
- 📝 Notes and reminders
- ⏰ Background task scheduling

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Twilio account
- Google Gemini API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/personal_assistant.git
cd personal_assistant

# Install the package
pip install -e .

# Set up environment variables
cp config/development.env .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the application
uvicorn src.apps.fastapi_app.main:app --reload
```

## Documentation

- [API Documentation](docs/api/)
- [Development Guide](docs/development/)
- [Deployment Guide](docs/deployment/)
- [User Guides](docs/user_guides/)

## Contributing

See [CONTRIBUTING.md](docs/development/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
