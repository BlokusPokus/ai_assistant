sequenceDiagram
actor User
participant AgentCore
participant LangGraphRunner
participant LLMPlanner
participant PromptBuilder
participant LLMClient
participant ToolRegistry

    User->>AgentCore: run(user_input)
    AgentCore->>LangGraphRunner: run(user_input)

    LangGraphRunner->>LangGraphRunner: create AgentState(user_input)

    loop Until FinalAnswer or LOOP_LIMIT
        LangGraphRunner->>LLMPlanner: choose_action(state)

        LLMPlanner->>PromptBuilder: build(state)
        PromptBuilder-->>LLMPlanner: prompt

        LLMPlanner->>ToolRegistry: get_schema()
        ToolRegistry-->>LLMPlanner: available_tools

        LLMPlanner->>LLMClient: complete(prompt, tools)
        LLMClient-->>LLMPlanner: response

        LLMPlanner->>LLMClient: parse_response(response)
        LLMClient-->>LLMPlanner: action

        LLMPlanner-->>LangGraphRunner: action

        alt action is ToolCall
            LangGraphRunner->>ToolRegistry: run_tool(name, args)
            ToolRegistry-->>LangGraphRunner: result
            LangGraphRunner->>LangGraphRunner: state.add_tool_result(action, result)
        else action is FinalAnswer
            LangGraphRunner-->>AgentCore: final_response
            AgentCore-->>User: final_response
        end
    end

    opt If LOOP_LIMIT reached
        LangGraphRunner->>LLMPlanner: force_finish(state)
        LLMPlanner-->>LangGraphRunner: forced_response
        LangGraphRunner-->>AgentCore: forced_response
        AgentCore-->>User: forced_response
    end
