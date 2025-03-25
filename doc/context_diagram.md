C4Context
title AI Assistant System - System Context

Person(user, "👤 Human User", "Interacts with the assistant via multiple channels")

Boundary(internal, "Internal Systems") {
System(ai, "🤖 AI Assistant System", "Personal automation system that handles scheduling, reminders, expense tracking, and grocery intelligence.")
System(grocery, "🛒 Grocery Extractor System", "Extracts grocery deals from flyers and returns structured data")
}

Boundary(external_systems, "External Systems") {
System_Ext(twilio, "📱 Twilio", "SMS communication platform")
System_Ext(outlook, "📧 Outlook", "Email system used for communication")
System_Ext(calendar, "📅 Outlook Calendar", "Calendar used for managing events and reminders")
System_Ext(obsidian, "📓 Obsidian", "Knowledge management system")
System_Ext(budget, "💰 Budget App","Budget tracking")
}

Rel(user, ai, "Uses")
Rel(ai, twilio, "Sends and receives SMS via")
Rel(ai, outlook, "Sends emails through")
Rel(ai, calendar, "Schedules and reads calendar events")
Rel(ai, obsidian, "Stores and retrieves long-term notes")
Rel(ai, grocery, "Controls and uses for grocery deal extraction")
