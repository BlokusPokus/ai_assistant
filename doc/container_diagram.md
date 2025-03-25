C4Container

title AI Assistant System - Container Diagram

Person(user, "👤 User", "Interacts via web, SMS, email")

Boundary(ai, "AI assistant") {
Container(web, "🖥️ Web Application", "React", "Allows users to view their data")
Container(api, "⚙️ Backend API", "FastAPI (Python)", "Handles business logic and integrates with external systems")
Container(auth, "Authentication Module", "FastAPI / OAuth2 / JWT", "Manages user login, tokens, and permissions")
SystemDb(db, "💾 Database", "PostgreSQL", "Stores users, schedules, expenses, grocery data, notes, etc.")
Container(obsidian, "📔 Obsidian Integration", "Local File System or API", "Pushes/pulls long-term notes")
Container(worker, "⏱️ Background Worker", "Python + Celery", "Executes scheduled tasks like reminders, note syncing, grocery analysis")
}

Boundary(external, "External systems") {
System_Ext(twilio, "📱 Twilio", "SMS communication")
System_Ext(outlook, "📧 Outlook", "Email service")
System_Ext(calendar, "📅 Outlook Calendar", "Schedules and events")
System_Ext(obsidian_ext, "📓 Obsidian", "Knowledge management")
System_Ext(budget, "💰 Budget App", "Budget tracking")
}

Rel(user, web, "Uses")
Rel(web, api, "Makes REST API calls to")
Rel(api, db, "Reads/writes to")
Rel(api, worker, "Dispatches background tasks to")
Rel(api, auth, "Delegates login/authentication to")
Rel(api, twilio, "Sends and receives SMS via")
Rel(api, outlook, "Sends email via")
Rel(api, calendar, "Reads/writes events to")
Rel(api, obsidian, "Reads/writes long-term notes to")
Rel(obsidian, obsidian_ext, "Syncs with")
Rel(api, budget, "Fetches budget info from")
