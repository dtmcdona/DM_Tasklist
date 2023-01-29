"""
Models:
    Pydantic models
        - Actions - All actions that can be executed by the process controller
        - Tasks - An ordered collection of actions to execute with a configuration
        - Schedules - An ordered collection of tasks to execute
        - Screen Objects - Screen objects represent text, buttons, or GUI elements
        - Image - An image from the xvfb virtual display
        - Json Data - Abstract object for storing JSON data
        - Source - Represents an abstract data source stored in the file system
        - Captured Data - Represents any form of data that can be captured as relevant data
            for an action or task
        - Task Rank - Used to determine how efficient it completes a goal
        - Mouse position - Might be used in the future to track relative mouse x and y
            coordinates for different resolutions
    JSON resources
        - All CRUD operations for utilizing single json files
    JSON collection resources
        - All CRUD operations for utilizing collections of json files
"""
import datetime
import json
import logging
import os
import uuid
from os.path import exists
from pathlib import Path
from typing import List, Optional, Any, Union

from pydantic import BaseModel
from pydantic.types import Json

base_dir = Path(".").absolute()
resources_dir = os.path.join(base_dir, "resources")
if not os.path.isdir(resources_dir):
    resources_dir = os.path.join(base_dir, "core", "resources")
logging.basicConfig(level=logging.DEBUG)


class ExtendedBaseModel(BaseModel):
    @classmethod
    def get_field_names(cls, alias=False):
        return list(cls.schema(alias).get("properties").keys())


class Action(BaseModel):
    """Actions represent the smallest process of a task"""

    id: Optional[str] = str(uuid.uuid4())
    function: str
    x1: Optional[int] = None
    x2: Optional[int] = None
    y1: Optional[int] = None
    y2: Optional[int] = None
    images: Optional[List[str]] = []
    image_conditions: Optional[List[str]] = []
    variables: Optional[List[str]] = []
    variable_conditions: Optional[List[str]] = []
    comparison_values: Optional[List[str]] = []
    created_at: Optional[str] = datetime.datetime.now().isoformat()
    time_delay: Optional[float] = 0.0
    sleep_duration: Optional[float] = 0.0
    key_pressed: Optional[str] = None
    true_case: Optional[str] = "conditions_true"
    false_case: Optional[str] = "conditions_false"
    skip_to_id: Optional[str] = None
    error_case: Optional[str] = "error"
    num_repeats: Optional[int] = 0
    random_path: Optional[bool] = False
    random_range: Optional[int] = 0
    random_delay: Optional[float] = 0.0


class Task(BaseModel):
    """Tasks represent a collection of actions that complete a goal"""

    id: Optional[str] = str(uuid.uuid4())
    task_dependency_id: Optional[int] = None
    action_id_list: List[str] = []
    job_creation_delta_time: Optional[float] = 0.5
    max_num_celery_jobs: Optional[int] = 10
    conditionals: Optional[List[int]] = []
    early_result_available: Optional[List[bool]] = []
    fastest_timeline: Optional[List[float]] = []
    last_conditional_results: Optional[List[Json]] = []


class Schedule(BaseModel):
    """Schedule is a series of tasks to run over a given timeframe"""

    id: Optional[str] = str(uuid.uuid4())
    schedule_dependency_id: Optional[str] = None
    task_id_list: List[str] = []


class ScreenObject(ExtendedBaseModel):
    """Screen objects represent text, buttons, or GUI elements"""

    id: Optional[str] = str(uuid.uuid4())
    type: Optional[str] = "text"
    action_id: Optional[str] = None
    timestamp: Optional[str] = datetime.datetime.now().isoformat()
    text: str = ""
    x1: int
    y1: int
    x2: int
    y2: int


class ScreenData(ExtendedBaseModel):
    """Screen data is a collection for all the screen objects found and the
    screenshot is saved as a base 64 image"""

    id: Optional[str] = str(uuid.uuid4())
    timestamp: Optional[str] = datetime.datetime.now().isoformat()
    base64str: str
    screen_obj_ids: List[str]


class Image(ExtendedBaseModel):
    """Represents any picture image that needs to be stored via a 64 bit
    encoding"""

    id: Optional[str] = str(uuid.uuid4())
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

    id: str
    data: Json


class Source(BaseModel):
    """Represents an abstract data source stored in the file system"""

    id: str
    uri: str


class CapturedData(BaseModel):
    """Represents any form of data that can be captured as relevant data
    for an action or task"""

    id: str
    type: str
    source_id: str
    json_data_id: str
    schedule_id: str


class TaskRank(BaseModel):
    """Used to determine how efficient it completes a goal"""

    task_rank: int
    task_id: str
    delta_vars: List[float]
    duration: datetime.time


class MousePosition(BaseModel):
    """Might be used in the future to track relative mouse x and y coords for
    different resolutions"""

    action_id: str
    x: int
    y: int
    screen_width: int
    screen_height: int


class JsonResource:
    def __init__(self, resource_dict):
        self.obj, self.obj_dir = self.dict_to_model(resource_dict)

    def dict_to_model(self, input_dict: dict) -> Any:
        all_models = {
            "Image": Image.get_field_names(),
            "ScreenObject": ScreenObject.get_field_names(),
            "ScreenData": ScreenData.get_field_names(),
        }
        best_match = {}
        for model, model_fields in all_models.items():
            input_keys = input_dict.keys()
            percent_match = len(set(model_fields) & set(input_keys)) / float(
                len(set(model_fields) | set(input_keys))
            )
            new_match = {
                "model": model,
                "percent_match": percent_match,
            }
            if percent_match > 0:
                if not best_match:
                    best_match = new_match
                elif percent_match > best_match.get("percent_match"):
                    best_match = new_match
                    if percent_match == 1:
                        break

        if not best_match:
            return None
        elif best_match.get("model") == "Image":
            obj_dir = os.path.join(resources_dir, "images")
            try:
                return Image(**input_dict), obj_dir
            except Exception:
                return None
        elif best_match.get("model") == "ScreenObject":
            obj_dir = os.path.join(resources_dir, "screen_data")
            try:
                return ScreenObject(**input_dict), obj_dir
            except Exception:
                return None
        elif best_match.get("model") == "ScreenData":
            obj_dir = os.path.join(resources_dir, "screen_data")
            try:
                return ScreenData(**input_dict), obj_dir
            except Exception:
                return None

    def store_resource(self) -> dict:
        file_name = f"{self.obj.id}.json"
        file_path = os.path.join(self.obj_dir, file_name)
        response = {"data": f"Saved: {file_name}"}
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.obj.dict(), file, indent=6)
            logging.debug(response)
        return response

    def load_resource(self) -> dict:
        file_name = f"{self.obj.id}.json"
        file_path = os.path.join(self.obj_dir, file_name)
        response = {"data": f"Loaded: {file_name}"}
        obj_json = None
        if exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                obj_json = json.loads(file.read())
                logging.debug(obj_json)
        else:
            response = {"data": f"File does not exist: {file_path}"}
        logging.debug(response)
        return obj_json

    def delete_resource(self) -> dict:
        file_name = f"{self.obj.id}.json"
        file_path = os.path.join(self.obj_dir, file_name)
        response = {"data": f"Deleted: {file_path}"}
        if exists(file_path):
            os.remove(file_path)
        else:
            response = {"data": f"File does not exist: {file_path}"}
        logging.debug(response)
        return response


class JsonCollectionResource:
    def __init__(self, model_cls, testing=False):
        self.model_cls = model_cls
        self.json_collection = {}
        test_file = "test_" if testing else ""
        if self.model_cls == Action:
            self.file_path = os.path.join(
                resources_dir, f"{test_file}action_collection.json"
            )
        elif self.model_cls == Task:
            self.file_path = os.path.join(
                resources_dir, f"{test_file}task_collection.json"
            )
        elif self.model_cls == Schedule:
            self.file_path = os.path.join(
                resources_dir, f"{test_file}schedule_collection.json"
            )
        if exists(self.file_path):
            self.load_collection()
        else:
            self.save_collection()

    def model_to_str(self) -> str:
        if self.model_cls == Action:
            return "Action"
        elif self.model_cls == Task:
            return "Task"
        elif self.model_cls == Schedule:
            return "Schedule"

    def get_collection(self, obj_id: str) -> dict:
        obj = self.json_collection.get(obj_id)
        if obj:
            response = obj
        else:
            response = {"data": f"{self.model_to_str()} not found."}
        return response

    def add_collection(self, obj: Union[Action, Task, Schedule]) -> Union[Action, Task, Schedule]:
        response = {f"Error adding {self.model_to_str()} with id: {obj.id}"}
        if self.json_collection not in [None, {}]:
            ids = self.json_collection.keys()
            while obj.id in ids:
                obj.id = str(uuid.uuid4())

            self.json_collection[obj.id] = obj.dict()
            self.save_collection()
            response = obj
            logging.debug(f"Added {self.model_to_str()} with id: {obj.id}")
        else:
            self.json_collection = {obj.id: obj.dict()}
            response = obj
            self.save_collection()
            logging.debug(f"Added {self.model_to_str()} with id: {obj.id}")
        return response

    def update_collection(self, obj_id: str, obj: Union[Action, Task, Schedule]) -> Union[Action, Task, Schedule]:
        ids = self.json_collection.keys()
        if obj_id not in ids:
            response = {"data": "Invalid ID entered."}
            logging.debug(response)
            return response
        self.json_collection[obj_id] = obj.dict()
        self.save_collection()
        logging.debug(f"Updated {self.model_to_str()} with id: {obj_id}")
        return obj

    def load_collection(self) -> None:
        self.json_collection = {}
        if exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as file:
                self.json_collection = json.loads(file.read())
            logging.debug(self.json_collection)
            logging.debug(f"Loaded {self.model_to_str()} collection")
        else:
            logging.debug(
                f"{self.model_to_str()} does not exist: " + self.file_path
            )

    def save_collection(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(self.json_collection, file, indent=6)
            logging.debug(f"Saved {self.model_to_str()} collection")

    def delete_collection(self, obj_id: str) -> dict:
        response = {"data": f"Deleted {self.model_to_str()} with id: {obj_id}"}
        try:
            del self.json_collection[obj_id]
            logging.debug(response)
            self.save_collection()
        except KeyError:
            response = {
                "data": f"{self.model_to_str()} does not exist: {obj_id}"
            }
        finally:
            return response
