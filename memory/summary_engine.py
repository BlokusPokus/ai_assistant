"""
Handles fallback summarization logic.
"""

from memory.memory_storage import InMemoryStorage


def generate_summary(messages: list) -> str:
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


def summarize_and_archive(conversation_id: str) -> str:
    """
    Generate and save a summary for a conversation.

    Args:
        conversation_id (str): ID of the conversation

    Returns:
        str: The generated summary
    """
    storage = InMemoryStorage()
    # Fetch conversation data using the storage interface
    conversation_data = storage.query(conversation_id, "fetch_conversation")
    # Generate summary
    summary = generate_summary(conversation_data)
    # Store the summary
    storage.add(conversation_id, summary, {"type": "summary"})
    return summary
