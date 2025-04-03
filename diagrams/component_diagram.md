C4Component

title Agent Core Service - Component Diagram

Container_Boundary(agent_core_boundary, "⚙️ Agent Core Service (agent_core)") {

Component(input_handler, "Input Handler", "Python Module(s)", "Receives external events (e.g., Twilio webhook via communication/twilio_integration) or user commands, routes to CoreLogic")
Component(core_logic, "Core Logic", "Python (core.py, graph_runner.py)", "Orchestrates LLM, tools, and memory based on input")
Component(llm_component, "LLM Component", "Python (llm/_)", "Manages interaction with Gemini (prompting, planning, function calling)")
Component(memory_component, "Memory Component", "Python (memory/_)", "Manages conversation history, state, and DB interaction via DAL")
Component(tools_component, "Tools Component", "Python (tools/_)", "Collection of tools for specific tasks (Calendar, Email, Notes, Expense, Grocery, SMS, Wikipedia, etc.)")
Component(scheduler_config, "Scheduler Config", "Python/Celery Beat", "Defines schedules and triggers TaskDispatcher")
Component(task_dispatcher, "Task Dispatcher", "Celery Client", "Dispatches background tasks (on-demand or scheduled) to the Scheduled Tasks Service")
Component(dal, "Data Access Layer", "Python (memory/_ or dedicated)", "Abstracts database access, used by Memory Component")

}

Container_Boundary(external_deps, "External Dependencies") {
Container_Ext(db, "💾 Database", "PostgreSQL")
Container_Ext(scheduled_tasks_cont, "📅 Scheduled Tasks Service", "Python/Celery Container", "Executes periodic tasks (schedule_tools/\*)")
System_Ext(gemini_ext, "✨ Gemini LLM", "Google Generative AI")
System_Ext(twilio_ext, "📱 Twilio", "SMS communication")
System_Ext(outlook_ext, "📧 Outlook", "Email service")
System_Ext(calendar_ext, "📅 Outlook Calendar", "Schedules and events")
System_Ext(obsidian_ext, "📓 Obsidian", "Knowledge Management")
System_Ext(budget_ext, "💰 Budget App", "Budget tracking")
System_Ext(wikipedia_ext, "🌐 Wikipedia", "Information lookup")
}

Rel(input_handler, core_logic, "Passes user input/events to")
Rel(input_handler, tools_component, "Uses SMS tool (Twilio) for input")

Rel(core_logic, llm_component, "Uses for planning and generation")
Rel(core_logic, memory_component, "Uses to read/write state")
Rel(core_logic, tools_component, "Selects and executes tools")
Rel(core_logic, task_dispatcher, "Dispatches on-demand background tasks via")

Rel(llm_component, gemini_ext, "Sends requests to / Receives responses from")

Rel(memory_component, dal, "Uses to persist/retrieve state")

Rel(tools_component, calendar_ext, "Uses Calendar Tool")
Rel(tools_component, outlook_ext, "Uses Email Tool")
Rel(tools_component, twilio_ext, "Uses SMS Tool")
Rel(tools_component, obsidian_ext, "Uses Notes Tool")
Rel(tools_component, budget_ext, "Uses Expense Tool")
Rel(tools_component, wikipedia_ext, "Uses Wikipedia Tool")

Rel(scheduler_config, task_dispatcher, "Schedules tasks via")

Rel(task_dispatcher, scheduled_tasks_cont, "Dispatches jobs to")

Rel(dal, db, "Executes queries against")
