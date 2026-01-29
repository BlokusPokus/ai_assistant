from celery import Celery

app = Celery(
    "tasks",
    broker="redis://:redis_password@localhost:6379/0",
    backend="redis://:redis_password@localhost:6379/0",
)

@app.task
def add(x, y):
    return x + y