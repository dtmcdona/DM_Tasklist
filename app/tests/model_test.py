import logging
import os

from core.models import Action, Task, Schedule, JsonCollectionResource


class TestModels:
    """Used to test actions, tasks, and schedule lists"""
    test_action1 = {
        "id": 0,
        "name": "test_move_to",
        "function": "move_to",
        "x1": 0,
        "y1": 0,
    }
    test_action2 = {
        "id": 1,
        "name": "test_click",
        "function": "click",
        "x1": 0,
        "y1": 0,
    }
    test_task = {
        "id": 0,
        "name": "test_tasks",
        "task_dependency_id": 0,
        "action_id_list": [1, 2],
    }
    test_shedule = {
        "id": 0,
        "name": "test_schedule",
        "schedule_dependency_id": 0,
        "task_id_list": [1],
    }

    @classmethod
    def setup_class(cls):
        cls.action_collection = JsonCollectionResource(Action, True)
        cls.task_collection = JsonCollectionResource(Task, True)
        cls.schedule_collection = JsonCollectionResource(Schedule, True)

    @classmethod
    def teardown_method(cls):
        os.remove(cls.action_collection.file_path)
        os.remove(cls.task_collection.file_path)
        os.remove(cls.schedule_collection.file_path)

    def test_json_collection_resource(self):
        test_action_obj1 = Action(**self.test_action1)
        test_action_obj2 = Action(**self.test_action2)
        self.action_collection.add_collection(test_action_obj1)
        self.action_collection.add_collection(test_action_obj2)
        logging.debug(self.action_collection)
        test_task_obj = Task(**self.test_task)
        self.task_collection.add_collection(test_task_obj)
        test_schedule1 = Schedule(**self.test_shedule)
        self.schedule_collection.add_collection(test_schedule1)
        self.action_collection.load_collection()
        self.task_collection.load_collection()
        self.schedule_collection.load_collection()
        assert set(self.action_collection.get_collection(0)) >= set(self.test_action1)
        assert set(self.action_collection.get_collection(1)) >= set(self.test_action2)
        assert set(self.task_collection.get_collection(0)) >= set(self.test_task)
        assert set(self.schedule_collection.get_collection(0)) >= set(self.test_shedule)
