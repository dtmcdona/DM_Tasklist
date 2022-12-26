import logging

from core import models


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
        logging.basicConfig(level=self.logging_level)

    def add_action(self, action) -> dict:
        return self.action_collection.add_collection(action)

    def get_action(self, action_id) -> models.Action:
        return self.action_collection.get_collection(action_id)

    def get_action_collection(self):
        return self.action_collection.json_collection

    def update_action(self, action_id, action) -> models.Action:
        return self.action_collection.update_collection(action_id, action)

    def delete_action(self, action_id):
        return self.action_collection.delete_collection(action_id)

    def add_task(self, task) -> dict:
        return self.task_collection.add_collection(task)

    def get_task(self, task_id) -> models.Task:
        return self.task_collection.get_collection(task_id)

    def get_task_by_name(self, task_name):
        return self.task_collection.get_collection_by_name(task_name)

    def get_task_collection(self):
        return self.task_collection.json_collection

    def update_task(self, task_id, task) -> models.Task:
        return self.task_collection.update_collection(task_id, task)

    def delete_task(self, task_id):
        return self.task_collection.delete_collection(task_id)

    def get_schedule(self, schedule_id) -> models.Schedule:
        return self.schedule_collection.get_collection(schedule_id)

    def get_schedule_by_name(self, schedule_name):
        return self.schedule_collection.get_collection_by_name(schedule_name)

    def get_schedule_collection(self):
        return self.schedule_collection.json_collection

    def update_schedule(self, schedule_id, schedule) -> models.Schedule:
        return self.schedule_collection.update_collection(schedule_id, schedule)

    def delete_schedule(self, schedule_id):
        return self.schedule_collection.delete_collection(schedule_id)
