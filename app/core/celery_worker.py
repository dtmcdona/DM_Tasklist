import os

from celery import Celery
from typing import List


celery = Celery(
    __name__,
    broker="amqp://user:password@broker:5672"
)


@celery.task(name="run_action")
def run_action(action_str_list: List[str]):
    for action_str in action_str_list:
        if action_str.startswith("say_hello"):
            param = action_str.lstrip("say_hello(\"")
            param = param.rstrip("\")")
            return f"Hello {param}"
    return 'Action not processed.'

