import pytest
from core import fast_api_endpoints, models, task_manager
from .mixins import ModelMixin


class TestTaskManager(ModelMixin):
    @staticmethod
    def get_default_config_mock():
        return {
            "conditionals": [],
            "early_result_available": [],
            "fastest_timeline": [],
            "last_conditional_results": [],
        }

    def expect_playback_success(self):
        task_manager_obj = task_manager.TaskManager(self.test_task_obj, False)
        task_manager_obj.actions = [
            self.get_action(action_id)
            for action_id in self.test_task_obj.action_id_list
        ]
        task_manager_obj.get_default_config()
        # assert task_manager_obj.config == self.get_default_config_mock()
        assert task_manager_obj.start_playback() == {"data": "Task complete"}
        return task_manager_obj

    def test_start_playback__no_conditionals(self):
        self.expect_playback_success()
        task_manager_obj = self.expect_playback_success()
        expected_actions_processed = {str(i): 1 for i in range(9)}
        assert task_manager_obj.actions_processed == expected_actions_processed

    def test_start_playback__skip_to_name(self):
        last_action_id = self.get_action_ids()[-1]
        self.test_action = {
            "id": 0,
            "name": "test_capture_screen_data",
            "function": "capture_screen_data",
            "x1": 0,
            "y1": 0,
            "x2": 132,
            "y2": 32,
            "images": ["test_image_copy3.png", "test_image_copy3.png"],
            "image_conditions": ["if_image_present"],
            "true_case": "skip_to_name",
            "false_case": "skip_to_name",
            "skip_to_name": self.get_action(last_action_id).get("name"),
        }
        self.test_action_obj = models.Action(**self.test_action)
        self.update_action(0, self.test_action_obj)
        task_manager_obj = self.expect_playback_success()
        expected_actions_processed = {
            str(i): 1 if i == 0 or i == 8 else 0 for i in range(9)
        }
        assert task_manager_obj.actions_processed == expected_actions_processed
