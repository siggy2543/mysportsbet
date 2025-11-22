"""
Celery Application Configuration for Sports Betting Platform
"""

import os
from celery import Celery

# Create Celery instance
celery = Celery('sports_betting_app')

# Configure Celery
celery.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/1'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/2'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    # Task discovery
    include=[
        'tasks.prediction_tasks',
        'tasks.betting_tasks',
    ]
)

# Auto-discover tasks
celery.autodiscover_tasks()

if __name__ == '__main__':
    celery.start()