import pytest

from core import constants, models, process_controller
from .mixins import ModelMixin


class TestProcessController(ModelMixin):
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

    @pytest.mark.parametrize(
        "condition, variable_value, comparison_value, expected",
        conditional_test_data,
    )
    def test_evaluate_conditional(
        self, condition, variable_value, comparison_value, expected
    ):
        assert (
            process_controller.evaluate_conditional(
                condition, variable_value, comparison_value
            )
            == expected
        )

    def test_action_controller(self):
        action_collection = self.get_action_collection()
        for action_id in action_collection:
            action = self.get_action(action_id)
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
        response = process_controller.screen_snip(
            0, 0, 132, 32, self.test_image
        )
        self.delete_image_files.append(response.id)
        assert response.width == 132
        assert response.height == 32
        assert response.is_static_position
        assert "iVBORw0KGgoAAAANSUhEUgAAAIQAAAAgCAIAAABc" in response.base64str

    def test_capture_screen_data(self):
        response = process_controller.capture_screen_data(
            0, 0, 132, 32, 0, True
        )
        self.delete_screen_data_files.append(response.get("screen_data_id"))
        self.delete_screen_data_files.append(response.get("variables")[0])
        assert response.get("function") == "capture_screen_data"
        assert "Parameters" in response.get("variables")
        assert response.get("x1") == 0
        assert response.get("y1") == 0
        assert response.get("x2") == 132
        assert response.get("y2") == 32
        assert "iVBORw0KGgoAAAANSUhEUgAAAIQAAAAgCAIAAABc" in response.get(
            "base64str"
        )

    def test_capture_screen_data__empty(self):
        response = process_controller.capture_screen_data(0, 0, 2, 2, 0, True)
        assert response == {"data": "No screen objects found"}

    def test_screen_shot(self):
        assert process_controller.screen_shot_response() == self.black_screen_json
