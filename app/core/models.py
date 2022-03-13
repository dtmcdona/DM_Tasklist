import datetime
import json
import os
import sys
from os.path import exists
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel
from pydantic.types import Json

resources_dir = os.path.join(os.getcwd(), 'resources/')
console_log = False


class Action(BaseModel):
    id: int
    name: str
    code: List[str]


class Task(BaseModel):
    id: int
    name: str
    task_dependency_id: Optional[int]
    action_id_list: List[int]


class Schedule(BaseModel):
    id: int
    name: str
    schedule_dependency_id: Optional[int]
    task_id_list: List[int]


class JsonData(BaseModel):
    id: int
    data: Json


class Source(BaseModel):
    id: int
    uri: str


class CapturedData(BaseModel):
    id: int
    type: str
    source_id: int
    json_data_id: int
    schedule_id: int


class TaskRank(BaseModel):
    task_rank: int
    task_id: int
    delta_vars: List[float]
    duration: datetime.time


class MousePosition(BaseModel):
    action_id: int
    x: int
    y: int
    screen_width: int
    screen_height: int


class ActionList:
    def __init__(self):
        self.action_list = []
        self.file_path = os.path.join(resources_dir, 'action_list.json')
        if exists(self.file_path):
            self.load_action_list()
        else:
            self.save_action_list()

    def add_action(self, action: Action):
        self.action_list.append(action)
        self.save_action_list()

    def load_action_list(self):
        if exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.loads(file.read())
            action_list = []
            for key in data:
                action_list.append(data[key])
            if console_log:
                print(data)
                print(action_list)
                print("Loaded action list.")
        else:
            if console_log:
                print('File does not exist: ' + self.file_path)

    def save_action_list(self):
        json_obj = dict()
        for index in range(len(self.action_list)):
            json_element = {
                str(index): json.loads(self.action_list[index].json())
            }
            json_obj.update(json_element)
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(json_obj, file, indent=6)
            if console_log:
                print("Saved action list.")


class TaskList:
    def __init__(self):
        self.task_list = []
        self.file_path = os.path.join(resources_dir, 'task_list.json')
        if exists(self.file_path):
            self.load_task_list()
        else:
            self.save_task_list()

    def add_task(self, task: Task):
        self.task_list.append(task)
        self.save_task_list()

    def load_task_list(self):
        if exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.loads(file.read())
            task_list = []
            for key in data:
                task_list.append(data[key])
            if console_log:
                print(data)
                print(task_list)
                print("Loaded task list.")
        else:
            if console_log:
                print('File does not exist: ' + self.file_path)

    def save_task_list(self):
        json_obj = dict()
        for index in range(len(self.task_list)):
            json_element = {
                str(index): json.loads(self.task_list[index].json())
            }
            json_obj.update(json_element)
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(json_obj, file, indent=6)
            if console_log:
                print("Saved task list.")


class ScheduleList:
    def __init__(self):
        self.schedule_list = []
        self.file_path = os.path.join(resources_dir, 'schedule_list.json')
        if exists(self.file_path):
            self.load_schedule_list()
        else:
            self.save_schedule_list()

    def add_schedule(self, schedule: Schedule):
        self.schedule_list.append(schedule)
        self.save_schedule_list()

    def load_schedule_list(self):
        if exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                data = json.loads(file.read())
            schedule_list = []
            for key in data:
                schedule_list.append(data[key])
            if console_log:
                print(data)
                print(schedule_list)
                print("Loaded schedule list.")
        else:
            if console_log:
                print('File does not exist: ' + self.file_path)

    def save_schedule_list(self, file_path: str = None):
        json_obj = dict()
        for index in range(len(self.schedule_list)):
            json_element = {
                str(index): json.loads(self.schedule_list[index].json())
            }
            json_obj.update(json_element)
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(json_obj, file, indent=6)
            if console_log:
                print("Saved schedule list.")


class TestModels:
    def __init__(self):
        self.action_list_obj = ActionList()
        self.task_list_obj = TaskList()
        self.schedule_list_obj = ScheduleList()

    def test_crud_model(self):
        test_action1 = {
            'id': 1,
            'name': 'say_hello',
            'code': ['print("Hello user!")'],
        }
        test_action2 = {
            'id': 2,
            'name': 'test_complete',
            'code': ['print("Test complete")'],
        }
        test_task = {
            'id': 1,
            'name': 'test_tasks',
            'task_dependency_id': 0,
            'action_id_list': [1, 2]
        }
        test_shedule = {
            'id': 1,
            'name': 'test_schedule',
            'schedule_dependency_id': 0,
            'task_id_list': [1]
        }
        test_action_obj1 = Action(**test_action1)
        test_action_obj2 = Action(**test_action2)
        self.action_list_obj.add_action(test_action_obj1)
        self.action_list_obj.add_action(test_action_obj2)
        test_task_obj = Task(**test_task)
        self.task_list_obj.add_task(test_task_obj)
        test_schedule1 = Schedule(**test_shedule)
        self.schedule_list_obj.add_schedule(test_schedule1)
        func_name = sys._getframe().f_code.co_name
        self.action_list_obj.load_action_list()
        self.task_list_obj.load_task_list()
        self.schedule_list_obj.load_schedule_list()
        if console_log:
            print("Test complete: "+func_name)


def main() -> None:
    """Main function"""
    test_obj = TestModels()
    test_obj.test_crud_model()


if __name__ == "__main__":
    main()
