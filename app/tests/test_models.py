import logging
from pathlib import Path
from shutil import rmtree
import uuid

from core.models import Action, Task, JsonCollectionResource


class TestModels:
    """Used to test actions and tasks lists"""

    action_id1 = f"{uuid.uuid4()}1"
    action_id2 = f"{uuid.uuid4()}2"
    task_id = str(uuid.uuid4())
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

    @classmethod
    def setup_class(cls):
        cls.action_collection = JsonCollectionResource(Action, True)
        cls.task_collection = JsonCollectionResource(Task, True)

    @classmethod
    def teardown_method(cls):
        rmtree(cls.action_collection.collection_dir)
        rmtree(cls.task_collection.collection_dir)

    def test_json_collection_resource(self):
        test_action_obj1 = Action(**self.test_action1)
        test_action_obj2 = Action(**self.test_action2)
        self.action_collection.add_collection(test_action_obj1)
        self.action_collection.add_collection(test_action_obj2)
        logging.debug(self.action_collection)
        test_task_obj = Task(**self.test_task)
        self.task_collection.add_collection(test_task_obj)
        assert set(
            self.action_collection.get_collection(self.action_id1)
        ) >= set(self.test_action1)
        assert set(
            self.action_collection.get_collection(self.action_id2)
        ) >= set(self.test_action2)
        assert set(self.task_collection.get_collection(self.task_id)) >= set(
            self.test_task
        )
