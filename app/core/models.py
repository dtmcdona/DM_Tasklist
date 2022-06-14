import datetime
import json
import os
import sys
import uuid
from os.path import exists
from pathlib import Path
from pydantic import BaseModel
from pydantic.types import Json
from typing import Optional, List


base_dir = Path('.').absolute()
resources_dir = os.path.join(base_dir, 'resources')
if not os.path.isdir(resources_dir):
    resources_dir = os.path.join(base_dir, 'core', 'resources')
console_log = False


class Action(BaseModel):
    """Actions represent the smallest process of a task"""
    id: Optional[int]
    name: str
    function: str
    x1: Optional[int] = None
    x2: Optional[int] = None
    y1: Optional[int] = None
    y2: Optional[int] = None
    images: Optional[List[str]] = []
    image_conditions: Optional[List[str]] = []
    variables: Optional[List[str]] = []
    variable_condition: Optional[List[str]] = []
    created_at: Optional[str] = datetime.datetime.now().isoformat()
    time_delay: Optional[float] = 0.0
    key_pressed: Optional[str] = None
    true_case: Optional[str] = "conditions_true"
    false_case: Optional[str] = "conditions_false"
    error_case: Optional[str] = "error"
    repeat: Optional[bool] = False
    num_repeats: Optional[int] = 0
    random_path: Optional[bool] = False
    random_range: Optional[int] = 0
    random_delay: Optional[float] = 0.0


class Task(BaseModel):
    """Tasks represent a collection of actions that complete a goal"""
    id: Optional[int]
    name: str
    task_dependency_id: Optional[int] = None
    action_id_list: List[int] = []


class Schedule(BaseModel):
    """Schedule is a series of tasks to run over a given timeframe"""
    id: Optional[int]
    name: str
    schedule_dependency_id: Optional[int] = None
    task_id_list: List[int] = []


class ScreenObject(BaseModel):
    """Screen objects represent text, buttons, or GUI elements"""
    id: Optional[str] = uuid.uuid4()
    type: Optional[str] = "text"
    action_id: Optional[int] = None
    timestamp: Optional[str] = datetime.datetime.now().isoformat()
    text: str = ""
    x1: int
    y1: int
    x2: int
    y2: int


class ScreenData(BaseModel):
    """Screen data is a collection for all the screen objects found and the screenshot is saved as a base 64 image"""
    id: Optional[str] = uuid.uuid4()
    timestamp: Optional[str] = datetime.datetime.now().isoformat()
    base64str: str
    screen_obj_ids: List[str]


class Conditional(BaseModel):
    """Conditionals represent the logic to check for any requirements needed to run an action or task"""
    id: Optional[str] = uuid.uuid4()
    condition: str
    sleep_if_false: Optional[bool] = False
    sleep_duration: Optional[float] = 0
    sleep_retries: Optional[int] = 0
    success_result: Json = {"data": "Success"}
    failure_result: Json = {"data": "Failure"}
    timestamp: str = datetime.datetime.now().isoformat()


class Image(BaseModel):
    """Represents any picture image that needs to be stored via a 64 bit encoding"""
    id: Optional[str] = uuid.uuid4()
    width: Optional[int] = 1920
    height: Optional[int] = 1080
    timestamp: Optional[str] = datetime.datetime.now().isoformat()
    is_static_position: Optional[bool] = True
    x1: Optional[int] = 0
    y1: Optional[int] = 0
    x2: Optional[int] = 1920
    y2: Optional[int] = 1920
    base64str: str


class JsonData(BaseModel):
    """Abstract data type for storing unique data"""
    id: int
    data: Json


class Source(BaseModel):
    """Represents an abstract data source stored in the file system"""
    id: int
    uri: str


class CapturedData(BaseModel):
    """Represents any form of data that can be captured as relevant data for an action or task"""
    id: int
    type: str
    source_id: int
    json_data_id: int
    schedule_id: int


class TaskRank(BaseModel):
    """Used to determine how efficient it completes a goal"""
    task_rank: int
    task_id: int
    delta_vars: List[float]
    duration: datetime.time


class MousePosition(BaseModel):
    """Might be used in the future to track relative mouse x and y coords for different resolutions"""
    action_id: int
    x: int
    y: int
    screen_width: int
    screen_height: int


class ScreenDataResource:
    """Collection of screen data with store, load and delete functions"""
    def __init__(self):
        self.screen_data_dir = os.path.join(resources_dir, 'screen_data')

    def store_screen_object(self, screen_object: ScreenObject):
        file_name = f"{screen_object.id}.json"
        file_path = os.path.join(self.screen_data_dir, file_name)
        response = {"data": f"Saved screen data: {file_name}"}
        with open(file_path, "w", encoding='utf-8') as file:
            json.dump(screen_object.dict(), file, indent=6)
            if console_log:
                print(f"Saved screen data: {file_name}")
        return response

    def store_screen_data(self, screen_data: ScreenData):
        file_name = f"{screen_data.id}.json"
        file_path = os.path.join(self.screen_data_dir, file_name)
        response = {"data": f"Saved screen data: {file_name}"}
        with open(file_path, "w", encoding='utf-8') as file:
            json.dump(screen_data.dict(), file, indent=6)
            if console_log:
                print(f"Saved screen data: {file_name}")
        return response

    def load_screen_data(self, screen_data_id: str):
        file_name = f"{screen_data_id}.json"
        file_path = os.path.join(self.screen_data_dir, file_name)
        screen_data = {}
        if exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                screen_data = json.loads(file.read())
                if console_log:
                    print(screen_data)
                    print(f"Loaded screen data: {file_name}")
        elif console_log:
            print('File does not exist: ' + file_path)
        return screen_data

    def delete_screen_data(self, screen_data_id: str):
        file_name = f"{screen_data_id}.json"
        file_path = os.path.join(self.screen_data_dir, file_name)
        response = {"data": f"File does not exist: {file_path}"}
        if exists(file_path):
            os.remove(os.path.join(self.screen_data_dir, file_path))
            response = {"data": f"Deleted screen data: {file_name}"}
            if console_log:
                print(f"Deleted screen data: {file_name}")
        elif console_log:
            print(f"File does not exist: {file_path}")
        return response


class ImageResource:
    """Collection of images with store, load and delete functions"""
    def __init__(self):
        self.image_dir = os.path.join(resources_dir, 'images')

    def store_image(self, image: Image):
        file_name = f"{image.id}.json"
        file_path = os.path.join(self.image_dir, file_name)
        response = {"data": f"Saved image: {file_name}"}
        with open(file_path, "w", encoding='utf-8') as file:
            json.dump(image.dict(), file, indent=6)
            if console_log:
                print(f"Saved image: {file_name}")
        return response

    def load_image(self, image_id: str):
        file_name = f"{image_id}.json"
        file_path = os.path.join(self.image_dir, file_name)
        image = {}
        if exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                image = json.loads(file.read())
                if console_log:
                    print(image)
                    print(f"Loaded image: {file_name}")
        elif console_log:
            print('File does not exist: ' + file_path)
        return image

    def delete_image(self, image_id: str):
        file_name = f"{image_id}.json"
        file_path = os.path.join(self.image_dir, file_name)
        response = {"data": f"File does not exist: {file_path}"}
        if exists(file_path):
            os.remove(os.path.join(self.image_dir, file_path))
            response = {"data": f"Deleted image: {file_name}"}
            if console_log:
                print(f"Deleted image: {file_name}")
        elif console_log:
            print(f"File does not exist: {file_path}")
        return response


class ActionList:
    """Collection of all actions entered into the system"""
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
                self.save_action_list()
                response = action
            else:
                index = names.index(action.name)
                action.id = index
                response = self.update_action(index, action)
        else:
            action.id = 0
            self.action_list = {
                "0": action.dict()
            }
            response = action
            self.save_action_list()
        return response

    def update_action(self, index: int, action: Action):
        self.action_list[str(index)] = action.dict()
        self.save_action_list()
        return action

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
        if action_id >= len(self.action_list) or action_id < 0:
            response = {'Data': f'Action does not exist'}
            return response
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
        response = {'Data': f'Deleted action id: {action_id}'}
        return response


class TaskList:
    """Collection of all tasks entered into the system"""
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
                response = task
                self.save_task_list()
            else:
                index = names.index(task.name)
                task.id = index
                response = self.update_task(index, task)
        else:
            task.id = 0
            self.task_list = {
                str(task.id): task.dict()
            }
            response = task
            self.save_task_list()
        return response

    def update_task(self, index: int, task: Task):
        self.task_list[str(index)] = task.dict()
        self.save_task_list()
        return task

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
    """Collection of all schedules entered into the system"""
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
    """Used to test actions, tasks, and schedule lists"""
    def __init__(self):
        self.action_list_obj = ActionList()
        self.task_list_obj = TaskList()
        self.schedule_list_obj = ScheduleList()

    def test_crud_model(self):
        test_action1 = {
            'id': 0,
            'name': 'test_move_to',
            'function': 'move_to',
            'x1': 0,
            'y1': 0
        }
        test_action2 = {
            'id': 1,
            'name': 'test_click',
            'function': 'click',
            'x1': 0,
            'y1': 0
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


def test_models() -> None:
    """Test function"""
    test_obj = TestModels()
    test_obj.test_crud_model()


if __name__ == "__main__":
    test_models()
