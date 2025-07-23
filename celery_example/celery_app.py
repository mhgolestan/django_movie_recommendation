from celery import Celery

app = Celery("example", broker="redis://localhost:6379/0")

@app.task
def long_running_task(x):
    import time
    time.sleep(15)
    return x * x