from celery import Celery
from app.core.config import settings

import logging

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s/%(processName)s] %(name)s: %(message)s",
)

celery = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
    timezone="Europe/Kyiv",
    enable_utc=True,
)


celery.conf.task_default_queue = "default"
celery.conf.task_queues = {
    "default": {
        "exchange": "default",
        "routing_key": "default"
    }
}
celery.autodiscover_tasks(["app.tasks"])

celery.conf.update(
    worker_hijack_root_logger=False,
)
