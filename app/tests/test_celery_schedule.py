import datetime as dt

from core.celery_scheduler import CeleryScheduler
from .mixins import ModelMixin


class TestCeleryScheduler(ModelMixin):
    def test_create_job_schedule(self):
        action = self.get_action(0)
        scheduler = CeleryScheduler(
            self.test_task_obj, action, dt.datetime.now()
        )
