import datetime
import json
import os
import sys
from os.path import exists
from typing import Optional, List
from pydantic import BaseModel
from pydantic.types import Json

resources_dir = os.path.join(os.getcwd(), 'core/resources/')
console_log = False


class Action(BaseModel):
    id: Optional[int]
    name: str
    code: List[str]


class Task(BaseModel):
    id: Optional[int]
    name: str
    task_dependency_id: Optional[int]
    action_id_list: List[int] = []


class Schedule(BaseModel):
    id: Optional[int]
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
        self.file_path = os.path.join(resources_dir, 'action_list.json')
        self.action_list = {}
        if exists(self.file_path):
            self.load_action_list()
        else:
            self.save_action_list()

    def add_action(self, action: Action):
        response = {}
        if self.action_list not in [None, {}]:
            names = []
            for key in self.action_list:
                names.append(self.action_list[key].get('name'))
            if action.name not in names:
                action.id = len(self.action_list)
                self.action_list[str(action.id)] = action.dict()
                response = {'Data': 'Action added'}
            elif console_log:
                print("Action already exists.")
            else:
                response = {'Data': 'Action already exists'}
        else:
            self.action_list = {
                str(action.id): action.dict()
            }
            response = {'Data': 'Action added'}
        self.save_action_list()
        return response

    def load_action_list(self):
        self.action_list = {}
        if exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.action_list = json.loads(file.read())
            if console_log:
                print(self.action_list)
                print("Loaded action list.")
        else:
            if console_log:
                print('File does not exist: ' + self.file_path)

    def save_action_list(self):
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(self.action_list, file, indent=6)
            if console_log:
                print("Saved action list.")

    def delete_action(self, action_id: int):
        new_action_list = {}
        index = 0
        for key in self.action_list:
            if key == str(action_id):
                continue
            element = self.action_list[str(key)]
            element["id"] = index
            new_action_list[str(index)] = element
            index += 1
        self.action_list = new_action_list
        if console_log:
            print(f"Deleted action id: {action_id}")
        self.save_action_list()


class TaskList:
    def __init__(self):
        self.task_list = []
        self.file_path = os.path.join(resources_dir, 'task_list.json')
        if exists(self.file_path):
            self.load_task_list()
        else:
            self.save_task_list()

    def add_task(self, task: Task):
        response = {}
        if self.task_list not in [None, {}]:
            names = []
            for key in self.task_list:
                names.append(self.task_list[key].get('name'))
            if task.name not in names:
                task.id = len(self.task_list)
                self.task_list[str(task.id)] = task.dict()
                response = {'Data': 'Task added'}
            elif console_log:
                print("Task already exists.")
            else:
                response = {'Data': 'Task already exists'}
        else:
            self.task_list = {
                str(task.id): task.dict()
            }
            response = {'Data': 'Task added'}
        self.save_task_list()
        return response

    def load_task_list(self):
        self.task_list = {}
        if exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.task_list = json.loads(file.read())
            if console_log:
                print(self.task_list)
                print("Loaded task list.")
        else:
            if console_log:
                print('File does not exist: ' + self.file_path)

    def save_task_list(self):
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(self.task_list, file, indent=6)
            if console_log:
                print("Saved task list.")

    def delete_task(self, task_id: int):
        new_task_list = {}
        index = 0
        for key in self.task_list:
            if key == str(task_id):
                continue
            element = self.task_list[str(key)]
            element["id"] = index
            new_task_list[str(index)] = element
            index += 1
        self.task_list = new_task_list
        if console_log:
            print(f"Deleted task id: {task_id}")
        self.save_task_list()


class ScheduleList:
    def __init__(self):
        self.schedule_list = []
        self.file_path = os.path.join(resources_dir, 'schedule_list.json')
        if exists(self.file_path):
            self.load_schedule_list()
        else:
            self.save_schedule_list()

    def add_schedule(self, schedule: Schedule):
        if self.schedule_list not in [None, {}]:
            names = []
            for key in self.schedule_list:
                names.append(self.schedule_list[key].get('name'))
            if schedule.name not in names:
                schedule.id = len(self.schedule_list)
                self.schedule_list[str(schedule.id)] = schedule.dict()
            elif console_log:
                print("Schedule already exists.")
        else:
            self.schedule_list = {
                str(schedule.id): schedule.dict()
            }
        self.save_schedule_list()

    def load_schedule_list(self):
        self.schedule_list = {}
        if exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.schedule_list = json.loads(file.read())
            if console_log:
                print(self.schedule_list)
                print("Loaded schedule list.")
        else:
            if console_log:
                print('File does not exist: ' + self.file_path)

    def save_schedule_list(self):
        with open(self.file_path, "w", encoding='utf-8') as file:
            json.dump(self.schedule_list, file, indent=6)
            if console_log:
                print("Saved schedule list.")

    def delete_schedule(self, schedule_id: int):
        new_schedule_list = {}
        index = 0
        for key in self.schedule_list:
            if key == str(schedule_id):
                continue
            element = self.schedule_list[str(key)]
            element["id"] = index
            new_schedule_list[str(index)] = element
            index += 1
        self.schedule_list = new_schedule_list
        if console_log:
            print(f"Deleted schedule id: {schedule_id}")
        self.save_schedule_list()


class TestModels:
    def __init__(self):
        self.action_list_obj = ActionList()
        self.task_list_obj = TaskList()
        self.schedule_list_obj = ScheduleList()

    def test_crud_model(self):
        test_action1 = {
            'id': 0,
            'name': 'say_hello',
            'code': ['print("Hello user!")'],
        }
        test_action2 = {
            'id': 1,
            'name': 'test_complete',
            'code': ['print("Test complete")'],
        }
        test_task = {
            'id': 0,
            'name': 'test_tasks',
            'task_dependency_id': 0,
            'action_id_list': [1, 2]
        }
        test_shedule = {
            'id': 0,
            'name': 'test_schedule',
            'schedule_dependency_id': 0,
            'task_id_list': [1]
        }
        test_action_obj1 = Action(**test_action1)
        test_action_obj2 = Action(**test_action2)
        self.action_list_obj.add_action(test_action_obj1)
        self.action_list_obj.add_action(test_action_obj2)
        print(self.action_list_obj)
        test_task_obj = Task(**test_task)
        self.task_list_obj.add_task(test_task_obj)
        test_schedule1 = Schedule(**test_shedule)
        self.schedule_list_obj.add_schedule(test_schedule1)
        func_name = sys._getframe().f_code.co_name
        self.action_list_obj.load_action_list()
        self.task_list_obj.load_task_list()
        self.schedule_list_obj.load_schedule_list()
        # self.action_list_obj.delete_action(0)
        if console_log:
            print("Test complete: "+func_name)


def main() -> None:
    """Main function"""
    test_obj = TestModels()
    test_obj.test_crud_model()


if __name__ == "__main__":
    main()
