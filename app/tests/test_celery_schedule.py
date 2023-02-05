import datetime as dt

from core.celery_scheduler import CeleryScheduler
from .mixins import ModelMixin


class TestCeleryScheduler(ModelMixin):
    def test_create_job_schedule(self):
        action = self.get_action("test_capture_screen_data")
        scheduler = CeleryScheduler(
            self.test_task_obj, action, dt.datetime.now()
        )
