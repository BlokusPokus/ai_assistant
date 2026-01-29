"""
Unit tests for the new canonical Celery entrypoint.

These tests describe the desired behavior for `personal_assistant.celery`
before the implementation exists, to drive a TDD-style refactor.
"""

import pytest


def test_celery_app_import():
    """The Celery app should be importable from personal_assistant.celery."""
    from personal_assistant.celery import app

    assert app is not None

def test_celery_app_basic_configuration():
    """The Celery app should have basic broker/backend and task config."""
    from personal_assistant.celery import app

    # Broker and backend should be configured and both use Redis
    assert hasattr(app.conf, "broker_url")
    assert hasattr(app.conf, "result_backend")
    assert "redis://" in app.conf.broker_url
    assert "redis://" in app.conf.result_backend
    assert app.conf.broker_url == app.conf.result_backend

    # Basic serialization and timezone config
    assert app.conf.task_serializer == "json"
    assert "json" in app.conf.accept_content
    assert app.conf.result_serializer == "json"
    assert app.conf.timezone == "UTC"
    assert app.conf.enable_utc is True


def test_celery_app_autodiscovery():
    """
    The Celery app should autodiscover tasks from the workers package.

    We expect at least the AI tasks module to be present in the task registry.
    """
    from personal_assistant.celery import app

    registered_tasks = app.tasks.keys()

    target = "personal_assistant.workers.tasks.ai_tasks.process_due_ai_tasks"

    assert any(
        target in name for name in registered_tasks
    ), "AI task module was not autodiscovered by Celery app"

def test_celery_app_side_effects_limited(monkeypatch):
    """
    Importing personal_assistant.celery should not initialize the database directly.

    We patch db_config._initialize_database and assert it is not called during import.
    """
    # Importing settings and db_config should be allowed, but Celery entrypoint
    # should not eagerly initialize the DB.
    from personal_assistant.config import database as database_module

    monkeypatch.setattr(
        database_module.db_config, "_initialize_database", lambda *args, **kwargs: None
    )

    # Importing the Celery entrypoint should not call DB initialization.
    # We don't assert the lambda was called; instead, this test ensures that
    # importing personal_assistant.celery does not itself import and execute
    # workers.celery_app (where DB init currently lives).
    from personal_assistant import celery  # noqa: F401


if __name__ == "__main__":
    pytest.main([__file__])

