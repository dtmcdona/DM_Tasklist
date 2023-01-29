"""
Task Manager
    Systematically executes linear, conditional, and re-ordered task lists
        1. Linear task list
            - A task that is performed automatically in one set order without conditions
        2. Conditional task list
            - This task list still retains the scheduled order of the original task list
            - A task that can contains conditionals and executes a result when they are True/False.
        3. Re-ordered task list
            - A task that can change the scheduled order of the actions to execute in the task list
            - They also contain conditionals and executes a result when they are True/False.
"""
import logging
import datetime as dt
from typing import List, Any

from . import api_resources, process_controller, celery_scheduler
from .models import Task


logging.basicConfig(level=logging.DEBUG)


class TaskManager:
    """Runs through all actions in a task and executes the action in the order determined
    by conditionals"""

    def __init__(self, task: Task, load_config=False):
        self.status = "Task manager created"
        self.task = task
        self.actions = [
            api_resources.storage.action_collection.get_collection(action_id)
            for action_id in self.task.action_id_list
        ]
        self.config = (
            self.load_task_config()
            if load_config
            else self.get_default_config()
        )
        self.actions_processed = {
            str(index): 0 for index, action_id in enumerate(self.task.action_id_list)
        }

    def get_default_config(self) -> dict:
        """Set the config to default values for a never played task or in the case where
        celery settings changes"""
        conditionals = [
            len(action.get("image_conditions"))
            + len(action.get("variable_conditions"))
            for action in self.actions
            if action.get("image_conditions")
            or action.get("variable_conditions")
        ]

        return {
            "conditionals": conditionals,
            "early_result_available": [],
            "fastest_timeline": [
                action.get("time_delay", 0) for action in self.actions
            ],
            "last_conditional_results": [],
        }

    def load_task_config(self) -> dict:
        """Load previous config"""
        return {
            "conditionals": self.task.conditionals,
            "early_result_available": self.task.early_result_available,
            "fastest_timeline": self.task.fastest_timeline,
            "last_conditional_results": self.task.last_conditional_results,
        }

    def save_task_config(self) -> None:
        """Save config for the current task"""
        new_task = self.task.dict()
        new_task.update(self.config)
        new_task_obj = Task(**new_task)
        self.task = api_resources.storage.update_task(self.task.id, new_task_obj)

    def start_playback(self) -> dict:
        """Execute all actions in a task then save the config"""
        self.execute_actions()
        self.save_task_config()
        return {"data": "Task complete"}

    def execute_actions(self) -> None:
        """This will loop through all actions in a linear, conditional or re-ordered task"""
        index: int = 0
        action_ids: List[str] = [action.get("id") for action in self.actions]
        celery_schedulers = (
            self.get_celery_schedulers()
            if self.config.get("conditionals")
            else []
        )
        while index < len(self.actions):
            action = self.actions[index]
            index += 1
            if not action:
                continue
            self.actions_processed[str(index-1)] += 1

            if len(celery_schedulers) > index:
                if (
                    self.config.get("early_result_available") not in [None, []]
                    and self.config.get("early_result_available")[index] is True
                ):
                    most_recent_result = celery_schedulers[
                        index
                    ].get_latest_result()
                else:
                    most_recent_result = celery_schedulers[
                        index
                    ].get_latest_result()
                    final_result = celery_schedulers[index].get_final_result()
                    self.config["early_result_available"].append(
                        most_recent_result == final_result
                    )
                    if most_recent_result != final_result:
                        most_recent_result = final_result

                self.status = process_controller.action_controller(
                    action, prefetched_condition_result=most_recent_result
                )
                self.config["last_conditional_results"].append(
                    most_recent_result
                )
            else:
                self.status = process_controller.action_controller(action)
            if self.status.get("data") == "skip_to_id":
                skip_to_id = action.get("skip_to_id")
                if skip_to_id in action_ids:
                    index = action_ids.index(skip_to_id)
                    self._cancel_schedulers(celery_schedulers)
                    celery_schedulers = self.get_celery_schedulers(
                        starting_index=index
                    )

    @staticmethod
    def _cancel_schedulers(schedulers) -> None:
        """Cancels any preexisting schedulers when playback order changes"""
        for scheduler in schedulers:
            if scheduler:
                scheduler.cancel_schedule()

    def get_celery_schedulers(self, starting_index: int = 0) -> List[Any]:
        """Creates a list of schedulers with an expected result due datetime"""
        schedulers = []
        result_wait_seconds = 0
        for i, action in enumerate(self.actions):
            if i < starting_index:
                schedulers.append(None)
                continue
            elif len(self.config.get("conditionals")) > 0:
                result_due_date = dt.datetime.now() + dt.timedelta(
                    seconds=result_wait_seconds
                )
                new_scheduler = celery_scheduler.CeleryScheduler(
                    self.task, action, result_due_date
                )
                schedulers.append(new_scheduler)
                result_wait_seconds = 0
            else:
                result_wait_seconds += (
                    self.config.get("fastest_timeline")[i] or 0
                )
                schedulers.append(None)

        return schedulers
