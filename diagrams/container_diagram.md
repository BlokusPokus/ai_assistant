C4Container

title AI Assistant System - Container Diagram

Person(user, "👤 User", "Interacts via SMS, email")

Boundary(ai_system, "AI Assistant System") {
Container(agent_core_service, "⚙️ Agent Core Service", "Python", "Handles core logic, API (if any), LLM interaction, tool execution, integrations (agent_core/_). Manages scheduled tasks.")
Container(scheduled_tasks_service, "📅 Scheduled Tasks Service", "Python/Celery", "Executes periodic tasks defined in schedule_tools/_.py (Expenses, ToDo, etc.).")
SystemDb(db, "💾 Database", "PostgreSQL", "Stores user data, state, schedules, expenses, notes, etc.")
}

Boundary(external, "External Systems") {
System_Ext(twilio, "📱 Twilio", "SMS communication")
System_Ext(outlook, "📧 Outlook", "Email service")
System_Ext(calendar, "📅 Outlook Calendar", "Schedules and events")
System_Ext(obsidian, "📓 Obsidian", "Knowledge management")
System_Ext(budget, "💰 Budget App", "Budget tracking")
System_Ext(gemini, "✨ Gemini LLM", "Core LLM")
System_Ext(wikipedia, "🌐 Wikipedia", "Information lookup")
}

Rel(user, agent_core_service, "Interacts with (e.g., via SMS/Twilio)")
Rel(agent_core_service, db, "Reads/writes core data to")
Rel(agent_core_service, twilio, "Sends/Receives SMS via")
Rel(agent_core_service, outlook, "Sends/Receives Email via")
Rel(agent_core_service, calendar, "Manages Calendar via")
Rel(agent_core_service, obsidian, "Manages Notes via")
Rel(agent_core_service, budget, "Reads Budget via")
Rel(agent_core_service, wikipedia, "Searches Wikipedia via")
Rel(agent_core_service, gemini, "Uses LLM via")
Rel(agent_core_service, scheduled_tasks_service, "Triggers / Manages")

Rel(scheduled_tasks_service, db, "Reads/Writes task data")
Rel(scheduled_tasks_service, agent_core_service, "Uses Tools / LLM via")
Rel(scheduled_tasks_service, outlook, "Sends reports/notifications via")
Rel(scheduled_tasks_service, calendar, "Updates/Reads calendar for planning")
Rel(scheduled_tasks_service, budget, "Reads budget data for reporting")
