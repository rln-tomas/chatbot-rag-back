"""
Celery configuration settings.
"""

from kombu import Queue

# Celery task queues
task_queues = (
    Queue("scraping", routing_key="scraping"),
    Queue("default", routing_key="default"),
)

# Task default configuration
task_default_queue = "default"
task_default_exchange = "default"
task_default_routing_key = "default"

# Result backend settings
result_backend_transport_options = {
    "master_name": "mymaster",
}

# Worker settings
worker_send_task_events = True
task_send_sent_event = True

# Retry policy
task_acks_late = True
task_reject_on_worker_lost = True

# Task result settings
result_expires = 3600  # Results expire after 1 hour

# Beat schedule (for periodic tasks if needed)
beat_schedule = {
    # Example periodic task
    # "cleanup-old-results": {
    #     "task": "worker.tasks.cleanup_tasks.cleanup_old_results",
    #     "schedule": crontab(hour=0, minute=0),  # Run daily at midnight
    # },
}
