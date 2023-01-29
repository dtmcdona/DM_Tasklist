"""
Celery workers:
    Each worker can execute these jobs for the Task Manager
"""
from celery import Celery

from . import fast_api_endpoints as api
from . import models, process_controller, redis_cache

celery = Celery(__name__, broker="amqp://user:password@broker:5672")


@celery.task(name="run_action")
def run_action(action_id: str):
    return api.execute_action(action_id)


@celery.task(name="cache_conditional_result")
def cache_conditional_result(
    action: models.Action, cache_key: str, screenshot_file: str
) -> None:
    result = process_controller.get_conditionals_result(action, screenshot_file)
    redis_cache.set_condition_result(cache_key, result)
