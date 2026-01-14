from app.core.celery_app import celery
import app.tasks.check_keys_task

if __name__ == "__main__":
    celery.start()
