sequenceDiagram
actor User
participant AgentCore
participant LangGraphRunner
participant MemoryComponent
participant LLMPlanner
participant PromptBuilder
participant LLMClient
participant ToolRegistry

    User->>AgentCore: run(user_input)
    AgentCore->>LangGraphRunner: run(user_input)

    LangGraphRunner->>LangGraphRunner: create AgentState(user_input)
    LangGraphRunner->>MemoryComponent: query(user_id, user_input)
    MemoryComponent-->>LangGraphRunner: memory_context
    LangGraphRunner->>LangGraphRunner: state.update(memory_context)

    %% Planner gets tool schemas once if needed
    opt Tools needed for planning
        LangGraphRunner->>LLMPlanner: get_tool_schemas()
        LLMPlanner->>ToolRegistry: get_schemas()
        ToolRegistry-->>LLMPlanner: tool_schemas
        LLMPlanner-->>LangGraphRunner: tool_schemas
    end

    loop Until FinalAnswer or LOOP_LIMIT
        LangGraphRunner->>LLMPlanner: choose_action(state, tool_schemas)

        LLMPlanner->>PromptBuilder: build(state, tool_schemas)
        PromptBuilder-->>LLMPlanner: prompt

        LLMPlanner->>LLMClient: complete(prompt, tool_schemas)
        LLMClient-->>LLMPlanner: llm_response

        LLMPlanner->>LLMPlanner: parse_response(llm_response)
        LLMPlanner-->>LangGraphRunner: action

        alt action is ToolCall
            LangGraphRunner->>ToolRegistry: run_tool(action.name, action.args)
            ToolRegistry-->>LangGraphRunner: result
            LangGraphRunner->>LangGraphRunner: state.add_tool_result(action, result)
            LangGraphRunner->>MemoryComponent: add(user_id, tool_interaction_data)
            MemoryComponent-->>LangGraphRunner: ack
        else action is FinalAnswer
            LangGraphRunner->>MemoryComponent: add(user_id, final_interaction_data)
            MemoryComponent-->>LangGraphRunner: ack
            LangGraphRunner-->>AgentCore: final_response
            AgentCore-->>User: final_response
        end
    end

    opt If LOOP_LIMIT reached
        LangGraphRunner->>LLMPlanner: force_finish(state)
        LLMPlanner-->>LangGraphRunner: forced_response
        LangGraphRunner->>MemoryComponent: add(user_id, loop_limit_interaction_data)
        MemoryComponent-->>LangGraphRunner: ack
        LangGraphRunner-->>AgentCore: forced_response
        AgentCore-->>User: forced_response
    end
