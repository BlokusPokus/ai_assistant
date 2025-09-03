"""
AI Tag Validator

This module provides robust validation for AI-generated tags to ensure they
conform to the predefined tag list and database requirements.
"""

import logging
from typing import List, Optional, Tuple

from ..config.logging_config import get_logger
from ..constants.tags import LTM_TAGS, get_tag_suggestions, validate_tags

logger = get_logger("ai_tag_validator")


class AITagValidator:
    """Validates and corrects AI-generated tags"""

    def __init__(self):
        self.allowed_tags = set(LTM_TAGS)
        logger.info(
            f"Initialized AI tag validator with {len(self.allowed_tags)} allowed tags"
        )

    def validate_and_correct_tags(
        self, ai_generated_tags: str, content: str = "", context: str = ""
    ) -> Tuple[List[str], List[str], str]:
        """
        Validate and correct AI-generated tags.

        Args:
            ai_generated_tags: Comma-separated string of tags from AI
            content: The content being tagged (for context)
            context: Additional context

        Returns:
            Tuple of (valid_tags, invalid_tags, correction_explanation)
        """
        try:
            # Parse the AI response
            if not ai_generated_tags or not ai_generated_tags.strip():
                logger.warning("AI generated empty tags, using fallback")
                return (
                    self._get_fallback_tags(content),
                    [],
                    "Used fallback tags due to empty AI response",
                )

            # Clean and split the tags
            raw_tags = [
                tag.strip().lower()
                for tag in ai_generated_tags.split(",")
                if tag.strip()
            ]

            if not raw_tags:
                logger.warning(
                    "AI generated no valid tags after parsing, using fallback"
                )
                return (
                    self._get_fallback_tags(content),
                    [],
                    "Used fallback tags due to no valid tags after parsing",
                )

            logger.info(f"AI generated tags: {raw_tags}")

            # Validate tags using the existing validation system
            valid_tags, invalid_tags = validate_tags(
                raw_tags, enable_smart_fallback=True
            )

            # If we have invalid tags, try to correct them
            if invalid_tags:
                logger.warning(f"AI generated invalid tags: {invalid_tags}")
                correction_explanation = f"Corrected invalid tags: {invalid_tags}"

                # Try to get suggestions for invalid tags
                for invalid_tag in invalid_tags:
                    suggestions = get_tag_suggestions(f"{invalid_tag} {content}")
                    if suggestions:
                        logger.info(
                            f"Found suggestions for '{invalid_tag}': {suggestions}"
                        )
                        # Add the first suggestion if it's not already in valid_tags
                        for suggestion in suggestions:
                            if (
                                suggestion not in valid_tags
                                and suggestion in self.allowed_tags
                            ):
                                valid_tags.append(suggestion)
                                break
            else:
                correction_explanation = "All AI-generated tags were valid"

            # Ensure we have at least one tag
            if not valid_tags:
                logger.warning("No valid tags after correction, using fallback")
                return (
                    self._get_fallback_tags(content),
                    invalid_tags,
                    "Used fallback tags due to no valid tags after correction",
                )

            # Remove duplicates while preserving order
            final_tags = list(dict.fromkeys(valid_tags))

            logger.info(f"Final validated tags: {final_tags}")
            return final_tags, invalid_tags, correction_explanation

        except Exception as e:
            logger.error(f"Error validating AI tags: {e}")
            return (
                self._get_fallback_tags(content),
                [],
                f"Error during validation: {str(e)}",
            )

    def _get_fallback_tags(self, content: str) -> List[str]:
        """Get fallback tags based on content analysis"""
        try:
            suggestions = get_tag_suggestions(content)
            if suggestions:
                return suggestions[:3]  # Return up to 3 suggestions
            else:
                return ["general"]  # Ultimate fallback
        except Exception as e:
            logger.error(f"Error getting fallback tags: {e}")
            return ["general"]

    def validate_single_tag(self, tag: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a single tag.

        Args:
            tag: The tag to validate

        Returns:
            Tuple of (is_valid, corrected_tag)
        """
        tag = tag.strip().lower()

        if tag in self.allowed_tags:
            return True, tag

        # Try to find a similar tag
        valid_tags, invalid_tags = validate_tags([tag], enable_smart_fallback=True)

        if valid_tags:
            return True, valid_tags[0]

        return False, None

    def get_tag_suggestions_for_content(self, content: str) -> List[str]:
        """Get tag suggestions based on content"""
        try:
            suggestions = get_tag_suggestions(content)
            # Filter to only include allowed tags
            return [tag for tag in suggestions if tag in self.allowed_tags]
        except Exception as e:
            logger.error(f"Error getting tag suggestions: {e}")
            return ["general"]

    def format_tag_validation_report(
        self,
        original_tags: str,
        valid_tags: List[str],
        invalid_tags: List[str],
        correction_explanation: str,
    ) -> str:
        """Format a report of tag validation results"""
        report = f"""
Tag Validation Report:
- Original AI tags: {original_tags}
- Valid tags: {valid_tags}
- Invalid tags: {invalid_tags}
- Correction: {correction_explanation}
- Final tags used: {valid_tags}
"""
        return report.strip()


# Global instance for easy access
ai_tag_validator = AITagValidator()


def validate_ai_generated_tags(
    ai_generated_tags: str, content: str = "", context: str = ""
) -> Tuple[List[str], List[str], str]:
    """
    Convenience function to validate AI-generated tags.

    Args:
        ai_generated_tags: Comma-separated string of tags from AI
        content: The content being tagged (for context)
        context: Additional context

    Returns:
        Tuple of (valid_tags, invalid_tags, correction_explanation)
    """
    return ai_tag_validator.validate_and_correct_tags(
        ai_generated_tags, content, context
    )
