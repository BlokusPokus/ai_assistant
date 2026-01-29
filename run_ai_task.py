#!/usr/bin/env python3
"""
Trigger an AI task via Celery and wait for the result.

Prerequisites:
- Redis running (e.g. Docker: docker compose -f docker/docker-compose.dev.yml up -d redis)
- Celery worker running (e.g. Docker worker service, or: celery -A personal_assistant.celery worker --loglevel=info --queues=ai_tasks)
- Optional: load config from config/development.env so CELERY_BROKER_URL is set

Run from repo root:
  PYTHONPATH=src python run_ai_task.py

Or with venv:
  PYTHONPATH=src ./venv_personal_assistant/bin/python run_ai_task.py
"""

import os
import sys

# Ensure src is on path for personal_assistant imports
repo_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def main():
    from personal_assistant.workers.celery_app import app

    task_name = "personal_assistant.workers.tasks.ai_tasks.test_scheduler_connection"
    print(f"Sending task: {task_name}")
    print("Waiting for worker (timeout 60s)...")

    result = app.send_task(task_name)
    try:
        outcome = result.get(timeout=60)
        print("Result:", outcome)
        if isinstance(outcome, dict) and outcome.get("status") == "success":
            print("OK: Task ran successfully.")
        else:
            print("Task completed; check result above.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
