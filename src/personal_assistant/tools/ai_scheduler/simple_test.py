#!/usr/bin/env python3
"""
Simple test script for the Calendar Scheduler

This script tests the basic functionality without importing the entire tools module.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_database_queries():
    """Test the database query functions."""
    logger.info("Testing database queries...")

    try:
        # Import directly to avoid circular imports
        from ..db_queries import (
            get_upcoming_events,
            reset_failed_events,
        )

        # Test getting upcoming events
        events = await get_upcoming_events(hours_ahead=2)
        logger.info(f"Found {len(events)} upcoming events")

        # Test resetting failed events
        reset_count = await reset_failed_events()
        logger.info(f"Reset {reset_count} failed events")

        return True

    except Exception as e:
        logger.error(f"Database query test failed: {e}")
        return False


def test_celery_config():
    """Test the Celery configuration."""
    logger.info("Testing Celery configuration...")

    try:
        from ..celery_config import app

        # Check if app is properly configured
        logger.info(f"Celery app name: {app.main}")
        logger.info(f"Broker URL: {app.conf.broker_url}")
        logger.info(f"Result backend: {app.conf.result_backend}")

        return True

    except Exception as e:
        logger.error(f"Celery configuration test failed: {e}")
        return False


def test_scheduler_configuration():
    """Test the scheduler configuration."""
    logger.info("Testing scheduler configuration...")

    try:
        # Import directly to avoid circular imports
        from ..scheduler import create_scheduler

        scheduler = create_scheduler()
        status = scheduler.get_status()
        logger.info(f"Scheduler status: {status}")
        return True

    except Exception as e:
        logger.error(f"Scheduler configuration test failed: {e}")
        return False


async def test_event_processing_workflow():
    """Test the complete event processing workflow."""
    logger.info("Testing event processing workflow...")

    try:
        # Import directly to avoid circular imports
        from ..db_queries import (
            get_upcoming_events,
            mark_event_completed,
            mark_event_processing,
        )

        # Get upcoming events
        # Look ahead 24 hours for testing
        events = await get_upcoming_events(hours_ahead=24)

        if not events:
            logger.info(
                "No events found for testing - this is normal if no events exist")
            return True

        # Test with the first event
        test_event = events[0]
        logger.info(f"Testing with event: {test_event.title}")

        # Mark as processing
        success = await mark_event_processing(test_event.id)
        if not success:
            logger.error("Failed to mark event as processing")
            return False

        # Simulate agent processing
        agent_response = f"Test response for event {test_event.title}"

        # Mark as completed
        success = await mark_event_completed(test_event.id, agent_response)
        if not success:
            logger.error("Failed to mark event as completed")
            return False

        logger.info("Event processing workflow test completed successfully")
        return True

    except Exception as e:
        logger.error(f"Event processing workflow test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting Calendar Scheduler tests...")

    # Test 1: Database queries
    db_test_passed = asyncio.run(test_database_queries())

    # Test 2: Celery configuration
    celery_test_passed = test_celery_config()

    # Test 3: Scheduler configuration
    scheduler_test_passed = test_scheduler_configuration()

    # Test 4: Event processing workflow
    workflow_test_passed = asyncio.run(test_event_processing_workflow())

    # Summary
    logger.info("Test Results:")
    logger.info(
        f"  Database queries: {'PASSED' if db_test_passed else 'FAILED'}")
    logger.info(
        f"  Celery config: {'PASSED' if celery_test_passed else 'FAILED'}")
    logger.info(
        f"  Scheduler config: {'PASSED' if scheduler_test_passed else 'FAILED'}")
    logger.info(
        f"  Event workflow: {'PASSED' if workflow_test_passed else 'FAILED'}")

    all_passed = all([
        db_test_passed,
        celery_test_passed,
        scheduler_test_passed,
        workflow_test_passed
    ])

    if all_passed:
        logger.info("All tests PASSED! Scheduler is ready to use.")
        return 0
    else:
        logger.error("Some tests FAILED. Please check the configuration.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
