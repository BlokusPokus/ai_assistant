"""
Text cleaning utilities for removing problematic Unicode characters.

This module provides functions to clean text of invisible Unicode control characters
that can cause issues with text processing, logging, and display.
"""

import re
import unicodedata


def clean_unicode_control_chars(text: str) -> str:
    """
    Remove invisible Unicode control characters from text.

    Args:
        text (str): Input text that may contain control characters

    Returns:
        str: Cleaned text with control characters removed
    """
    if not text:
        return text

    # Remove zero-width characters and other problematic Unicode
    # \u200b - Zero-width space
    # \u200c - Zero-width non-joiner
    # \u200d - Zero-width joiner
    # \u200e - Left-to-right mark
    # \u200f - Right-to-left mark
    # \u2060 - Word joiner
    # \u2061 - Function application
    # \u2062 - Invisible times
    # \u2063 - Invisible separator
    # \u2064 - Invisible plus
    # \u2066 - Left-to-right isolate
    # \u2067 - Right-to-left isolate
    # \u2068 - First strong isolate
    # \u2069 - Pop directional isolate
    # \u206a - Inhibit symmetric swapping
    # \u206b - Activate symmetric swapping
    # \u206c - Inhibit arabic form shaping
    # \u206d - Activate arabic form shaping
    # \u206e - National digit shapes
    # \u206f - Nominal digit shapes

    # Pattern to match zero-width and control characters
    control_chars_pattern = re.compile(
        r"[\u200b\u200c\u200d\u200e\u200f\u2060\u2061\u2062\u2063\u2064\u2066\u2067\u2068\u2069\u206a\u206b\u206c\u206d\u206e\u206f]"
    )

    # Remove the control characters
    cleaned_text = control_chars_pattern.sub("", text)

    # Also remove other control characters (C0 and C1 control codes)
    cleaned_text = "".join(
        char for char in cleaned_text if not unicodedata.category(char).startswith("C")
    )

    return cleaned_text


def clean_text_for_logging(text: str) -> str:
    """
    Clean text specifically for logging purposes.

    Args:
        text (str): Input text that may contain problematic characters

    Returns:
        str: Cleaned text safe for logging
    """
    if not text:
        return text

    # First clean Unicode control characters
    cleaned = clean_unicode_control_chars(text)

    # Also remove other problematic characters for logging
    # Remove null bytes
    cleaned = cleaned.replace("\x00", "")

    # Remove other control characters that might cause issues
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

    # Limit length for logging
    if len(cleaned) > 1000:
        cleaned = cleaned[:1000] + "... [truncated]"

    return cleaned


def clean_html_content(html_content: str) -> str:
    """
    Clean HTML content and remove problematic Unicode characters.

    Args:
        html_content (str): HTML content to clean

    Returns:
        str: Cleaned text content
    """
    if not html_content:
        return ""

    import re

    # Remove HTML tags
    clean_text = re.sub(r"<[^>]+>", "", html_content)

    # Remove CSS styles
    clean_text = re.sub(r"<style[^>]*>.*?</style>", "", clean_text, flags=re.DOTALL)

    # Remove JavaScript
    clean_text = re.sub(r"<script[^>]*>.*?</script>", "", clean_text, flags=re.DOTALL)

    # Remove HTML entities
    clean_text = clean_text.replace("&nbsp;", " ")
    clean_text = clean_text.replace("&amp;", "&")
    clean_text = clean_text.replace("&lt;", "<")
    clean_text = clean_text.replace("&gt;", ">")
    clean_text = clean_text.replace("&quot;", '"')

    # Remove Unicode control characters
    clean_text = clean_unicode_control_chars(clean_text)

    # Remove extra whitespace and normalize
    clean_text = re.sub(r"\s+", " ", clean_text)
    clean_text = clean_text.strip()

    # Limit length to prevent context explosion
    if len(clean_text) > 2000:
        clean_text = clean_text[:2000] + "... [content truncated]"

    return clean_text
