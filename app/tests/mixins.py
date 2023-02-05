import json
from logging import DEBUG
import os
import pathlib
import shutil
from shutil import rmtree
from itertools import product
from typing import List

import pytest
from core import api_resources, fast_api_endpoints, constants, models

from core import redis_cache


class ModelMixin:
    test_action = {
        "id": "test_capture_screen_data",
        "function": "capture_screen_data",
        "x1": 0,
        "y1": 0,
        "x2": 132,
        "y2": 32,
        "images": [
            "test_image.png",
        ],
    }
    test_task = {"id": "test_task", "action_id_list": [1]}
    test_task_obj = None
    base_dir = pathlib.Path(".").absolute()
    resources_dir = os.path.join(base_dir, "resources")
    if not os.path.isdir(resources_dir):
        resources_dir = os.path.join(base_dir, "core", "resources")
    test_screen_data = os.path.join(
        models.resources_dir, "screen_data", "test_screen_data.json"
    )
    test_screen_data_json = None
    test_screen_data_obj = os.path.join(
        models.resources_dir, "screen_data", "test_screen_data_object.json"
    )
    test_screen_data_obj_json = None
    delete_image_files = []
    delete_screen_data_files = []
    test_image = None
    black_screen_json = None
    black_screen = os.path.join(
        models.resources_dir, "screenshot", "black_screen.json"
    )
    action_collection = None
    task_collection = None

    @classmethod
    def setup_class(cls):
        cls.action_collection = models.JsonCollectionResource(
            models.Action, True
        )
        cls.task_collection = models.JsonCollectionResource(models.Task, True)
        api_resources.storage = api_resources.APICollections(
            action_collection=cls.action_collection,
            task_collection=cls.task_collection,
            logging_level=DEBUG,
        )
        test_action_obj = models.Action(**cls.test_action)
        test_task_obj = models.Task(**cls.test_task)
        cls.add_action(test_action_obj)
        cls.add_task(test_task_obj)
        if os.path.exists(cls.test_screen_data):
            with open(cls.test_screen_data, "r", encoding="utf-8") as file:
                cls.test_screen_data_json = json.loads(file.read())
        if os.path.exists(cls.test_screen_data_obj):
            with open(cls.test_screen_data_obj, "r", encoding="utf-8") as file:
                cls.test_screen_data_obj_json = json.loads(file.read())
        if os.path.exists(cls.black_screen):
            with open(cls.black_screen, "r", encoding="utf-8") as file:
                cls.black_screen_json = json.loads(file.read())
        x1 = cls.test_screen_data_obj_json["x1"]
        y1 = cls.test_screen_data_obj_json["y1"]
        x2 = cls.test_screen_data_obj_json["x2"]
        y2 = cls.test_screen_data_obj_json["y2"]
        image_width = x2 - x1
        image_height = y2 - y1
        image_kwargs = {
            "is_static_position": True,
            "base64str": cls.test_screen_data_json["base64str"],
            "width": image_width,
            "height": image_height,
            "x1": cls.test_screen_data_obj_json["x1"],
            "y1": cls.test_screen_data_obj_json["y1"],
            "x2": cls.test_screen_data_obj_json["x2"],
            "y2": cls.test_screen_data_obj_json["y2"],
        }
        cls.test_image = models.Image(**image_kwargs)
        cls.delete_image_files.append(cls.test_image.id)
        cls.test_image_path = os.path.join(
            models.resources_dir, "images", "test_image.png"
        )
        cls.test_image_copy_path = os.path.join(
            models.resources_dir, "images", "test_image_copy.png"
        )
        cls.test_image_copy2_path = os.path.join(
            models.resources_dir, "images", "test_image_copy2.png"
        )
        cls.test_image_copy3_path = os.path.join(
            models.resources_dir, "images", "test_image_copy3.png"
        )
        cls.delete_image_files.append("test_image_copy")
        cls.delete_image_files.append("test_image_copy2")
        mouse_positions = [
            [18, 18, None, None],
            [18, 18, 36, 36],
        ]
        rand_ranges = [0, 18, 36]
        rand_mouse_positions = product(mouse_positions, rand_ranges)
        key_presses = [None, "0"]
        for action_function in constants.ACTIONS:
            if action_function != "capture_screen_data":
                if (
                    action_function != "key_pressed"
                    and "image" not in action_function
                ):
                    for position, rand_range in rand_mouse_positions:
                        new_test_action = {
                            "function": action_function,
                            "x1": position[0],
                            "y1": position[1],
                            "x2": position[2],
                            "y2": position[3],
                            "random_range": rand_range,
                        }
                        test_action_obj = models.Action(**new_test_action)
                        cls.add_action(test_action_obj)
                elif action_function == "move_to_image":
                    new_test_action = {
                        "function": action_function,
                        "images": [
                            "test_image_copy.png",
                            "test_image_copy.png",
                        ],
                        "x1": None,
                        "y1": None,
                        "x2": None,
                        "y2": None,
                    }
                    test_action_obj = models.Action(**new_test_action)
                    cls.add_action(test_action_obj)
                elif action_function == "click_image":
                    new_test_action = {
                        "function": action_function,
                        "images": [
                            "test_image_copy2.png",
                            "test_image_copy2.png",
                        ],
                        "x1": None,
                        "y1": None,
                        "x2": None,
                        "y2": None,
                    }
                    test_action_obj = models.Action(**new_test_action)
                    cls.add_action(test_action_obj)
                elif action_function != "key_pressed":
                    for key in key_presses:
                        new_test_action = {
                            "function": action_function,
                            "key_pressed": key,
                        }
                        test_action_obj = models.Action(**new_test_action)
                        cls.add_action(test_action_obj)
        cls.test_task = {
            "id": "test_task",
            "action_id_list": [key for key in cls.get_action_collection().keys()],
        }
        cls.test_task_obj = models.Task(**cls.test_task)
        cls.update_task(cls.test_task_obj.id, cls.test_task_obj)

    @pytest.fixture(autouse=True)
    def setup_picture_files(self):
        if not os.path.exists(self.test_image_copy_path):
            shutil.copy(self.test_image_path, self.test_image_copy_path)
        if not os.path.exists(self.test_image_copy2_path):
            shutil.copy(self.test_image_path, self.test_image_copy2_path)
        if not os.path.exists(self.test_image_copy3_path):
            shutil.copy(self.test_image_path, self.test_image_copy3_path)

    @classmethod
    def teardown_class(cls):
        redis_cache.rc.flushdb()
        rmtree(cls.action_collection.collection_dir)
        rmtree(cls.task_collection.collection_dir)
        file_types = ["png", "json"]
        for image_id in cls.delete_image_files:
            for file_type in file_types:
                test_image = os.path.join(
                    models.resources_dir, "images", f"{image_id}.{file_type}"
                )
                if os.path.exists(test_image):
                    os.remove(test_image)

        for screen_data_id in cls.delete_screen_data_files:
            test_image = os.path.join(
                models.resources_dir, "screen_data", f"{screen_data_id}.json"
            )
            if os.path.exists(test_image):
                os.remove(test_image)
        cls.clear_images()

    def add_actions_to_task(self) -> None:
        self.test_task = {
            "id": "test_task",
            "action_id_list": self.get_action_ids(),
        }
        self.test_task_obj = models.Task(**self.test_task)
        self.update_task(1, self.test_task_obj)

    def get_action_ids(self) -> List[int]:
        return [key for key in self.get_action_collection().keys()]

    @staticmethod
    def clear_images():
        image_dir = os.path.join(models.resources_dir, "images")
        for file_name in os.listdir(image_dir):
            if file_name not in ("test_image.json", "test_image.png"):
                file_path = os.path.join(image_dir, file_name)
                os.remove(file_path)

    @staticmethod
    def add_action(action) -> dict:
        return api_resources.storage.add_action(action)

    @staticmethod
    def get_action(action_id) -> models.Action:
        return api_resources.storage.get_action(action_id)

    @staticmethod
    def get_action_collection():
        return api_resources.storage.get_action_collection()

    @staticmethod
    def update_action(action_id, action) -> models.Action:
        return api_resources.storage.update_action(action_id, action)

    @staticmethod
    def get_task(task_id) -> models.Task:
        return api_resources.storage.get_task(task_id)

    @staticmethod
    def add_task(task) -> dict:
        return api_resources.storage.add_task(task)

    @staticmethod
    def update_task(task_id, task) -> models.Task:
        return api_resources.storage.update_task(task_id, task)

    @staticmethod
    def get_task_collection():
        return api_resources.storage.get_task_collection()
