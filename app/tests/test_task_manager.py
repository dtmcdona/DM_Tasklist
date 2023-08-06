from unittest.mock import patch

from core import api_resources, fast_api_endpoints, models, task_manager
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
        assert task_manager_obj.start_playback() == {"data": "Task complete"}
        return task_manager_obj

    def setup_task_manager(self, images):
        action_ids = self.get_action_ids()
        last_action_id = action_ids[-1]
        first_action_id = action_ids[0]
        self.test_action = {
            "id": first_action_id,
            "function": "capture_screen_data",
            "x1": 0,
            "y1": 0,
            "x2": 132,
            "y2": 32,
            "images": images,
            "haystack_image": "test_image_copy3.png",
            "image_conditions": ["if_image_present"],
            "true_case": "skip_to_id",
            "skip_to_id": self.get_action(last_action_id).get("id"),
        }
        self.test_action_obj = models.Action(**self.test_action)
        self.update_action(first_action_id, self.test_action_obj)
        task_manager_obj = self.expect_playback_success()
        return task_manager_obj, action_ids

    def test_start_playback__no_conditionals(self):
        """
        Play the task with no conditionals twice and make sure config is expected
        result
        """
        action_ids = self.get_action_ids()
        self.expect_playback_success()
        task_manager_obj = self.expect_playback_success()
        expected_actions_processed = {str(i): 1 for i in range(len(action_ids))}
        assert task_manager_obj.actions_processed == expected_actions_processed
        assert task_manager_obj.config == {
            "conditionals": [],
            "early_result_available": [],
            "fastest_timeline": [0.0 for _ in range(10)],
            "last_conditional_results": [],
        }

    def test_start_playback__skip_to_id(self):
        task_manager_obj, action_ids = self.setup_task_manager(
            ["test_image_copy3.png"]
        )
        expected_actions_processed = {
            str(i): 1 if i == 0 or i == len(action_ids) - 1 else 0
            for i in range(len(action_ids))
        }
        assert task_manager_obj.actions_processed == expected_actions_processed

    def test_start_playback__multiple_images_found(self):
        task_manager_obj, action_ids = self.setup_task_manager(
            ["test_image_copy3.png", "test_image_present_1.png"]
        )
        expected_actions_processed = {
            str(i): 1 if i == 0 or i == len(action_ids) - 1 else 0
            for i in range(len(action_ids))
        }
        assert task_manager_obj.actions_processed == expected_actions_processed

    def test_start_playback__images_not_found(self):
        task_manager_obj, action_ids = self.setup_task_manager(
            ["test_image_present_1.png" for _ in range(3)]
        )
        expected_actions_processed = {str(i): 1 for i in range(len(action_ids))}
        assert task_manager_obj.actions_processed == expected_actions_processed

    @patch(
        "core.celery_scheduler.redis_cache.get_condition_result",
        return_value=True,
    )
    def test_start_playback__cached_result_true(
        self, mock_get_condition_result
    ):
        task_manager_obj, action_ids = self.setup_task_manager(
            ["test_image_copy3.png", "test_image_present_1.png"]
        )
        expected_actions_processed = {
            str(i): 1 if i == 0 or i == len(action_ids) - 1 else 0
            for i in range(len(action_ids))
        }
        assert task_manager_obj.actions_processed == expected_actions_processed

    @patch(
        "core.celery_scheduler.redis_cache.get_condition_result",
        return_value=False,
    )
    def test_start_playback__cached_result_false(
        self, mock_get_condition_result
    ):
        task_manager_obj, action_ids = self.setup_task_manager(
            ["test_image_present_1.png" for _ in range(3)]
        )
        expected_actions_processed = {str(i): 1 for i in range(len(action_ids))}
        assert task_manager_obj.actions_processed == expected_actions_processed
