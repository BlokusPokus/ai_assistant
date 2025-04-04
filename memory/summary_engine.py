"""
Handles fallback summarization logic.
"""
from datetime import datetime
from database.session import AsyncSessionLocal
from database.models.memory_chunk import MemoryChunk
from database.crud.utils import add_record, filter_by


async def generate_summary(messages: list) -> str:
    """
    Generate a summary from a message list.

    Args: 
        messages (list): List of message dicts

    Returns:
        str: Summarized string
    """
    # Example logic: Concatenate the first sentence of each message
    summary = []
    for message in messages:
        # Assuming each message is a dict with a 'text' key
        text = message.get('text', '')
        # Extract the first sentence
        first_sentence = text.split('.')[0]
        summary.append(first_sentence)

    # Join the sentences to form the summary
    return '. '.join(summary) + '.'


async def summarize_and_archive(conversation_id: str) -> str:
    """
    Generate and save a summary for a conversation.

    Args:
        conversation_id (str): ID of the conversation

    Returns:
        str: The generated summary
    """
    async with AsyncSessionLocal() as session:
        # Fetch conversation messages
        records = await filter_by(
            session,
            MemoryChunk,
            meta_data__conversation_id=conversation_id,
            meta_data__type="message"
        )

        # Generate summary
        messages = [{"text": record.content} for record in records]
        summary = await generate_summary(messages)

        # Store the summary
        data = {
            "content": summary,
            "meta_data": {
                "conversation_id": conversation_id,
                "type": "summary",
                "created_at": datetime.utcnow().isoformat()
            }
        }
        await add_record(session, MemoryChunk, data)

        return summary
