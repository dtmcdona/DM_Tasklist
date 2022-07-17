import logging
import random
import time

from pyautogui import moveTo, click, keyUp, keyDown
from core import models
from core import random_mouse
from core import screen_reader


CONDITIONALS = [
    "greater_than",
    "less_than",
    "equals",
    "if",
    "if_not",
    "if_image_present",
]
RESULTS = [
    "execute_action",
    "skip_action",
    "set_action_name"
    "skip_to_name",
    "sleep_and_repeat",
    "sleep",
    "set_variable",
    "increment_variable",
    "decrement_variable",
    "switch_task",
    "end_task",
    "spawn_process",
    "repeat",
]


def evaluate_conditional(condition, variable_value, comparison_value=None):
    if condition not in CONDITIONALS:
        pass
    if comparison_value:
        if condition == "greater_than":
            if variable_value > comparison_value:
                return True
            else:
                return False
        elif condition == "less_than":
            if variable_value < comparison_value:
                return True
            else:
                return False
        elif condition == "equals":
            if variable_value == comparison_value:
                return True
            else:
                return False
    if condition == "if" and variable_value or condition == "if_not" and not variable_value:
        return True
    elif condition == "if" or condition == "if_not" and variable_value:
        return False
    if "if_image_present":
        x, y = screen_reader.image_search(variable_value)
        if x == -1 or y == -1:
            return False
        return True


def process_action(action: models.Action):
    response = {'data': f'Error with action_id:{action.get("id")}'}
    if action.get("time_delay") not in [0.0, None]:
        delay = float(action["time_delay"])
        time.sleep(delay)
    if action.get("function") not in ["", None]:
        x = -1
        y = -1
        x1 = None
        x2 = None
        y1 = None
        y2 = None
        random_range = 0 if action.get("random_range") in [0, None] else action["random_range"]
        random_delay = 0.0 if action.get("random_delay") in [0.0, None] else float(action["random_delay"])
        if action.get("images") not in [[], None]:
            needle_file_name = action["images"][0]
            if action.get("images")[1] not in ["", None]:
                haystack_file_name = action["images"][1]
            else:
                haystack_file_name = ""
            percent_similarity = .9
            x, y = screen_reader.image_search(needle_file_name=needle_file_name,
                                              haystack_file_name=haystack_file_name,
                                              percent_similarity=percent_similarity)
        if action.get("x2") not in [-1, None] and action.get("y2") not in [-1, None]:
            if action.get("x1") in [-1, None] or action.get("y1") in [-1, None]:
                logging.error(response)
                return response
            x1 = action["x1"]
            y1 = action["y1"]
            x2 = action["x2"]
            y2 = action["y2"]
            x_range = x2 - x1
            y_range = y2 - y1
            if action.get("random_range") not in [0, None]:
                # This fixes any errors with random mouse click range with region click
                if x_range > random_range * 2:
                    x1 = x1 + random_range
                    x2 = x2 - random_range
                elif x_range < random_range and x_range > 4:
                    random_range = 1
                    x1 = x1 + random_range
                    x2 = x2 - random_range
                else:
                    random_range = 0
                if y_range > random_range * 2:
                    y1 = y1 + random_range
                    y2 = y2 - random_range
                elif y_range < random_range and y_range > 4:
                    random_range = 1
                    y1 = y1 + random_range
                    y2 = y2 - random_range
                else:
                    random_range = 0
            x = random.randrange(x1, x2)
            y = random.randrange(y1, y2)
        elif action.get("x1") not in [-1, None] and action.get("y1") not in [-1, None]:
            x = action["x1"]
            y = action["y1"]
        if action["function"] == 'click' or action["function"] == 'click_image':
            if x == -1 or y == -1:
                logging.debug(response)
                return response
            if action.get("random_path") not in [False, None]:
                random_mouse.random_move(x=x, y=y)
            if action.get("random_range") not in [0, None] or action.get("random_delay") not in [0.0, None]:
                random_mouse.random_click(x=x, y=y, rand_range=random_range, delay_duration=random_delay)
            else:
                click(x, y)
            response = {'data': f'Mouse clicked: ({x}, {y})'}
        elif action["function"] == 'move_to' or action["function"] == 'move_to_image':
            if x == -1 or y == -1:
                logging.debug(response)
                return response
            if action.get("random_path") not in [False, None]:
                random_mouse.random_move(x=x, y=y)
            else:
                moveTo(x=x, y=y)
            response = {'data': f'Mouse moved to: ({x}, {y})'}
        elif action["function"] == 'key_pressed' and action.get("key_pressed") not in ["", None]:
            action_key = action["key_pressed"]
            keyDown(action_key)
            time.sleep(1)
            keyUp(action_key)
            response = {'data': f'Key pressed {action_key}'}
        elif action["function"] == 'capture_screen_data':
            if x1 and x2 and y1 and y2:
                action_id = action.get("id")
                response = screen_reader.capture_screen_data(x1=x1, y1=y1, x2=x2, y2=y2, action_id=action_id)
    return response


def action_controller(action: models.Action):
    repeat = True if action.get("repeat") not in [False, None] else False
    num_repeats = action.get("num_repeats") if action.get("num_repeats") not in [0, None] else 0
    # Repeat action until num_repeats is 0 or repeat is false
    image_conditions = action.get("image_conditions")
    variable_conditions = action.get("variable_conditions")
    conditionals_true = True
    while conditionals_true:
        if image_conditions:
            images = action.get("images")
            for condition in image_conditions:
                conditionals_true = conditionals_true and evaluate_conditional(condition, images)
        if variable_conditions:
            variables = action.get("variables")
            comparison_values = action.get("comparison_values")
            for count, ele in enumerate(variable_conditions):
                if len(comparison_values) > count + 1:
                    conditionals_true = conditionals_true and evaluate_conditional(variable_conditions[count],
                                                                             variables[(count * 2) + 1])
                else:
                    conditionals_true = conditionals_true and evaluate_conditional(variable_conditions[count],
                                                                             variables[(count * 2) + 1],
                                                                             comparison_values[count])
        if not conditionals_true:
            response = {'data': 'False conditional(s)'}
            break

        response = process_action(action)
        if num_repeats <= 0 or not repeat:
            break
        elif num_repeats > 0:
            num_repeats = num_repeats - 1
    return response
