"""
Handles comprehensive summarization logic with tool information and conversation context.
"""

from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import aliased


from ..config.logging_config import get_logger

from ..database.models.memory_metadata import MemoryMetadata
from ..types.state import AgentState

TypeMeta = aliased(MemoryMetadata)
ConvMeta = aliased(MemoryMetadata)

logger = get_logger("memory")


async def generate_summary(messages: list) -> str:
    """
    Generate a summary from a message list (legacy function for backward compatibility).

    Args: 
        messages (list): List of message dicts

    Returns:
        str: Summarized string
    """
    # For backward compatibility, create a basic summary
    summary_parts = []
    for message in messages:
        text = message.get('text', '')
        if text:
            # Extract the first sentence
            first_sentence = text.split('.')[0]
            if first_sentence:
                summary_parts.append(first_sentence)

    return '. '.join(summary_parts) + '.' if summary_parts else ""


# def extract_tool_information(conversation_history: List[Dict]) -> Dict[str, Any]:
#     """
#     Extract tool usage information from conversation history.

#     Args:
#         conversation_history: List of conversation messages

#     Returns:
#         Dict containing tools used and their results
#     """
#     tools_used = []
#     tool_results = {}

#     for message in conversation_history:
#         if message.get("role") == "tool":
#             tool_name = message.get("name", "")
#             tool_content = message.get("content", "")

#             if tool_name and tool_name not in tools_used:
#                 tools_used.append(tool_name)
#                 tool_results[tool_name] = tool_content

#     return {
#         "tools_used": tools_used,
#         "tool_results": tool_results
#     }


# def extract_focus_areas(conversation_history: List[Dict], user_input: str) -> List[str]:
#     """
#     Extract focus areas from conversation based on content analysis.

#     Args:
#         conversation_history: List of conversation messages
#         user_input: The user's input

#     Returns:
#         List of focus areas/topics
#     """
#     focus_areas = set()

#     # Keywords that indicate different focus areas
#     focus_keywords = {
#         "email": ["email", "mail", "inbox", "message", "send", "read"],
#         "calendar": ["calendar", "event", "meeting", "schedule", "appointment"],
#         "communication": ["message", "chat", "text", "call", "contact"],
#         "files": ["file", "document", "folder", "upload", "download"],
#         "search": ["search", "find", "lookup", "query"],
#         "delete": ["delete", "remove", "trash", "archive"],
#         "create": ["create", "new", "add", "make"],
#         "update": ["update", "edit", "modify", "change"]
#     }

#     # Check user input
#     user_input_lower = user_input.lower()
#     for area, keywords in focus_keywords.items():
#         if any(keyword in user_input_lower for keyword in keywords):
#             focus_areas.add(area)

#     # Check conversation history
#     for message in conversation_history:
#         content = message.get("content", "")
#         # Convert content to string if it's not already
#         if not isinstance(content, str):
#             content = str(content)
#         content = content.lower()
#         for area, keywords in focus_keywords.items():
#             if any(keyword in content for keyword in keywords):
#                 focus_areas.add(area)

#     return list(focus_areas)


# def generate_comprehensive_summary(state: AgentState) -> Dict[str, Any]:
#     """
#     Generate a comprehensive summary from AgentState.

#     Args:
#         state: AgentState object containing conversation data

#     Returns:
#         Dict containing comprehensive summary information
#     """
#     try:
#         # Extract tool information
#         tool_info = extract_tool_information(state.conversation_history)

#         # Extract focus areas
#         focus_areas = extract_focus_areas(
#             state.conversation_history, state.user_input)

#         # Create comprehensive summary
#         summary = {
#             "user_input": state.user_input,
#             "memory_context": state.memory_context,
#             "history": state.history,
#             "step_count": state.step_count,
#             "focus": focus_areas,
#             "conversation_history": state.conversation_history,
#             "tools_used": tool_info["tools_used"],

#             "summary_timestamp": datetime.utcnow().isoformat()
#         }

#         return summary
#     except Exception as e:
#         logger.error(f"Error in generate_comprehensive_summary: {str(e)}")
#         logger.error(f"State type: {type(state)}")
#         logger.error(f"State attributes: {dir(state)}")
#         # Return a minimal summary to prevent the error from propagating
#         return {
#             "user_input": getattr(state, 'user_input', ''),
#             "memory_context": getattr(state, 'memory_context', []),
#             "history": getattr(state, 'history', []),
#             "step_count": getattr(state, 'step_count', 0),
#             "focus": getattr(state, 'focus', []),
#             "conversation_history": getattr(state, 'conversation_history', []),
#             "tools_used": [],
#             "tool_results": {},
#             "last_tool_result": None,
#             "summary_timestamp": datetime.utcnow().isoformat(),
#             "error": f"Summary generation failed: {str(e)}"
#         }


# async def summarize_and_archive(conversation_id: str) -> str:
#     """
#     Generate and save a comprehensive summary for a conversation.

#     Args:
#         conversation_id (str): ID of the conversation

#     Returns:
#         str: The generated summary JSON string
#     """
#     async with AsyncSessionLocal() as session:
#         # Fetch conversation messages using proper joins
#         stmt = (
#             select(MemoryChunk)
#             .join(MemoryMetadata, MemoryMetadata.chunk_id == MemoryChunk.id)
#             .where(
#                 MemoryMetadata.key == "conversation_id",
#                 MemoryMetadata.value == conversation_id
#             )
#             .order_by(MemoryChunk.created_at)
#         )
#         result = await session.execute(stmt)
#         records = result.scalars().all()

#         if not records:
#             logger.warning(
#                 f"No records found for conversation {conversation_id}")
#             return ""

#         # Try to reconstruct AgentState from the records
#         try:
#             # Look for state records first
#             state_stmt = (
#                 select(MemoryChunk)
#                 .join(MemoryMetadata, MemoryMetadata.chunk_id == MemoryChunk.id)
#                 .where(
#                     MemoryMetadata.key == "conversation_id",
#                     MemoryMetadata.value == conversation_id,
#                     MemoryMetadata.key == "type",
#                     MemoryMetadata.value == "state"
#                 )
#                 .order_by(desc(MemoryChunk.created_at))
#                 .limit(1)
#             )
#             state_result = await session.execute(state_stmt)
#             state_chunk = state_result.scalar_one_or_none()

#             if state_chunk and state_chunk.content:
#                 # Parse the state from JSON
#                 state_data = json.loads(state_chunk.content)
#                 state = AgentState.from_dict(state_data)

#                 # Generate comprehensive summary
#                 summary_data = generate_comprehensive_summary(state)
#                 summary_json = json.dumps(summary_data, indent=2)

#                 logger.info(
#                     f"Generated comprehensive summary for conversation {conversation_id}")
#                 return summary_json
#             else:
#                 # Fallback to basic summary
#                 messages = [{"text": record.content} for record in records]
#                 summary = await generate_summary(messages)
#                 logger.info(
#                     f"Generated basic summary for conversation {conversation_id}")
#                 return summary

#         except Exception as e:
#             logger.error(
#                 f"Error generating summary for conversation {conversation_id}: {e}")
#             # Fallback to basic summary
#             messages = [{"text": record.content} for record in records]
#             summary = await generate_summary(messages)
#             return summary


# async def store_comprehensive_summary(user_id: str, conversation_id: str, summary_data: Dict[str, Any]) -> None:
#     """
#     Store or update a comprehensive summary with all conversation information.

#     Args:
#         user_id: User ID
#         conversation_id: Conversation ID
#         summary_data: Comprehensive summary data dictionary
#     """
#     async with AsyncSessionLocal() as session:
#         # Convert user_id string to int
#         user_id_int = int(user_id)

#         # Try to find an existing summary chunk for this user and conversation
#         stmt = (
#             select(MemoryChunk)
#             .join(TypeMeta, TypeMeta.chunk_id == MemoryChunk.id)
#             .join(ConvMeta, ConvMeta.chunk_id == MemoryChunk.id)
#             .where(
#                 MemoryChunk.user_id == user_id_int,
#                 TypeMeta.key == "type",
#                 TypeMeta.value == "summary",
#                 ConvMeta.key == "conversation_id",
#                 ConvMeta.value == conversation_id
#             )
#             .order_by(desc(MemoryChunk.created_at))
#             .limit(1)
#         )
#         result = await session.execute(stmt)
#         chunk = result.scalar_one_or_none()

#         if chunk:
#             # Update the existing chunk
#             chunk.content = json.dumps(summary_data, indent=2)
#             chunk.created_at = datetime.utcnow()
#             await session.commit()
#             logger.info(
#                 f"Updated comprehensive summary for user {user_id}, conversation {conversation_id}")
#         else:
#             # Create memory chunk with comprehensive summary
#             chunk_data = {
#                 "user_id": user_id_int,
#                 "content": json.dumps(summary_data, indent=2),
#                 "created_at": datetime.utcnow()
#             }
#             chunk = await add_record(session, MemoryChunk, chunk_data)

#             # Add metadata entries
#             metadata_entries = [
#                 {"chunk_id": chunk.id, "key": "type", "value": "summary"},
#                 {"chunk_id": chunk.id, "key": "created_at",
#                     "value": datetime.utcnow().isoformat()},
#                 {"chunk_id": chunk.id, "key": "summary_version",
#                     "value": "comprehensive"},
#                 {"chunk_id": chunk.id, "key": "conversation_id",
#                     "value": conversation_id}
#             ]

#             for entry in metadata_entries:
#                 await add_record(session, MemoryMetadata, entry)

#             # Generate RAG embeddings for the summary chunk
#             try:
#                 logger.info(
#                     f"🧠 Generating RAG embeddings for summary chunk {chunk.id}")
#                 await embed_and_index(
#                     document=chunk.content,
#                     metadata={
#                         "user_id": user_id,
#                         "chunk_id": chunk.id,
#                         "conversation_id": conversation_id,
#                         "type": "summary",
#                         "source": "summary_engine"
#                     }
#                 )
#                 logger.info(
#                     f"✅ RAG embeddings generated for summary chunk {chunk.id}")
#             except Exception as e:
#                 logger.warning(
#                     f"⚠️ Failed to generate RAG embeddings for summary chunk {chunk.id}: {e}")
#                 # Continue without embeddings - system will still work

#             logger.info(
#                 f"Stored comprehensive summary for user {user_id}, conversation {conversation_id}")
