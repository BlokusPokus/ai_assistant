C4Component

title Backend API (FastAPI) - Component Diagram

Container_Boundary(api_boundary, "⚙️ Backend API") {

Component(userController, "UserController", "FastAPI Router", "Manages user profile endpoints and routes user input to the Agent")

Component(agentCore, "AgentCore", "Python module", "Determines user intent and orchestrates actions using internal and external tools")

Component(authComponent, "AuthComponent", "OAuth2/JWT", "Handles login, tokens, and auth checks")

Component(scheduler, "SchedulerComponent", "Python module", "Manages reminders and calendar sync")

Component(expenses, "ExpenseTrackerComponent", "Python module", "Tracks expenses and syncs with Budget App")

Component(grocery, "GroceryIntelligenceComponent", "Python module", "Processes grocery data and suggests optimizations")

Component(notes, "NotesComponent", "Python module", "Saves/retrieves notes to/from Obsidian")

Component(notifications, "NotificationService", "Python service", "Sends SMS and email")

Component(calendarSync, "CalendarIntegration", "Python module", "Integrates with Outlook Calendar")

Component(tasks, "TaskDispatcher", "Celery Client", "Dispatches tasks to background worker, both scheduled and on-demand")

Component(dal, "DataAccessLayer", "SQLAlchemy or similar", "Abstracts access to PostgreSQL database")

}

Container_Boundary(g, "⚙️ Backend PI") {

Container_Ext(db, "💾 Database", "PostgreSQL")

Container_Ext(worker, "⏱️ Background Worker", "Python + Celery", "Executes user-triggered and periodic tasks like reminders, syncing, and grocery analysis")

Container_Ext(obsidian, "📔 Obsidian Integration", "Local File System")

System_Ext(twilio, "📱 Twilio", "SMS communication")

System_Ext(outlook, "📧 Outlook", "Email service")

System_Ext(calendar, "📅 Outlook Calendar", "Schedules and events")

System_Ext(budget, "💰 Budget App", "Budget tracking")

}

Rel(userController, authComponent, "Delegates auth to")

Rel(userController, agentCore, "Delegates user intent to")

Rel(agentCore, scheduler, "Triggers scheduling tasks")

Rel(agentCore, calendarSync, "Syncs calendar data with")

Rel(agentCore, expenses, "Manages budget interactions")

Rel(agentCore, grocery, "Triggers grocery intelligence")

Rel(agentCore, notes, "Manages long-term notes")

Rel(agentCore, notifications, "Sends messages via")

Rel(agentCore, tasks, "Dispatches background tasks to")

Rel(scheduler, calendarSync, "Uses")

Rel(scheduler, tasks, "Schedules background jobs via")

Rel(scheduler, dal, "Reads/writes schedules via")

Rel(expenses, budget, "Fetches budget data from")

Rel(expenses, dal, "Stores expense data")

Rel(grocery, dal, "Reads grocery data from DB")

Rel(grocery, tasks, "Triggers grocery analysis")

Rel(notes, obsidian, "Stores/retrieves notes via")

Rel(notifications, twilio, "Sends/receives SMS")

Rel(notifications, outlook, "Sends emails")

Rel(calendarSync, calendar, "Syncs with")

Rel(tasks, worker, "Dispatches jobs to")

Rel(dal, db, "Executes queries")
