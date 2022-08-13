from celery import Celery

from . import fast_api_automation as api

celery = Celery(__name__, broker="amqp://user:password@broker:5672")


@celery.task(name="run_action")
def run_action(action_id: int):
    return api.execute_action(action_id)
