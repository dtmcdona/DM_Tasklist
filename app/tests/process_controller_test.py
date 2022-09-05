import json
import os
import pathlib
import shutil
import uuid

import pytest

from core import constants, models, process_controller


class TestProcessController:
    conditional_test_data = [
        ("greater_than", 2, 1, True),
        ("less_than", 1, 2, True),
        ("equals", 1, 1, True),
        ("if", 1, 2, True),
        ("if_not", None, None, True),
        ("greater_than", 1, 2, False),
        ("less_than", 2, 1, False),
        ("equals", 1, 2, False),
        ("if", None, None, False),
        ("if_not", 1, 1, False),
    ]
    test_action = {
        "id": 0,
        "name": "test_capture_screen_data",
        "function": "capture_screen_data",
        "x1": 0,
        "y1": 0,
        "x2": 132,
        "y2": 32,
        "images": [
            "test_image.png",
        ]
    }
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

    @classmethod
    def setup_class(cls):
        cls.action_collection = models.JsonCollectionResource(models.Action, True)
        test_action_obj = models.Action(**cls.test_action)
        cls.action_collection.add_collection(test_action_obj)
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

    @classmethod
    def teardown_class(cls):
        os.remove(cls.action_collection.file_path)
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

    def generate_actions_without_condition(self):
        mouse_positions = [
            [18, 18, None, None],
            [18, 18, 36, 36],
        ]
        rand_ranges = [
            0, 18, 36
        ]
        key_presses = [
            None, "0"
        ]
        test_image_path = os.path.join(
            models.resources_dir, "images", "test_image.png"
        )
        test_image_copy_path = os.path.join(
            models.resources_dir, "images", "test_image_copy.png"
        )
        test_image2_copy_path = os.path.join(
            models.resources_dir, "images", "test_image_copy2.png"
        )
        shutil.copy(test_image_path, test_image_copy_path)
        shutil.copy(test_image_path, test_image2_copy_path)
        for action_function in constants.ACTIONS:
            if action_function != "capture_screen_data":
                if action_function != "key_pressed" and "image" not in action_function:
                    for position in mouse_positions:
                        for rand_range in rand_ranges:
                            new_test_action = {
                                "name": str(uuid.uuid4()),
                                "function": action_function,
                                "x1": position[0],
                                "y1": position[1],
                                "x2": position[2],
                                "y2": position[3],
                                "random_range": rand_range
                            }
                            test_action_obj = models.Action(**new_test_action)
                            self.action_collection.add_collection(test_action_obj)
                elif action_function == "move_to_image":
                    new_test_action = {
                        "name": str(uuid.uuid4()),
                        "function": action_function,
                        "images": ["test_image_copy.png", "test_image_copy.png"],
                        "x1": None,
                        "y1": None,
                        "x2": None,
                        "y2": None,
                    }
                    test_action_obj = models.Action(**new_test_action)
                    self.action_collection.add_collection(test_action_obj)
                elif action_function == "click_image":
                    new_test_action = {
                        "name": str(uuid.uuid4()),
                        "function": action_function,
                        "images": ["test_image_copy2.png", "test_image_copy2.png"],
                        "x1": None,
                        "y1": None,
                        "x2": None,
                        "y2": None,
                    }
                    test_action_obj = models.Action(**new_test_action)
                    self.action_collection.add_collection(test_action_obj)
                elif action_function != "key_pressed":
                    for key in key_presses:
                        new_test_action = {
                            "name": str(uuid.uuid4()),
                            "function": action_function,
                            "key_pressed": key
                        }
                        test_action_obj = models.Action(**new_test_action)
                        self.action_collection.add_collection(test_action_obj)

    @pytest.mark.parametrize("condition, variable_value, comparison_value, expected", conditional_test_data)
    def test_evaluate_conditional(self, condition, variable_value, comparison_value, expected):
        assert process_controller.evaluate_conditional(condition, variable_value, comparison_value) == expected

    def test_action_controller(self):
        self.generate_actions_without_condition()
        for action_id in self.action_collection.json_collection:
            action = self.action_collection.get_collection(int(action_id))
            if action.get("function") == "capture_screen_data":
                continue
            response = process_controller.action_controller(action)
            if "move" in action.get("function"):
                assert "Mouse moved to:" in response["data"]
            elif "click" in action.get("function"):
                assert "Mouse clicked:" in response["data"]
            elif action.get("function") == "key_pressed":
                assert response == {"data": f"Key pressed {action.key_pressed}"}

    def test_screen_snip(self):
        response = process_controller.screen_snip(0, 0, 132, 32, self.test_image)
        self.delete_image_files.append(response.id)
        assert response.width == 132
        assert response.height == 32
        assert response.is_static_position
        assert "iVBORw0KGgoAAAANSUhEUgAAAIQAAAAgCAIAAABc" in response.base64str

    def test_capture_screen_data(self):
        response = process_controller.capture_screen_data(0, 0, 132, 32, 0, True)
        self.delete_screen_data_files.append(response.get("screen_data_id"))
        self.delete_screen_data_files.append(response.get("variables")[0])
        assert response.get("function") == "capture_screen_data"
        assert "Parameters" in response.get("variables")
        assert response.get("x1") == 0
        assert response.get("y1") == 0
        assert response.get("x2") == 132
        assert response.get("y2") == 32
        assert "iVBORw0KGgoAAAANSUhEUgAAAIQAAAAgCAIAAABc" in response.get("base64str")

    def test_capture_screen_data__empty(self):
        response = process_controller.capture_screen_data(0, 0, 2, 2, 0, True)
        assert response == {"data": "No screen objects found"}

    def test_screen_shot(self):
        assert process_controller.screen_shot() == self.black_screen_json
