# LTM Optimization Package

## Purpose

This package provides **AI/ML optimization** for Long-Term Memory (LTM). It's the "how to make LTM smarter" layer.

## What This Package Does

- **Active Learning**: Learns from user interactions to improve memory creation
- **Pattern Recognition**: Identifies communication styles and preferences
- **Smart Retrieval**: Uses AI to find the most relevant memories
- **Memory Consolidation**: Intelligently merges and organizes memories
- **Context Optimization**: Formats memories efficiently for agent injection

## Relationship to LTM Tool

- **LTM Tool** (`tools/ltm/`): "How to use LTM" - provides the interface
- **This package** (`memory/ltm_optimization/`): "How to make LTM smarter" - provides the intelligence

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    LTM Optimization Package                │
│                    (AI/ML Intelligence Layer)              │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Learning Manager│  │ Smart Retriever │  │  Context    │ │
│  │                 │  │                 │  │  Optimizer  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│           │                      │                │        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Pattern Learner │  │ Memory          │  │ Lifecycle   │ │
│  │                 │  │ Consolidator    │  │ Manager     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│           │                      │                │        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Preference      │  │ Configuration   │  │ Statistics  │ │
│  │ Learner         │  │                 │  │ & Analytics │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└────────────────────────────────────────────────────────────┘
```

## Import Pattern

- **For tool usage**: Import from `tools.ltm`
- **For optimization**: Import from `memory.ltm_optimization`
- **For basic operations**: Use the tool interface

## Key Components

### 1. **LTMLearningManager** (`learning_manager.py`)

Main orchestrator for active learning and memory creation.

```python
from personal_assistant.memory.ltm_optimization import LTMLearningManager

learning_manager = LTMLearningManager()

# Learn from user interaction
created_memories = await learning_manager.learn_from_interaction(
    user_id="user123",
    user_input="I prefer to work in the morning",
    agent_response="I understand you prefer morning work",
    tool_result="Successfully created note"
)
```

### 2. **ConversationPatternLearner** (`pattern_learner.py`)

Learns patterns from conversation history.

```python
from personal_assistant.memory.ltm_optimization import ConversationPatternLearner

pattern_learner = ConversationPatternLearner()

# Learn patterns from conversation
pattern_memories = await pattern_learner.learn_patterns(
    user_id="user123",
    user_input="Please can you help me with this?",
    agent_response="Of course, I'd be happy to help!"
)
```

### 3. **UserPreferenceLearner** (`preference_learner.py`)

Learns user preferences from interactions and tool usage.

```python
from personal_assistant.memory.ltm_optimization import UserPreferenceLearner

preference_learner = UserPreferenceLearner()

# Learn preferences
preference_memories = await preference_learner.learn_preferences(
    user_id="user123",
    user_input="Create a note for me",
    agent_response="I've created your note",
    tool_result="Successfully created note 'Meeting Notes'"
)
```

### 4. **SmartLTMRetriever** (`smart_retriever.py`)

Provides intelligent memory retrieval with relevance scoring.

```python
from personal_assistant.memory.ltm_optimization import SmartLTMRetriever

retriever = SmartLTMRetriever()

# Get relevant memories
relevant_memories = await retriever.get_relevant_memories(
    user_id="user123",
    context="I need help with note creation",
    limit=5
)
```

### 5. **ContextOptimizationManager** (`context_optimizer.py`)

Optimizes LTM context for injection into the agent.

```python
from personal_assistant.memory.ltm_optimization import ContextOptimizationManager

optimizer = ContextOptimizationManager()

# Optimize context for injection
optimized_context = await optimizer.optimize_ltm_context(
    memories=relevant_memories,
    user_input="I need help with note creation",
    max_length=800
)
```

### 6. **MemoryConsolidator** (`memory_consolidator.py`)

Consolidates related and redundant memories.

```python
from personal_assistant.memory.ltm_optimization import MemoryConsolidator

consolidator = MemoryConsolidator()

# Consolidate user memories
consolidated = await consolidator.consolidate_user_memories("user123")
```

### 7. **MemoryLifecycleManager** (`lifecycle_manager.py`)

Manages memory lifecycle including aging, archiving, and deletion.

```python
from personal_assistant.memory.ltm_optimization import MemoryLifecycleManager

lifecycle_manager = MemoryLifecycleManager()

# Manage memory lifecycle
report = await lifecycle_manager.manage_memory_lifecycle("user123")

# Get memory statistics
stats = await lifecycle_manager.get_memory_statistics("user123")
```

### 8. **LTMConfig** (`config.py`)

Configuration settings for the entire LTM optimization system.

```python
from personal_assistant.memory.ltm_optimization import LTMConfig

config = LTMConfig(
    min_importance_for_memory=3,
    max_memories_per_interaction=5,
    memory_creation_confidence_threshold=0.6
)
```

## Configuration

The `LTMConfig` class provides extensive configuration options:

```python
config = LTMConfig(
    # Memory creation thresholds
    min_importance_for_memory=3,
    max_memories_per_interaction=5,
    memory_creation_confidence_threshold=0.6,

    # Memory consolidation settings
    tag_similarity_threshold=0.7,
    content_similarity_threshold=0.6,
    min_group_size_for_consolidation=2,

    # Memory lifecycle settings
    memory_aging_days=30,
    memory_archiving_days=60,
    low_importance_threshold=3,

    # Retrieval settings
    max_candidate_memories=20,
    max_retrieved_memories=5,
    min_importance_for_retrieval=3,

    # Context optimization settings
    max_context_length=1000,
    max_memories_per_type=3
)
```

## Usage Examples

### Basic Integration

```python
from personal_assistant.memory.ltm_optimization import (
    LTMLearningManager,
    SmartLTMRetriever,
    ContextOptimizationManager
)

# Initialize components
learning_manager = LTMLearningManager()
retriever = SmartLTMRetriever()
optimizer = ContextOptimizationManager()

# Learn from interaction
await learning_manager.learn_from_interaction(
    user_id="user123",
    user_input="I prefer morning meetings",
    agent_response="I'll schedule your meetings in the morning",
    tool_result="Successfully scheduled meeting"
)

# Get relevant context
memories = await retriever.get_relevant_memories(
    user_id="user123",
    context="Schedule a meeting for me",
    limit=5
)

# Optimize context for injection
context = await optimizer.optimize_ltm_context(
    memories=memories,
    user_input="Schedule a meeting for me",
    max_length=800
)
```

### Advanced Usage

```python
from personal_assistant.memory.ltm_optimization import (
    LTMLearningManager,
    MemoryConsolidator,
    MemoryLifecycleManager
)

# Initialize with custom config
config = LTMConfig(
    min_importance_for_memory=5,
    max_memories_per_interaction=10
)

learning_manager = LTMLearningManager(config)
consolidator = MemoryConsolidator(config)
lifecycle_manager = MemoryLifecycleManager(config)

# Comprehensive memory management
async def manage_user_memories(user_id: str):
    # Learn from recent interactions
    created = await learning_manager.learn_from_interaction(
        user_id=user_id,
        user_input="This is very important to remember",
        agent_response="I will remember this important information",
        tool_result="Success"
    )

    # Consolidate related memories
    consolidated = await consolidator.consolidate_user_memories(user_id)

    # Manage lifecycle
    lifecycle_report = await lifecycle_manager.manage_memory_lifecycle(user_id)

    # Get statistics
    stats = await lifecycle_manager.get_memory_statistics(user_id)

    return {
        "created": len(created),
        "consolidated": len(consolidated),
        "lifecycle": lifecycle_report,
        "statistics": stats
    }
```

## Testing

Run the basic test to verify all components work:

```bash
cd src/personal_assistant/memory/ltm_optimization
python test_basic.py
```

## Expected Results

### Performance Improvements

- **Memory Creation**: 5-10x increase in relevant memory creation
- **Retrieval Quality**: 80%+ improvement in context relevance
- **Storage Efficiency**: 30-50% reduction in redundant memories

### Quality Improvements

- **Active Learning**: System learns from every interaction
- **Pattern Recognition**: Identifies user preferences and habits
- **Memory Consolidation**: Reduces redundancy and improves insights

### User Experience Improvements

- **Personalization**: Responses reflect learned preferences
- **Consistency**: System remembers user patterns and preferences
- **Efficiency**: Faster, more relevant responses

## Next Steps

1. **Test the components** using the provided test file
2. **Integrate with your agent system** by updating the LTM manager
3. **Customize configuration** based on your specific needs
4. **Monitor performance** and adjust thresholds as needed

This package transforms your LTM system from a passive storage system to an **active learning system** that continuously improves and provides increasingly relevant context to your agent.

## Clear Separation of Concerns

- **`tools/ltm/`**: "How to use LTM" - provides the tool interface
- **`memory/ltm_optimization/`**: "How to make LTM smarter" - provides the AI intelligence
- **Together**: They create a powerful, intelligent LTM system
