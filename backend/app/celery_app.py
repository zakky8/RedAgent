"""
Celery application — task queue for async scan execution.
Build Rule 14: Tasks must handle failure and retry with exponential backoff.
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "agentred",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scan_tasks",
        "app.tasks.report_tasks",
        "app.tasks.monitor_tasks",
        "app.tasks.compliance_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=settings.CELERY_MAX_TASKS_PER_CHILD,
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    task_soft_time_limit=3600,   # 1 hour soft limit
    task_time_limit=4200,         # 70 min hard limit
    beat_schedule={
        "run-continuous-cycles": {
            "task": "app.tasks.monitor_tasks.run_continuous_cycles",
            "schedule": 3600.0,  # Every 60 minutes
        },
        "cleanup-old-events": {
            "task": "app.tasks.monitor_tasks.cleanup_old_monitor_events",
            "schedule": 86400.0,  # Daily
        },
    },
)
