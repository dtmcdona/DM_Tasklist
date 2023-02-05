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
import uuid
from pathlib import Path
from typing import List, Optional, Any, Union

from pydantic import BaseModel
from pydantic.types import Json

base_dir = Path(".").absolute()
resources_dir = base_dir / "resources"
if not resources_dir.is_dir():
    resources_dir = base_dir / "core" / "resources"
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
            obj_dir = resources_dir / "images"
            try:
                return Image(**input_dict), obj_dir
            except Exception:
                return None
        elif best_match.get("model") == "ScreenObject":
            obj_dir = resources_dir / "screen_data"
            try:
                return ScreenObject(**input_dict), obj_dir
            except Exception:
                return None
        elif best_match.get("model") == "ScreenData":
            obj_dir = resources_dir / "screen_data"
            try:
                return ScreenData(**input_dict), obj_dir
            except Exception:
                return None

    def store_resource(self) -> dict:
        file_name = f"{self.obj.id}.json"
        file_path = self.obj_dir / file_name
        response = {"data": f"Saved: {file_name}"}
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.obj.dict(), file, indent=6)
            logging.debug(response)
        return response

    def load_resource(self) -> dict:
        file_name = f"{self.obj.id}.json"
        file_path = self.obj_dir / file_name
        response = {"data": f"Loaded: {file_name}"}
        obj_json = None
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                obj_json = json.loads(file.read())
                logging.debug(obj_json)
        except OSError:
            response = {"data": f"File does not exist: {file_path}"}
            logging.debug(response)
        return obj_json

    def delete_resource(self) -> dict:
        file_name = f"{self.obj.id}.json"
        file_path = self.obj_dir / file_name
        response = {"data": f"Deleted: {file_path}"}
        try:
            file_path.unlink()
        except OSError:
            response = {"data": f"File does not exist: {file_path}"}
        logging.debug(response)
        return response


class JsonCollectionResource:
    def __init__(self, model_cls, testing=False):
        self.model_cls = model_cls
        test_dir = "test_" if testing else ""
        self.collection_dir = (
            resources_dir / f"{test_dir}{self.model_to_str()}s"
        )
        self.collection_dir.mkdir(exist_ok=True)

    def model_to_str(self) -> str:
        return {Action: "action", Task: "task", Schedule: "schedule"}.get(
            self.model_cls
        )

    def get_collection(self, obj_id: str) -> dict:
        try:
            file_path = self.collection_dir / obj_id
            with open(file_path, mode="r", encoding="utf-8") as f:
                obj = json.load(f)
            response = obj
            logging.debug(response)
        except OSError:
            response = {"data": f"{self.model_to_str()} not found."}
            logging.debug(response)
        return response

    def add_collection(
        self, obj: Union[Action, Task, Schedule]
    ) -> Union[Action, Task, Schedule]:
        try:
            ids = [
                file_path.name for file_path in self.collection_dir.iterdir()
            ]
            while obj.id in ids:
                obj.id = str(uuid.uuid4())
            file_path = self.collection_dir / obj.id
            with open(file_path, mode="w", encoding="utf-8") as f:
                json.dump(obj.dict(), f, indent=6)
            response = obj
            logging.debug(response)
        except OSError:
            response = {f"Error adding {self.model_to_str()} with id: {obj.id}"}
            logging.debug(response)
        return response

    def update_collection(
        self, obj_id: str, obj: Union[Action, Task, Schedule]
    ) -> Union[Action, Task, Schedule]:
        response = {f"Error adding {self.model_to_str()} with id: {obj.id}"}
        try:
            ids = [filename for filename in self.collection_dir.iterdir()]
            while obj.id in ids:
                obj.id = str(uuid.uuid4())
            file_path = self.collection_dir / obj.id
            with open(file_path, mode="w", encoding="utf-8") as f:
                json.dump(obj.dict(), f, indent=6)
            if obj_id != obj.id:
                old_file_path = self.collection_dir / obj_id
                old_file_path.unlink(missing_ok=True)
            response = obj
            logging.debug(f"Updated {self.model_to_str()} with id: {obj.id}")
        except OSError:
            response = {f"Error adding {self.model_to_str()} with id: {obj.id}"}
            logging.debug(response)
        return response

    def get_all_collections(self):
        return {
            file_path.name: json.load(open(file_path))
            for file_path in self.collection_dir.iterdir()
        }

    def delete_collection(self, obj_id: str) -> dict:
        response = {"data": f"Deleted {self.model_to_str()} with id: {obj_id}"}
        try:
            file_path = self.collection_dir / obj_id
            file_path.unlink()
        except FileNotFoundError:
            response = {
                "data": f"{self.model_to_str()} does not exist: {obj_id}"
            }
        logging.debug(response)
        return response
