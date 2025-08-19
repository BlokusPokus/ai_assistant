# AI Assistant System

A comprehensive personal automation system that handles scheduling, reminders, expense tracking, and grocery intelligence through multiple communication channels.

## 🌟 Overview

The AI Assistant System is an intelligent personal assistant that:

- Processes user requests through web, SMS, and email interfaces
- Manages calendar events and reminders
- Tracks expenses and integrates with budget applications
- Handles grocery shopping intelligence
- Maintains long-term knowledge through Obsidian integration
- Provides automated notifications and updates

## 🏗️ Architecture

### System Context

The system operates within an ecosystem of internal and external components:

- **Core System**: AI Assistant + Grocery Extractor System
- **External Integrations**:
  - Twilio (SMS communication)
  - Outlook (Email & Calendar)
  - Obsidian (Knowledge management)
  - Budget App (Expense tracking)

### Key Components

#### Backend API (FastAPI)

- **UserController**: Routes user input to appropriate handlers
- **AgentCore**: Main intelligence layer for intent recognition and action orchestration
- **AuthComponent**: Handles authentication and authorization
- **SchedulerComponent**: Manages reminders and calendar synchronization
- **ExpenseTrackerComponent**: Integrates with budget tracking
- **GroceryIntelligenceComponent**: Processes and optimizes grocery data
- **NotesComponent**: Manages Obsidian integration
- **NotificationService**: Handles SMS and email communications

#### Background Processing

- Celery-based task dispatcher
- Handles scheduled tasks and periodic operations
- Manages long-running operations asynchronously

#### Data Layer

- PostgreSQL database
- SQLAlchemy ORM
- Structured data storage for all system components

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for Celery)
- API keys for external services (Twilio, Outlook, etc.)

### Installation

bash
Clone the repository
git clone [repository-url]
Install dependencies
pip install -r requirements.txt
Set up environment variables
cp .env.example .env
Edit .env with your configuration
Initialize database
python scripts/init_db.py
Start the services
uvicorn app.main:app --reload # API server
celery -A app.worker worker --loglevel=info # Background worker
ini

.env example
DATABASE_URL=postgresql://user:pass@localhost/dbname
TWILIO_API_KEY=your_key
OUTLOOK_CLIENT_ID=your_client_id
OBSIDIAN_VAULT_PATH=/path/to/vault

## 🎯 Usage

### Web Interface

Access the web dashboard at `http://localhost:8000`

### API Endpoints

POST /api/v1/message - Send a message to the assistant
GET /api/v1/calendar - Get calendar events
POST /api/v1/reminder - Set a reminder
GET /api/v1/expenses - View expense tracking

### SMS Commands

Send SMS commands to your configured Twilio number:

- "remind me to [task] at [time]"
- "schedule meeting with [person] for [time]"
- "track expense [amount] for [category]"

## 🔄 Development Workflow

### Adding New Features

1. Create feature branch
2. Implement changes
3. Add tests
4. Submit pull request

### Testing

bash
Run unit tests
pytest
Run integration tests
pytest tests/integration
Run specific test suite
pytest tests/test_agent_core.py

## 📚 Documentation

Detailed documentation available in `/doc`:

- `component_diagram.md`: Detailed component architecture
- `container_diagram.md`: System container relationships
- `context_diagram.md`: System context and boundaries
- `sequence_diagram_agent_core.md`: Core processing flow

## 🛠️ Technical Details

### Agent Core

The system uses a ReAct-style architecture for decision making:

1. Receives user input
2. Processes through LLM for intent recognition
3. Executes appropriate tools based on intent
4. Maintains conversation context
5. Generates appropriate responses

### Memory Management

- Short-term context maintained during conversations
- Long-term storage through Obsidian integration
- Structured data in PostgreSQL

### Tool Integration

- Modular tool system
- Easy addition of new capabilities
- Standardized interface for all tools

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👥 Support

For support:

- Open an issue
- Contact development team
- Check documentation

## 🔮 Future Plans

- Enhanced natural language processing
- Additional external integrations
- Mobile application development
- Improved grocery intelligence
- Extended automation capabilities
