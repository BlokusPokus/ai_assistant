"""
Email extraction utilities for calendar tools.

This module provides functions to extract email addresses from user input
and format them for calendar event creation.
"""

import re
from typing import List, Tuple


def extract_emails_from_text(text: str) -> List[str]:
    """
    Extract email addresses from text input.
    
    Args:
        text: Input text that may contain email addresses
        
    Returns:
        List of found email addresses
    """
    if not text:
        return []
    
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Find all email addresses
    emails = re.findall(email_pattern, text)
    
    # Remove duplicates while preserving order
    unique_emails = []
    for email in emails:
        if email not in unique_emails:
            unique_emails.append(email)
    
    return unique_emails


def extract_event_info_with_emails(text: str) -> Tuple[str, List[str]]:
    """
    Extract event information and email addresses from user input.
    
    Args:
        text: User input text (e.g., "Climbing date camillecouture10@gmail.com")
        
    Returns:
        Tuple of (cleaned_event_name, list_of_emails)
    """
    if not text:
        return "", []
    
    # Extract emails first
    emails = extract_emails_from_text(text)
    
    # Clean the event name by removing email addresses
    cleaned_text = text
    for email in emails:
        # Remove the email and any surrounding punctuation/whitespace
        cleaned_text = re.sub(rf'\s*{re.escape(email)}\s*', ' ', cleaned_text)
    
    # Clean up extra whitespace and punctuation
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    cleaned_text = re.sub(r'[,\s]*$', '', cleaned_text)  # Remove trailing commas/whitespace
    
    return cleaned_text, emails


def format_attendees_for_calendar(emails: List[str]) -> str:
    """
    Format email addresses for calendar tool input.
    
    Args:
        emails: List of email addresses
        
    Returns:
        Comma-separated string of emails for calendar tool
    """
    if not emails:
        return ""
    
    return ','.join(emails)


def parse_calendar_request(text: str) -> Tuple[str, List[str]]:
    """
    Parse calendar request text to extract event name and attendees.
    
    Args:
        text: User input like "Hey can you book a calendar event for tomorrow at 12 with Camille, event name: Climbing date camillecouture10@gmail.com"
        
    Returns:
        Tuple of (event_name, list_of_emails)
    """
    if not text:
        return "", []
    
    # Look for event name patterns
    event_patterns = [
        r'event name:\s*([^,]+)',
        r'event:\s*([^,]+)',
        r'name:\s*([^,]+)',
        r'title:\s*([^,]+)'
    ]
    
    event_name = ""
    for pattern in event_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            event_name = match.group(1).strip()
            break
    
    # If no explicit event name pattern found, try to extract from the end
    if not event_name:
        # Look for text that might be an event name (after "with" or similar)
        with_match = re.search(r'with\s+[^,]+,\s*([^,]+?)(?:\s*$|\.)', text, re.IGNORECASE)
        if with_match:
            event_name = with_match.group(1).strip()
    
    # Extract emails from the entire text
    emails = extract_emails_from_text(text)
    
    # If we found an event name, clean it of emails
    if event_name:
        cleaned_event_name, _ = extract_event_info_with_emails(event_name)
        return cleaned_event_name, emails
    
    # If no event name found, try to extract from the whole text
    return "", emails


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_cases = [
        "Hey can you book a calendar event for tomorrow at 12 with Camille, event name: Climbing date camillecouture10@gmail.com",
        "Create meeting with john@example.com and jane@test.org",
        "Schedule lunch event name: Team Lunch sarah@company.com, mike@company.com",
        "Book appointment with doctor@clinic.com",
        "No emails here, just text"
    ]
    
    for test_case in test_cases:
        event_name, emails = parse_calendar_request(test_case)
        print(f"Input: {test_case}")
        print(f"Event: '{event_name}'")
        print(f"Emails: {emails}")
        print(f"Formatted: '{format_attendees_for_calendar(emails)}'")
        print("-" * 50)
