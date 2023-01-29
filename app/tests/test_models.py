import logging
import os
import uuid

from core.models import Action, Task, Schedule, JsonCollectionResource


class TestModels:
    """Used to test actions, tasks, and schedule lists"""
    action_id1 = f"{uuid.uuid4()}1"
    action_id2 = f"{uuid.uuid4()}2"
    task_id = str(uuid.uuid4())
    schedule_id = str(uuid.uuid4())
    test_action1 = {
        "id": action_id1,
        "function": "move_to",
        "x1": 0,
        "y1": 0,
    }
    test_action2 = {
        "id": action_id2,
        "function": "click",
        "x1": 0,
        "y1": 0,
    }
    test_task = {
        "id": task_id,
        "action_id_list": [action_id1, action_id2],
    }
    test_shedule = {
        "id": schedule_id,
        "task_id_list": [task_id],
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
        test_schedule_obj = Schedule(**self.test_shedule)
        self.schedule_collection.add_collection(test_schedule_obj)
        self.action_collection.load_collection()
        self.task_collection.load_collection()
        self.schedule_collection.load_collection()
        assert set(self.action_collection.get_collection(self.action_id1)) >= set(
            self.test_action1
        )
        assert set(self.action_collection.get_collection(self.action_id2)) >= set(
            self.test_action2
        )
        assert set(self.task_collection.get_collection(self.task_id)) >= set(
            self.test_task
        )
        assert set(self.schedule_collection.get_collection(self.schedule_id)) >= set(
            self.test_shedule
        )
