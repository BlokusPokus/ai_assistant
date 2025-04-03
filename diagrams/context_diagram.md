C4Context
title AI Assistant System - System Context

Person(user, "👤 Human User", "Interacts with the assistant via multiple channels")

Boundary(internal, "Internal Systems") {
System(ai_assistant, "🤖 AI Assistant System", "Personal automation system based on agent_core and schedule_tools.")
}

Boundary(external_systems, "External Systems") {
System_Ext(twilio, "📱 Twilio", "SMS communication platform (via communication/twilio_integration)")
System_Ext(outlook, "📧 Outlook", "Email system (via agent_core/tools/emails)")
System_Ext(calendar, "📅 Outlook Calendar", "Calendar system (via agent_core/tools/calendar)")
System_Ext(obsidian, "📓 Obsidian", "Knowledge management system (via agent_core/tools/notes)")
System_Ext(budget, "💰 Budget App","Budget tracking (via agent_core/tools/expense)")
System_Ext(wikipedia, "🌐 Wikipedia", "Information lookup (via agent_core/tools/wikipedia)")
System_Ext(gemini, "✨ Gemini LLM", "Core LLM (via agent_core/llm)")
}

Rel(user, ai_assistant, "Uses")
Rel(ai_assistant, twilio, "Sends and receives SMS via")
Rel(ai_assistant, outlook, "Sends/Receives emails via")
Rel(ai_assistant, calendar, "Manages calendar events via")
Rel(ai_assistant, obsidian, "Stores/Retrieves notes via")
Rel(ai_assistant, budget, "Reads budget data via")
Rel(ai_assistant, wikipedia, "Searches via")
Rel(ai_assistant, gemini, "Uses for generation and planning")
