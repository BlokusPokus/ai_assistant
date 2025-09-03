"""
Feature Flags for Task 053: Database Schema Redesign

This module provides a centralized feature flag system to control the activation
of new features, enabling gradual rollout and A/B testing capabilities.
"""

import os
from typing import Any, Dict

from ..config.logging_config import get_logger

logger = get_logger("feature_flags")

# Feature flag definitions
FEATURE_FLAGS = {
    # Task 053: Database Schema Redesign
    "USE_NORMALIZED_STORAGE": {
        "default": True,  # Changed to True - use new storage by default
        "description": "Use new normalized database schema instead of JSON blobs",
        "env_var": "USE_NORMALIZED_STORAGE",
        "type": "boolean",
    },
    "NORMALIZED_STORAGE_FALLBACK": {
        "default": False,  # Changed to False - no fallback needed
        "description": "Fallback to old storage if normalized storage fails",
        "env_var": "NORMALIZED_STORAGE_FALLBACK",
        "type": "boolean",
    },
    "NORMALIZED_STORAGE_LOGGING": {
        "default": True,
        "description": "Enable detailed logging for normalized storage operations",
        "env_var": "NORMALIZED_STORAGE_LOGGING",
        "type": "boolean",
    },
    # Future feature flags can be added here
    "ENABLE_ADAPTIVE_CONTEXT_SIZING": {
        "default": False,
        "description": "Enable dynamic context sizing based on input complexity",
        "env_var": "ENABLE_ADAPTIVE_CONTEXT_SIZING",
        "type": "boolean",
    },
    "ENABLE_CONTEXT_QUALITY_VALIDATION": {
        "default": True,
        "description": "Enable context quality validation before LLM injection",
        "env_var": "ENABLE_CONTEXT_QUALITY_VALIDATION",
        "type": "boolean",
    },
}


class FeatureFlagManager:
    """
    Centralized feature flag management system.

    This class provides methods to check feature flags, with support for:
    - Environment variable overrides
    - Default values
    - Type validation
    - Logging and monitoring
    """

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._initialized = False

    def _initialize(self):
        """Initialize the feature flag manager and load all flags."""
        if self._initialized:
            return

        logger.info("🔧 Initializing feature flag manager...")

        for flag_name, flag_config in FEATURE_FLAGS.items():
            value = self._get_flag_value(flag_name, flag_config)
            self._cache[flag_name] = value

            logger.info(
                f"🚩 Feature flag '{flag_name}': {value} ({flag_config['description']})"
            )

        self._initialized = True
        logger.info("✅ Feature flag manager initialized")

    def _get_flag_value(self, flag_name: str, flag_config: Dict[str, Any]) -> Any:
        """
        Get the value of a specific feature flag.

        Args:
            flag_name: Name of the feature flag
            flag_config: Configuration for the feature flag

        Returns:
            The resolved value of the feature flag
        """
        # Check environment variable first
        env_var = flag_config.get("env_var")
        if env_var:
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    if flag_config["type"] == "boolean":
                        # Handle various boolean string representations
                        if env_value.lower() in ("true", "1", "yes", "on", "enabled"):
                            return True
                        elif env_value.lower() in (
                            "false",
                            "0",
                            "no",
                            "off",
                            "disabled",
                        ):
                            return False
                        else:
                            logger.warning(
                                f"⚠️ Invalid boolean value for {flag_name}: {env_value}, using default"
                            )
                    elif flag_config["type"] == "integer":
                        return int(env_value)
                    elif flag_config["type"] == "float":
                        return float(env_value)
                    else:
                        return env_value
                except (ValueError, TypeError) as e:
                    logger.warning(
                        f"⚠️ Failed to parse environment variable for {flag_name}: {e}, using default"
                    )

        # Return default value
        return flag_config["default"]

    def is_enabled(self, flag_name: str) -> bool:
        """
        Check if a feature flag is enabled.

        Args:
            flag_name: Name of the feature flag to check

        Returns:
            True if the feature flag is enabled, False otherwise

        Raises:
            KeyError: If the feature flag doesn't exist
        """
        if not self._initialized:
            self._initialize()

        if flag_name not in self._cache:
            raise KeyError(f"Feature flag '{flag_name}' not found")

        value = self._cache[flag_name]

        # Ensure boolean flags return boolean values
        if FEATURE_FLAGS[flag_name]["type"] == "boolean":
            return bool(value)

        return value

    def get_value(self, flag_name: str) -> Any:
        """
        Get the raw value of a feature flag.

        Args:
            flag_name: Name of the feature flag to get

        Returns:
            The raw value of the feature flag

        Raises:
            KeyError: If the feature flag doesn't exist
        """
        if not self._initialized:
            self._initialize()

        if flag_name not in self._cache:
            raise KeyError(f"Feature flag '{flag_name}' not found")

        return self._cache[flag_name]

    def get_all_flags(self) -> Dict[str, Any]:
        """
        Get all feature flags and their current values.

        Returns:
            Dictionary of all feature flags and their values
        """
        if not self._initialized:
            self._initialize()

        return self._cache.copy()

    def refresh_flags(self):
        """Refresh all feature flags from environment variables."""
        logger.info("🔄 Refreshing feature flags...")
        self._initialized = False
        self._cache.clear()
        self._initialize()

    def set_flag_override(self, flag_name: str, value: Any):
        """
        Override a feature flag value (for testing purposes).

        Args:
            flag_name: Name of the feature flag to override
            value: New value for the feature flag

        Raises:
            KeyError: If the feature flag doesn't exist
        """
        if flag_name not in FEATURE_FLAGS:
            raise KeyError(f"Feature flag '{flag_name}' not found")

        # Validate type
        expected_type = FEATURE_FLAGS[flag_name]["type"]
        if expected_type == "boolean" and not isinstance(value, bool):
            raise ValueError(
                f"Feature flag '{flag_name}' expects boolean value, got {type(value)}"
            )
        elif expected_type == "integer" and not isinstance(value, int):
            raise ValueError(
                f"Feature flag '{flag_name}' expects integer value, got {type(value)}"
            )
        elif expected_type == "float" and not isinstance(value, (int, float)):
            raise ValueError(
                f"Feature flag '{flag_name}' expects float value, got {type(value)}"
            )

        self._cache[flag_name] = value
        logger.info(f"🚩 Feature flag '{flag_name}' overridden to: {value}")


# Global feature flag manager instance
_feature_flag_manager = None


def get_feature_flag_manager() -> FeatureFlagManager:
    """Get or create the global feature flag manager instance."""
    global _feature_flag_manager
    if _feature_flag_manager is None:
        _feature_flag_manager = FeatureFlagManager()
    return _feature_flag_manager


def is_feature_enabled(flag_name: str) -> bool:
    """
    Convenience function to check if a feature flag is enabled.

    Args:
        flag_name: Name of the feature flag to check

    Returns:
        True if the feature flag is enabled, False otherwise
    """
    return get_feature_flag_manager().is_enabled(flag_name)


def get_feature_value(flag_name: str) -> Any:
    """
    Convenience function to get the value of a feature flag.

    Args:
        flag_name: Name of the feature flag to get

    Returns:
        The value of the feature flag
    """
    return get_feature_flag_manager().get_value(flag_name)


# Specific feature flag checks for Task 053
def use_normalized_storage() -> bool:
    """Check if normalized storage should be used."""
    return is_feature_enabled("USE_NORMALIZED_STORAGE")


def normalized_storage_fallback() -> bool:
    """Check if fallback to old storage is enabled."""
    return is_feature_enabled("NORMALIZED_STORAGE_FALLBACK")


def normalized_storage_logging() -> bool:
    """Check if detailed logging for normalized storage is enabled."""
    return is_feature_enabled("NORMALIZED_STORAGE_LOGGING")


# Environment variable setup for easy configuration
def setup_feature_flags_from_env():
    """Set up feature flags from environment variables."""
    logger.info("🔧 Setting up feature flags from environment variables...")

    # Set up normalized storage flags
    if os.getenv("USE_NORMALIZED_STORAGE"):
        os.environ["USE_NORMALIZED_STORAGE"] = os.getenv("USE_NORMALIZED_STORAGE")

    if os.getenv("NORMALIZED_STORAGE_FALLBACK"):
        os.environ["NORMALIZED_STORAGE_FALLBACK"] = os.getenv(
            "NORMALIZED_STORAGE_FALLBACK"
        )

    if os.getenv("NORMALIZED_STORAGE_LOGGING"):
        os.environ["NORMALIZED_STORAGE_LOGGING"] = os.getenv(
            "NORMALIZED_STORAGE_LOGGING"
        )

    logger.info("✅ Feature flags configured from environment variables")


# Initialize feature flags when module is imported
setup_feature_flags_from_env()
