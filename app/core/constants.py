"""
Actions:
    All possible actions that can be performed by the process_controller

Conditionals:
    All possible conditions with analyzing the screen data

Results:
    All possible results of conditions being True/False
"""
from typing import List

ACTIONS: List[str] = [
    "click",
    "click_right",
    "click_image",
    "click_image_region",
    "move_to",
    "move_to_image",
    "drag_to",
    "key_pressed",
    "capture_screen_data",
]

CONDITIONALS: List[str] = [
    "greater_than",
    "less_than",
    "equals",
    "if",
    "if_not",
    "if_image_present",
]

RESULTS: List[str] = [
    "continue",
    "set_action_id",
    "skip_to_id",
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
