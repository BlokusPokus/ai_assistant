sequenceDiagram
participant U as 🧑‍💻 User
participant Core as AgentCore
participant Graph as LangGraphRunner
participant Mem as MemoryInterface
participant LLM as LLMPlanner
participant Tools as ToolRegistry
participant Log as Logger

    U ->> Core: run(user_input)
    Core ->> Graph: run(user_input)
    Graph ->> Mem: query(user_input)
    Mem -->> Graph: memory_context
    Graph ->> LLM: choose_action(state)
    LLM -->> Graph: ToolCall or FinalAnswer

    alt If FinalAnswer
        Graph ->> Log: log_interaction()
        Graph -->> Core: return FinalAnswer
        Core -->> U: final response
    else If ToolCall
        loop Tool execution (max 5 iterations)
            Graph ->> Tools: run_tool(tool_name, args)
            Tools -->> Graph: tool_output
            Graph ->> Mem: add(tool_output, metadata)
            Graph ->> Log: log_interaction()
            Graph ->> LLM: choose_action(updated_state)
            LLM -->> Graph: ToolCall or FinalAnswer

            alt If FinalAnswer
                Graph -->> Core: return FinalAnswer
                Core -->> U: final response
                break
            end
        end

        alt If loop limit reached
            Graph ->> LLM: force_finish(state)
            Graph -->> Core: return fallback response
            Core -->> U: fallback response
        end
    end

    U ->> U: new message

end
