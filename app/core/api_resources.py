"""
API Resources
    API Collections - central storage for JSON Collection objects
        1. Action collection - All actions created, read, updated and
            deleted through the API endpoints
        2. Task collection - All tasks  created, read, updated and
            deleted through the API endpoints
        3. Schedule collection - All schedules created, read, updated and
            deleted through the API endpoints
        4. Logging level - Logging level for the API
"""
import logging

from . import models, redis_cache


class APICollections:
    def __init__(
        self,
        action_collection: models.Action = None,
        task_collection: models.Task = None,
        schedule_collection: models.Schedule = None,
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
            self.schedule_collection = (
                schedule_collection
                or models.JsonCollectionResource(models.Schedule, testing=True)
            )
        else:
            self.action_collection = models.JsonCollectionResource(
                models.Action
            )
            self.task_collection = models.JsonCollectionResource(models.Task)
            self.schedule_collection = models.JsonCollectionResource(
                models.Schedule
            )

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

    def update_action(self, action_id: str, action: models.Action) -> models.Action:
        response = self.action_collection.update_collection(action_id, action)
        redis_cache.set_json("action", response.id, response.dict())
        return self.action_collection.update_collection(action_id, action)

    def delete_action(self, action_id):
        response = self.action_collection.delete_collection(action_id)
        if response.get('data') == f"Deleted Action with id: {action_id}":
            redis_cache.del_json("action", action_id)
        return response

    def add_task(self, task: models.Task) -> dict:
        return self.task_collection.add_collection(task)

    def get_task(self, task_id: str) -> models.Task:
        return self.task_collection.get_collection(task_id)

    def get_task_collection(self) -> dict:
        return self.task_collection.get_all_collections()

    def update_task(self, task_id: str, task: models.Task) -> models.Task:
        return self.task_collection.update_collection(task_id, task)

    def delete_task(self, task_id: str):
        return self.task_collection.delete_collection(task_id)

    def get_schedule(self, schedule_id: str) -> models.Schedule:
        return self.schedule_collection.get_collection(schedule_id)

    def get_schedule_collection(self) -> dict:
        return self.schedule_collection.get_all_collections()

    def update_schedule(self, schedule_id, schedule) -> models.Schedule:
        return self.schedule_collection.update_collection(schedule_id, schedule)

    def delete_schedule(self, schedule_id):
        return self.schedule_collection.delete_collection(schedule_id)

storage = APICollections()
