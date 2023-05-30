"""
Celery Scheduler:
    Creates a schedule for work to be executed by a celery task worker.
        1. Starting time
            - The moment in time this object was created
        2. Action
            - The current action to check a conditional with current screen data
        3. Job Creation Delta Time
            - The time between the creation of each celery job
        4. Job Schedule
            - The schedule for the creation of celery jobs
        5. Cache key list
            - List containing retrieval keys for the Task Manager
        6. Result due date
            - The date time this action condition result is due
"""
import threading
import time
import uuid
import datetime as dt
from typing import Optional

from . import celery_worker, models, process_controller, redis_cache


class CeleryScheduler:
    """A celery job scheduler that incrementally makes jobs to be executed
    at a later point in time. The scheduler will create jobs until the
    maximum number of jobs is reached or the result due date is reached."""

    def __init__(self, task: models.Task, action: models.Action, result_due_datetime):
        self.schedule_id = uuid.uuid4()
        self.starting_datetime = dt.datetime.now()
        self.action = action
        self.job_creation_delta_time = task.job_creation_delta_time
        self.max_num_jobs = task.max_num_celery_jobs
        self.job_schedule = []
        self.cache_key_list = []
        self.result_due_date = result_due_datetime
        self.cancel_threads = threading.Event()

    def cancel_schedule(self) -> None:
        """Cancels the schedule by setting the cancel threads event."""
        self.cancel_threads.set()

    def get_time_delta(self):
        """Gets the time delta between the starting time and the current time."""
        return self.starting_datetime - dt.datetime.now()

    def get_result(self, reverse: bool) -> Optional[bool]:
        """Gets the result of the action condition from shared cache."""
        cache_keys = reversed(self.cache_key_list) if reverse else self.cache_key_list
        return next(
            (redis_cache.get_condition_result(cache_key) for cache_key in cache_keys if redis_cache.get_condition_result(cache_key)),
            None
        )

    def get_latest_result(self) -> Optional[bool]:
        """Gets the latest result of the action condition from shared cache."""
        return self.get_result(reverse=True)

    def get_final_result(self) -> Optional[bool]:
        """Gets the final result of the action condition from shared cache."""
        return self.get_result(reverse=False)

    def create_job(self, job_num: int, job_start_time: dt.datetime) -> None:
        """Creates a job to be executed by a celery worker."""
        screenshot_file = process_controller.save_screenshot()
        now = dt.datetime.now()
        if now < job_start_time:
            time_diff = job_start_time - now
            time.sleep(time_diff.total_seconds())
        if not self.cancel_threads.is_set():
            celery_worker.cache_conditional_result.delay(
                action=self.action,
                screenshot_file=screenshot_file,
                cache_key=self.cache_key_list[job_num],
            )

    def job_scheduler_thread(self) -> None:
        """Creates a thread that creates jobs to be executed by a celery worker."""
        for job_num, job_start_time in enumerate(self.job_schedule):
            if self.cancel_threads.is_set():
                break
            self.create_job(job_num, job_start_time)

    def create_job_schedule(self) -> None:
        """Creates a schedule for jobs to be executed by a celery worker."""
        self.job_schedule = [
            self.result_due_date - dt.timedelta(seconds=job_num * self.job_creation_delta_time)
            for job_num in range(self.max_num_jobs)
            if self.result_due_date - dt.timedelta(seconds=job_num * self.job_creation_delta_time) > dt.datetime.now()
        ]
        self.cache_key_list = [f"{self.schedule_id}-{job_num}" for job_num in range(len(self.job_schedule))]

    def execute_job_schedule(self) -> None:
        """Creates a thread that creates jobs to be executed by a celery worker."""
        job_schedule_thread = threading.Thread(target=self.job_scheduler_thread, daemon=True)
        job_schedule_thread.start()

    def execute_job_retry(self) -> None:
        """Creates a job to be executed by a celery worker."""
        job_num = len(self.job_schedule)
        job_start_time = dt.datetime.now()
        self.cache_key_list.append(f"{self.schedule_id}-{job_num}")
        self.job_schedule.append(job_start_time)
        self.create_job(job_num, job_start_time)
