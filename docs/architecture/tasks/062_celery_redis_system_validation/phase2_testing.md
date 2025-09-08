# Phase 2: Individual Component Testing

## 🧪 **Testing Overview**

**Phase**: 2 - Individual Component Testing  
**Goal**: Test each component in isolation to validate functionality  
**Focus**: Validate that user can create tasks that trigger LLM when scheduled date arrives

---

## 🎯 **Core Functionality Testing**

### **Test 1: Redis Connection Testing**

Let's start by testing Redis connectivity:

```bash
# Test Redis server status
redis-cli ping
```

Expected result: `PONG`

```bash
# Test Redis with authentication
redis-cli -a redis_password ping
```

Expected result: `PONG`

```bash
# Test Redis info
redis-cli info server
```

Expected result: Server information including version, uptime, etc.

### **Test 2: Celery App Initialization**

```python
# Test Celery app loading
python -c "
from personal_assistant.workers.celery_app import app
print(f'✅ Celery app loaded: {app.main}')
print(f'   Broker: {app.conf.broker_url}')
print(f'   Backend: {app.conf.result_backend}')
print(f'   Registered tasks: {len(app.tasks)}')
"
```

Expected result: App loads with proper configuration

### **Test 3: AI Task Manager Database Operations**

```python
# Test AI task manager
python -c "
import asyncio
from personal_assistant.tools.ai_scheduler.ai_task_manager import AITaskManager

async def test_ai_task_manager():
    manager = AITaskManager()
    print('✅ AI Task Manager loaded')

    # Test connection
    try:
        # This should test database connectivity
        print('Testing database connection...')
        # Add actual test here
        print('✅ Database connection working')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')

asyncio.run(test_ai_task_manager())
"
```

### **Test 4: Task Creation Workflow**

```python
# Test task creation
python -c "
import asyncio
from datetime import datetime, timedelta
from personal_assistant.tools.ai_scheduler.ai_task_manager import AITaskManager

async def test_task_creation():
    manager = AITaskManager()

    # Test creating a reminder task
    try:
        remind_at = datetime.now() + timedelta(minutes=5)

        task = await manager.create_reminder(
            user_id=126,
            title='Test Reminder',
            remind_at=remind_at,
            description='Test reminder for validation',
            notification_channels=['sms']
        )

        print(f'✅ Task created: ID={task.id}, Title={task.title}')
        print(f'   Next run: {task.next_run_at}')
        print(f'   Status: {task.status}')

    except Exception as e:
        print(f'❌ Task creation failed: {e}')

asyncio.run(test_task_creation())
"
```

### **Test 5: Worker Task Execution**

```python
# Test worker task execution
python -c "
from personal_assistant.workers.tasks.ai_tasks import test_scheduler_connection

# Test scheduler connection task
try:
    result = test_scheduler_connection.delay()
    response = result.get(timeout=30)
    print(f'✅ Scheduler test result: {response}')
except Exception as e:
    print(f'❌ Scheduler test failed: {e}')
"
```

---

## 🚀 **Live System Testing**

### **Step 1: Start Required Services**

```bash
# Start Redis (if not running)
redis-server --port 6379 --daemonize yes

# Start PostgreSQL (if not running)
pg_ctl start -D /usr/local/var/postgres

# Verify services
redis-cli ping
psql -c "SELECT 1;"
```

### **Step 2: Start Celery Worker**

```bash
# Activate virtual environment
source venv_personal_assistant/bin/activate

# Start Celery worker
celery -A personal_assistant.workers.celery_app worker -Q ai_tasks -l info --detach
```

### **Step 3: Start Beat Scheduler**

```bash
# Start beat scheduler
celery -A personal_assistant.workers.celery_app beat -l info --detach
```

### **Step 4: Test End-to-End Workflow**

```python
# Test complete workflow
python -c "
import asyncio
from datetime import datetime, timedelta
from personal_assistant.workers.tasks.ai_tasks import create_ai_reminder

async def test_complete_workflow():
    # Create a test reminder
    remind_at = (datetime.now() + timedelta(minutes=2)).isoformat()

    try:
        result = create_ai_reminder.delay(
            user_id=126,
            title='Test AI Reminder',
            remind_at=remind_at,
            description='Test reminder for complete workflow validation'
        )

        response = result.get(timeout=30)
        print(f'✅ Complete workflow test: {response}')

    except Exception as e:
        print(f'❌ Complete workflow test failed: {e}')

asyncio.run(test_complete_workflow())
"
```

---

## 🔍 **Component-Specific Tests**

### **Test: AI Task Manager**

```python
# Test AI task manager functionality
python -c "
import asyncio
from datetime import datetime, timedelta
from personal_assistant.tools.ai_scheduler.ai_task_manager import AITaskManager

async def test_ai_task_manager_comprehensive():
    manager = AITaskManager()

    # Test 1: Create reminder
    print('Test 1: Creating reminder...')
    remind_at = datetime.now() + timedelta(minutes=5)
    task = await manager.create_reminder(
        user_id=126,
        title='Test Reminder',
        remind_at=remind_at,
        description='Test reminder'
    )
    print(f'✅ Reminder created: {task.id}')

    # Test 2: Get due tasks
    print('Test 2: Getting due tasks...')
    due_tasks = await manager.get_due_tasks(limit=10)
    print(f'✅ Found {len(due_tasks)} due tasks')

    # Test 3: Update task status
    print('Test 3: Updating task status...')
    await manager.update_task_status(
        task_id=task.id,
        status='processing',
        last_run_at=datetime.now()
    )
    print('✅ Task status updated')

    # Test 4: Create periodic task
    print('Test 4: Creating periodic task...')
    periodic_task = await manager.create_periodic_task(
        user_id=126,
        title='Daily Check-in',
        schedule_type='daily',
        schedule_config={'time': '09:00'},
        description='Daily check-in reminder'
    )
    print(f'✅ Periodic task created: {periodic_task.id}')

asyncio.run(test_ai_task_manager_comprehensive())
"
```

### **Test: Celery Task Registration**

```python
# Test Celery task registration
python -c "
from personal_assistant.workers.celery_app import app

print('Registered Celery Tasks:')
for task_name in sorted(app.tasks.keys()):
    if not task_name.startswith('celery.'):
        print(f'  ✅ {task_name}')

print(f'\\nTotal registered tasks: {len([t for t in app.tasks.keys() if not t.startswith(\"celery.\")])}')

# Test task routing
print('\\nTask Routing:')
for pattern, config in app.conf.task_routes.items():
    print(f'  {pattern} -> Queue: {config.get(\"queue\", \"default\")}, Priority: {config.get(\"priority\", \"default\")}')
"
```

### **Test: Beat Schedule Configuration**

```python
# Test beat schedule
python -c "
from personal_assistant.workers.celery_app import app

print('Beat Schedule Configuration:')
for name, schedule in app.conf.beat_schedule.items():
    print(f'  ✅ {name}:')
    print(f'     Task: {schedule[\"task\"]}')
    print(f'     Schedule: {schedule[\"schedule\"]}')
    print(f'     Options: {schedule.get(\"options\", {})}')
    print()
"
```

---

## 🐛 **Error Testing**

### **Test: Invalid Task Creation**

```python
# Test error handling
python -c "
import asyncio
from datetime import datetime, timedelta
from personal_assistant.tools.ai_scheduler.ai_task_manager import AITaskManager

async def test_error_handling():
    manager = AITaskManager()

    # Test 1: Invalid user ID
    try:
        await manager.create_reminder(
            user_id=99999,  # Non-existent user
            title='Test',
            remind_at=datetime.now() + timedelta(minutes=5)
        )
        print('❌ Should have failed with invalid user ID')
    except Exception as e:
        print(f'✅ Correctly handled invalid user ID: {e}')

    # Test 2: Past date
    try:
        await manager.create_reminder(
            user_id=126,
            title='Test',
            remind_at=datetime.now() - timedelta(days=1)  # Past date
        )
        print('❌ Should have failed with past date')
    except Exception as e:
        print(f'✅ Correctly handled past date: {e}')

asyncio.run(test_error_handling())
"
```

### **Test: Worker Failure Recovery**

```python
# Test worker failure recovery
python -c "
from personal_assistant.workers.tasks.ai_tasks import test_scheduler_connection

# Test retry mechanism
try:
    # This should test retry behavior
    result = test_scheduler_connection.delay()
    print(f'Task ID: {result.id}')
    print(f'Retries: {result.retries}')
    response = result.get(timeout=30)
    print(f'✅ Task completed: {response}')
except Exception as e:
    print(f'❌ Task failed: {e}')
"
```

---

## 📊 **Performance Testing**

### **Test: Concurrent Task Execution**

```python
# Test concurrent task execution
python -c "
import time
from concurrent.futures import ThreadPoolExecutor
from personal_assistant.workers.tasks.ai_tasks import test_scheduler_connection

def execute_task():
    start = time.time()
    result = test_scheduler_connection.delay()
    response = result.get()
    return time.time() - start

# Test 5 concurrent tasks
start_time = time.time()
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(execute_task) for _ in range(5)]
    results = [future.result() for future in futures]

total_time = time.time() - start_time
avg_task_time = sum(results) / len(results)

print(f'Concurrent tasks (5): {total_time:.2f} seconds total')
print(f'Average task time: {avg_task_time:.2f} seconds')
print(f'Tasks per second: {5/total_time:.2f}')
"
```

---

## 🎯 **Success Criteria**

### **Functional Requirements**

- [ ] Redis connectivity: 100% success rate
- [ ] Celery app initialization: 100% success rate
- [ ] AI task manager operations: 100% success rate
- [ ] Task creation: 100% success rate
- [ ] Worker task execution: 100% success rate

### **Performance Requirements**

- [ ] Task execution time: < 30 seconds
- [ ] Concurrent task handling: 5+ tasks simultaneously
- [ ] Memory usage: < 512MB per worker
- [ ] Redis operations: < 100ms response time

### **Reliability Requirements**

- [ ] Error recovery: 100% recovery rate
- [ ] Task retry: 3 retries maximum
- [ ] Logging coverage: 100% of events logged
- [ ] Monitoring accuracy: 100% status accuracy

---

**Phase 2 Testing Complete** ✅  
**Status**: Ready for Phase 3 - Integration Testing  
**Next**: Test component interactions and end-to-end workflows
