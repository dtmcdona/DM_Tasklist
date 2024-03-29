"""
API Resources
    API Collections - central storage for JSON Collection objects
        1. Action collection - All actions created, read, updated and
            deleted through the API endpoints
        2. Task collection - All tasks  created, read, updated and
            deleted through the API endpoints
        3. Logging level - Logging level for the API
"""
import logging

from . import models, redis_cache


class APICollections:
    def __init__(
        self,
        action_collection: models.Action = None,
        task_collection: models.Task = None,
        logging_level=None,
    ):
        if logging_level == logging.DEBUG:
            self.action_collection = (
                action_collection
                or models.JsonCollectionResource(models.Action, testing=True)
            )
            self.task_collection = (
                task_collection
                or models.JsonCollectionResource(models.Task, testing=True)
            )
        else:
            self.action_collection = models.JsonCollectionResource(
                models.Action
            )
            self.task_collection = models.JsonCollectionResource(models.Task)

        self.logging_level = logging.WARNING

    def add_action(self, action: models.Action) -> dict:
        response = self.action_collection.add_collection(action)
        redis_cache.set_json("action", response.id, response.dict())
        return response

    def get_action(self, action_id: str) -> models.Action:
        cached_value = redis_cache.get_json("action", action_id)
        if cached_value:
            return cached_value

        response = self.action_collection.get_collection(action_id)
        redis_cache.set_json("action", response.get("id"), response)
        return response

    def get_action_collection(self) -> dict:
        return self.action_collection.get_all_collections()

    def update_action(
        self, action_id: str, action: models.Action
    ) -> models.Action:
        response = self.action_collection.update_collection(action_id, action)
        redis_cache.set_json("action", response.id, response.dict())
        return self.action_collection.update_collection(action_id, action)

    def delete_action(self, action_id):
        response = self.action_collection.delete_collection(action_id)
        if response.get("data") == f"Deleted Action with id: {action_id}":
            redis_cache.del_json("action", action_id)
        return response

    def add_task(self, task: models.Task) -> dict:
        response = self.task_collection.add_collection(task)
        redis_cache.set_json("task", response.id, response.dict())
        return response

    def get_task(self, task_id: str) -> models.Task:
        cached_value = redis_cache.get_json("task", task_id)
        if cached_value:
            return cached_value

        response = self.task_collection.get_collection(task_id)
        redis_cache.set_json("task", response.get("id"), response)
        return response

    def get_task_collection(self) -> dict:
        return self.task_collection.get_all_collections()

    def update_task(self, task_id: str, task: models.Task) -> models.Task:
        response = self.task_collection.update_collection(task_id, task)
        redis_cache.set_json("task", response.id, response.dict())
        return self.task_collection.update_collection(task_id, task)

    def delete_task(self, task_id: str):
        response = self.task_collection.delete_collection(task_id)
        if response.get("data") == f"Deleted Task with id: {task_id}":
            redis_cache.del_json("task", task_id)
        return response


storage = APICollections()
