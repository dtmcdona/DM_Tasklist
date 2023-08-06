import datetime as dt
from unittest.mock import patch
from core.celery_scheduler import CeleryScheduler
from .mixins import ModelMixin


class TestCeleryScheduler(ModelMixin):
    def setup_scheduler(self, delay: int):
        action = self.get_action("test_capture_screen_data")
        scheduler = CeleryScheduler(
            self.test_task_obj,
            action,
            dt.datetime.now() + dt.timedelta(seconds=delay),
        )
        scheduler.create_job_schedule()
        return scheduler

    def test_create_job_schedule(self):
        scheduler = self.setup_scheduler(2)
        assert len(scheduler.job_schedule) == 4
        assert len(scheduler.cache_key_list) == 4

    def test_create_job_schedule__empty(self):
        scheduler = self.setup_scheduler(0)
        assert len(scheduler.job_schedule) == 0
        assert len(scheduler.cache_key_list) == 0

    @patch(
        "core.celery_scheduler.redis_cache.get_condition_result",
        return_value=True,
    )
    def test_execute_job_schedule(self, mock_get_condition_result):
        scheduler = self.setup_scheduler(2)
        scheduler.execute_job_schedule()
        assert len(scheduler.job_schedule) == 4
        assert len(scheduler.cache_key_list) == 4
        scheduler.cancel_schedule()
        assert (
            scheduler.get_latest_result()
            == mock_get_condition_result.return_value
        )
        assert (
            scheduler.get_final_result()
            == mock_get_condition_result.return_value
        )
