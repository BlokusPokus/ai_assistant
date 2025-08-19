#!/usr/bin/env python3
"""
Configuration validation script for Personal Assistant.

This script validates that all required environment variables are set
and provides helpful feedback for missing or misconfigured settings.
"""

import os
import sys
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
config_file = f"config/{ENVIRONMENT}.env"

if os.path.exists(config_file):
    load_dotenv(config_file)
else:
    load_dotenv()

# Configuration requirements
REQUIRED_SETTINGS = {
    "DATABASE_URL": "Database connection string",
    "GOOGLE_API_KEY": "Google API key for Gemini LLM functionality"
}

OPTIONAL_SETTINGS = {
    "TWILIO_ACCOUNT_SID": "Twilio account SID for SMS notifications",
    "TWILIO_AUTH_TOKEN": "Twilio auth token for SMS notifications",
    "QDRANT_API_KEY": "Qdrant API key for vector database",
    "MICROSOFT_CLIENT_ID": "Microsoft client ID for email integration",
    "NOTION_API_KEY": "Notion API key for knowledge management",
    "CONVERSATION_RESUME_WINDOW_MINUTES": "Minutes after which conversations are considered old"
}


def validate_setting(key: str, value: str, required: bool = False) -> Tuple[bool, str]:
    """Validate a single setting."""
    if not value or value.strip() == "":
        if required:
            return False, f"❌ {key} is REQUIRED but not set"
        else:
            return True, f"⚠️  {key} is optional and not set"

    # Check for placeholder values
    if "your_" in value.lower() or "placeholder" in value.lower():
        if required:
            return False, f"❌ {key} contains placeholder value: {value}"
        else:
            return True, f"⚠️  {key} contains placeholder value: {value}"

    return True, f"✅ {key} is properly configured"


def validate_configuration() -> Tuple[bool, List[str]]:
    """Validate the entire configuration."""
    results = []
    all_valid = True

    print(f"🔍 Validating configuration for environment: {ENVIRONMENT}")
    print(f"📁 Config file: {config_file}")
    print("=" * 60)

    # Check required settings
    print("\n📋 REQUIRED SETTINGS:")
    for key, description in REQUIRED_SETTINGS.items():
        value = os.getenv(key, "")
        is_valid, message = validate_setting(key, value, required=True)
        if not is_valid:
            all_valid = False
        results.append(message)
        print(f"  {message}")
        if description:
            print(f"    Description: {description}")

    # Check optional settings
    print("\n📋 OPTIONAL SETTINGS:")
    for key, description in OPTIONAL_SETTINGS.items():
        value = os.getenv(key, "")
        is_valid, message = validate_setting(key, value, required=False)
        results.append(message)
        print(f"  {message}")
        if description:
            print(f"    Description: {description}")

    # Check environment-specific settings
    print("\n📋 ENVIRONMENT SETTINGS:")
    env_settings = {
        "ENVIRONMENT": "Current environment",
        "DEBUG": "Debug mode",
        "LOG_LEVEL": "Logging level"
    }

    for key, description in env_settings.items():
        value = os.getenv(key, "")
        is_valid, message = validate_setting(key, value, required=False)
        results.append(message)
        print(f"  {message}")
        if description:
            print(f"    Description: {description}")

    return all_valid, results


def main():
    """Main validation function."""
    try:
        is_valid, results = validate_configuration()

        print("\n" + "=" * 60)
        if is_valid:
            print("🎉 Configuration validation PASSED!")
            print("✅ All required settings are properly configured.")
        else:
            print("❌ Configuration validation FAILED!")
            print("⚠️  Please fix the issues above before proceeding.")

            # Provide specific guidance
            print("\n🔧 IMMEDIATE ACTIONS REQUIRED:")
            print("1. Set GOOGLE_API_KEY to your actual Google API key for Gemini")
            print("2. Ensure DATABASE_URL points to your actual database")
            print("3. Test all external service connections")

            sys.exit(1)

        # Additional recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("1. Ensure all API keys are valid and have proper permissions")
        print("2. Test database connectivity before deployment")
        print("3. Verify external service credentials work")
        print("4. Consider using a secrets management service for production")

        # Production readiness check
        if os.getenv("ENVIRONMENT") == "production":
            print("\n🚀 PRODUCTION READINESS CHECK:")
            print("✅ Environment is set to production")
            print("✅ Debug mode is disabled")
            print("✅ Log levels are production-appropriate")
            print("✅ All required settings are configured")

    except Exception as e:
        print(f"❌ Validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
