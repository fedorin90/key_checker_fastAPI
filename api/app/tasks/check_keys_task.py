import time
from app.celery_app import celery

@celery.task
def add(x, y):
    time.sleep(5)
    return x + y
