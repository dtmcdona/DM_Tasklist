"""
Process Controller
    This is the main logic for each different actions with a display.
    It typically uses a xvfb virtual display for pyautogui to operate
    either locally or in a docker container.  Screen data is captured
    using cv2 and pytesseract with a screenshot.  Screen data then can
    be compared with different conditions and perform a result.  This
    can also be used in conjunction with a Task Manager to perform an
    ordered or re-ordered list of actions in a task.
"""
import base64
import datetime
import json
import logging
import os
from pathlib import Path
import random
import subprocess
import time
import uuid
from typing import Tuple, Optional, Any

import cv2
import enchant
import numpy as np
import pytesseract

from . import fast_api_endpoints as api
from . import api_resources, models, random_mouse, constants

"""Virtual display setup has to be setup before pyautogui is imported"""
import Xlib.display
from pyvirtualdisplay.display import Display

disp = Display(visible=True, size=(1920, 1080), backend="xvfb", use_xauth=True)
disp.start()
import pyautogui

"""Virtual display"""
pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ["DISPLAY"])

image_dir = models.resources_dir / "images"
screen_width, screen_height = pyautogui.size()
logging.basicConfig(level=logging.DEBUG)


class ActionStrategy:
    def __init__(self, action: models.Action):
        self.action = action
        self.response = {"data": f'Error with action_id:{action.get("id")}'}

    def execute_action(self, time_delay) -> None:
        if not self.action.get("function"):
            return
        if time_delay and self.action.get("time_delay", 0.0) != 0.0:
            delay = float(self.action["time_delay"])
            time.sleep(delay)


class KeyAction(ActionStrategy):
    def execute_action(self, time_delay) -> None:
        super().execute_action(time_delay)
        action_key = self.action["key_pressed"]
        keypress(action_key)
        self.response = {"data": f"Key pressed {action_key}"}


class MouseAction(ActionStrategy):
    def __init__(self, action: models.Action):
        super().__init__(action)
        self.x, self.y = -1, -1
        self.x1 = self.action.get("x1")
        self.x2 = self.action.get("x2")
        self.y1 = self.action.get("y1")
        self.y2 = self.action.get("y2")

    def execute_action(self, time_delay) -> None:
        super().execute_action(time_delay)
        random_range = self.action.get("random_range", 0)
        random_delay = float(self.action.get("random_delay", 0.0))
        if self.x2 is not None and self.y2 is not None:
            if self.x1 is None or self.y1 is None:
                logging.error(self.response)
                return

            x_range = self.x2 - self.x1
            y_range = self.y2 - self.y1

            if random_range != 0:
                if x_range > random_range * 2:
                    self.x1 += random_range
                    self.x2 -= random_range
                elif x_range < random_range and x_range > 4:
                    random_range = 1
                    self.x1 += random_range
                    self.x2 -= random_range
                else:
                    random_range = 0

                if y_range > random_range * 2:
                    self.y1 += random_range
                    self.y2 -= random_range
                elif y_range < random_range and y_range > 4:
                    random_range = 1
                    self.y1 += random_range
                    self.y2 -= random_range
                else:
                    random_range = 0

            self.x = random.randrange(self.x1, self.x2)
            self.y = random.randrange(self.y1, self.y2)
        elif self.x1 is not None and self.y1 is not None:
            self.x = self.x1
            self.y = self.y1

        function = self.action.get("function")

        if function in ("click", "click_image", "click_image_region"):
            if self.x == -1 or self.y == -1:
                logging.debug(self.response)
                return

            if self.action.get("random_path"):
                random_mouse.random_move(x=self.x, y=self.y)

            if self.action.get("random_range") or self.action.get(
                "random_delay"
            ):
                random_mouse.random_click(
                    x=self.x,
                    y=self.y,
                    rand_range=random_range,
                    delay_duration=random_delay,
                )
            else:
                pyautogui.click(self.x, self.y)

            self.response = {"data": f"Mouse clicked: ({self.x}, {self.y})"}
        elif function in ("move_to", "move_to_image"):
            if self.x == -1 or self.y == -1:
                logging.debug(self.response)
                return

            if self.action.get("random_path"):
                random_mouse.random_move(x=self.x, y=self.y)
            else:
                pyautogui.moveTo(x=self.x, y=self.y)

            self.response = {"data": f"Mouse moved to: ({self.x}, {self.y})"}


class ImageAction(MouseAction):
    def execute_action(self, time_delay) -> None:
        needle_file_name = self.action["images"][0]
        percent_similarity = 0.9

        if self.action.get("function") == "click_image_region":
            haystack_image = self.action.get("haystack_image")
            if haystack_image:
                haystack_file_name = haystack_image
                delete_haystack_file = False
            else:
                haystack_file_name = screenshot_snip(
                    self.x1, self.y2, self.x2, self.y2
                )
                delete_haystack_file = True

            self.x, self.y = image_search(
                needle_file_name=needle_file_name,
                haystack_file_name=haystack_file_name,
                percent_similarity=percent_similarity,
                delete_haystack_file=delete_haystack_file,
            )

            if self.x != -1 and self.y != -1:
                self.x += self.x1
                self.y += self.y1
        else:
            haystack_image = self.action.get("haystack_image")
            haystack_file_name = haystack_image if haystack_image else ""

            self.x, self.y = image_search(
                needle_file_name=needle_file_name,
                haystack_file_name=haystack_file_name,
                percent_similarity=percent_similarity,
                delete_haystack_file=False,
            )
        super().execute_action(time_delay)


class CaptureDataAction(MouseAction):
    def execute_action(self, time_delay) -> None:
        super().execute_action(time_delay)
        if (
            self.x1 is not None
            and self.x2 is not None
            and self.y1 is not None
            and self.y2 is not None
        ):
            action_id = self.action.get("id")
            self.response = capture_screen_data(
                x1=self.x1,
                y1=self.y1,
                x2=self.x2,
                y2=self.y2,
                action_id=action_id,
            )


def mouse_up(mouse_button: str = "left"):
    """Mouse button up"""
    pyautogui.mouseUp(button=mouse_button)


def mouse_down(mouse_button: str = "left"):
    """Mouse button down"""
    pyautogui.mouseDown(button=mouse_button)


def mouse_pos() -> Tuple[int, int]:
    """Mouse (x, y) position"""
    return pyautogui.position()


def open_browser(url: str) -> dict:
    """Open a browser window and return a screenshot"""
    try:
        browser_options = (
            "--disable-extensions --no-sandbox --disable-gpu "
            "--disable-extension --desktop-window-1080p"
        )
        cmd = f'google-chrome {browser_options} "{url}" 2> /dev/null'
        subprocess.Popen(cmd, shell=True)
    except Exception as ex:
        logging.debug(ex)
    # Time it takes for webbrowser to open and render to xvfb
    black_screen = models.resources_dir / "screenshot" / "black_screen.json"
    response = {}
    time.sleep(1)
    logging.debug(black_screen)
    if black_screen.is_file():
        with open(black_screen, "r", encoding="utf-8") as file:
            black_screen_json = json.loads(file.read())
            response = screen_shot_response()
            while response.get("data") == black_screen_json.get("data"):
                time.sleep(1)
                response = screen_shot_response()
                logging.debug(
                    response.get("data") == black_screen_json.get("data")
                )
    return response


def evaluate_conditional(
    condition: str, variable_value: str, comparison_value: Optional[str] = None
) -> Optional[bool]:
    """Comparison value is provided by user and the variable_value is from
    capture_screen_data action.  This is used to compare the two values
    and return a boolean result."""
    if condition not in constants.CONDITIONALS:
        pass
    if condition in ("greater_than", "less_than", "equals"):
        if not comparison_value:
            return False
        if condition == "greater_than":
            if float(variable_value) > float(comparison_value):
                return True
            else:
                return False
        elif condition == "less_than":
            if float(variable_value) < float(comparison_value):
                return True
            else:
                return False
        elif condition == "equals":
            if variable_value == comparison_value:
                return True
            else:
                return False
    if (
        condition == "if"
        and variable_value
        or condition == "if_not"
        and not variable_value
    ):
        return True
    elif condition == "if" or condition == "if_not" and variable_value:
        return False
    if condition == "if_image_present":
        """Check to see if image is present before doing action"""
        x, y = image_search(variable_value, comparison_value, False)
        if x == -1 or y == -1:
            return False
        return True


def process_action(action: models.Action, time_delay=True) -> dict:
    """Process a given action based on its function and return a response.
    This is the main logic for each different actions with a virtual display."""
    if not isinstance(action, dict):
        action = action.dict()

    function = action.get("function")
    action_handler = {
        "click": MouseAction,
        "click_image": ImageAction,
        "click_image_region": ImageAction,
        "move_to": MouseAction,
        "move_to_image": ImageAction,
        "key_pressed": KeyAction,
        "capture_screen_data": CaptureDataAction,
    }.get(function)(action)
    action_handler.execute_action(time_delay)
    return action_handler.response


def get_conditionals_result(
    action: models.Action, screenshot_file: str = None
) -> bool:
    """Evaluates conditionals for an action"""
    image_conditions = action.get("image_conditions")
    variable_conditions = action.get("variable_conditions")

    if image_conditions:
        images = action.get("images")
        haystack_image = action.get("haystack_image")

        for condition in image_conditions:
            needle_file_name = images[0]
            haystack_file_name = haystack_image or screenshot_file

            if not evaluate_conditional(
                condition, needle_file_name, haystack_file_name
            ):
                return False
    elif variable_conditions:
        variables = action.get("variables")
        comparison_values = action.get("comparison_values")

        for count, condition in enumerate(variable_conditions):
            value_index = (count * 2) + 1
            value = variables[value_index]
            compare_value = (
                comparison_values[count]
                if len(comparison_values) > count + 1
                else None
            )

            if not evaluate_conditional(condition, value, compare_value):
                return False
    else:
        return False

    return True


def action_controller(
    action: models.Action, prefetched_condition_result: bool = None
) -> dict:
    """This controller manages different outcomes of the action's conditional
    and then processes the given action"""
    if not isinstance(action, dict):
        action = action.dict()

    if action.get("function") not in constants.ACTIONS:
        response = {"data": f'Action has invalid function: {action.get("id")}'}
        logging.debug(response)
        return response

    num_repeats = action.get("num_repeats", 0)

    while True:
        if action.get("function") == "capture_screen_data":
            response = process_action(action)
            conditionals_true = (
                prefetched_condition_result or get_conditionals_result(action)
            )

            if "repeat" in action.get(f"{conditionals_true}_case".lower()):
                if (
                    action.get(f"{conditionals_true}_case".lower())
                    == "sleep_and_repeat"
                ):
                    time.sleep(action.get("sleep_duration"))
                num_repeats = 1
            else:
                if action.get(f"{conditionals_true}_case".lower()) == "sleep":
                    time.sleep(action.get("sleep_duration"))
                response = {
                    "data": action.get(f"{conditionals_true}_case".lower())
                }
                break
        else:
            response = process_action(action)

        if num_repeats <= 0:
            break

        num_repeats -= 1
        if num_repeats <= 0:
            break

    return response


def keypress(key_input: str, duration: float = 0.05) -> dict:
    """Presses the given key for a duration"""
    response = {"data": "Invalid input"}
    valid_input = pyautogui.KEYBOARD_KEYS
    if key_input.lower() in valid_input:
        pyautogui.press(key_input.lower())
        response = {"data": f"Key pressed {key_input}"}
    else:
        combo_key_array = key_input.split("|")
        if len(combo_key_array) > 1:
            for combo_key in combo_key_array:
                pyautogui.keyDown(combo_key)
            time.sleep(duration)
            for combo_key in combo_key_array:
                pyautogui.keyUp(combo_key)
            response = {"data": f"Key pressed {key_input}"}
        else:
            key_array = list(key_input)
            if len(key_array) > 1:
                for key in key_array:
                    pyautogui.keyDown(key)
                    time.sleep(duration)
                    pyautogui.keyUp(key)
                response = {"data": f"Key pressed {key_input}"}
    logging.debug(response)
    return response


def mouse_click(x: int, y: int) -> dict:
    """Moves and clicks the mouse at point (x, y)"""
    screen_width, screen_height = pyautogui.size()
    response = {"data": "Invalid input"}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        pyautogui.click(x, y)
        response = {"data": f"Moved mouse to ({x},{y})"}
    logging.debug(response)
    return response


def mouse_move(x: int, y: int, duration: float = 0.0) -> dict:
    """Moves the mouse to (x, y)"""
    screen_width, screen_height = pyautogui.size()
    response = {"data": "Invalid input"}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        pyautogui.moveTo(x, y, duration)
        response = {"data": f"Moved mouse to ({x},{y})"}
    logging.debug(response)
    return response


def image_search(
    needle_file_name: str,
    haystack_file_name: str = "",
    percent_similarity: float = 0.9,
    delete_haystack_file: bool = True,
) -> Tuple[int, int]:
    """Search for 'needle' image in a 'haystack' image and return (x, y) coords"""
    needle_file_path = str(image_dir / needle_file_name)
    needle = cv2.imread(needle_file_path, cv2.IMREAD_UNCHANGED)
    grayscale_needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)
    if haystack_file_name in ["", None]:
        image_id = uuid.uuid4()
        haystack_file_path = str(image_dir / f"{image_id}.png")
        pyautogui.screenshot(haystack_file_path)
    else:
        haystack_file_path = str(image_dir / haystack_file_name)
    haystack = cv2.imread(haystack_file_path, cv2.IMREAD_UNCHANGED)
    grayscale_haystack = cv2.cvtColor(haystack, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(
        grayscale_haystack, grayscale_needle, cv2.TM_CCOEFF_NORMED
    )
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    """Max location has the best match with max_val to be % accuracy"""
    width = needle.shape[1]
    height = needle.shape[0]
    # bottom_right = (max_loc[0] + width, max_loc[1] + height)
    """Threshold is the % accuracy compared to original needle"""
    threshold = percent_similarity
    yloc, xloc = np.where(result >= threshold)
    """Keep track of all matches and identify unique cases"""
    matches = []
    """Delete haystack image since it is a representation of current screen"""
    if delete_haystack_file:
        Path(haystack_file_path).unlink(missing_ok=True)
    if len(xloc) > 0:
        # logging.debug("There are {0} total matches in the haystack.".format(len(xloc)))
        for (x, y) in zip(xloc, yloc):
            """Twice to ensure singles are kept after picking unique cases"""
            matches.append([int(x), int(y), int(width), int(height)])
            matches.append([int(x), int(y), int(width), int(height)])
        """Grouping function"""
        matches, weights = cv2.groupRectangles(matches, 1, 0.2)
        # logging.debug("There are {0} unique matches in the haystack.".format(len(matches)))
        """Assuming the first match was a good match"""
        if len(matches) > 0:
            center_x = matches[0][0] + width / 2
            center_y = matches[0][1] + height / 2
            return center_x, center_y
    else:
        logging.debug("There are no matches.")
        return -1, -1


def capture_screen_data(
    x1: int, y1: int, x2: int, y2: int, action_id: str, testing: bool = False
) -> dict:
    """This function captures data within the region within (x1, y1) and (x2, y2).
    The data is then processed, stored and returned as a string."""
    response = {"data": "Screen data not captured"}
    screenshot_id = str(uuid.uuid4())
    screenshot_path = str(
        models.resources_dir / "screenshot" / f"{screenshot_id}.png"
    )
    pyautogui.screenshot(screenshot_path)
    if testing:
        test_image = str(models.resources_dir / "images" / "test_image.png")
        img = cv2.imread(test_image)
    else:
        img = cv2.imread(screenshot_path)
    width = x2 - x1
    height = y2 - y1
    if width != screen_width and height != screen_height:
        cv2.imwrite(screenshot_path, img[y1:y2, x1:x2, :])
        img = cv2.imread(screenshot_path)
    """Prepare screenshot for Pytesseract OCR"""
    png_img = cv2.imencode(".png", img)
    b64_string = base64.b64encode(png_img[1]).decode("utf-8")
    (h, w) = img.shape[:2]
    img = cv2.resize(img, (w * 5, h * 5))
    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thr = cv2.threshold(gry, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    cv2.imwrite(screenshot_path, thr)
    """There might be some case where inverting the image gives better results"""
    # screenshot_path = resources_dir / f"invert_{screenshot_id}.png"
    # inverted_thr = cv2.bitwise_not(thr)
    # cv2.imwrite(screenshot_path, inverted_thr)
    # inverted_img_data = pytesseract.image_to_data(thr)
    img_data = pytesseract.image_to_data(thr)
    timestamp = datetime.datetime.now().isoformat()
    Path(screenshot_path).unlink(missing_ok=True)

    count = 0
    screen_obj_ids = []
    screen_obj_values = []
    english_dict = enchant.Dict("en_US")
    for index, word_data in enumerate(img_data.splitlines()):
        """This loops through all words and numbers found within the region
        and stores in screen_object json files."""
        if index == 0:
            continue
        word = word_data.split()
        if len(word) == 12:
            if word[11].isnumeric() or english_dict.check(word[11]):
                word_id = str(uuid.uuid4())
                text = word[11]
                screen_obj_ids.append(word_id)
                screen_obj_values.append(text)
                word_x1, word_y1, word_width, word_height = (
                    int(word[6]),
                    int(word[7]),
                    int(word[8]),
                    int(word[9]),
                )
                if (
                    action_id
                    in api_resources.storage.action_collection.get_all_collections()
                ):
                    word_action_id = action_id
                else:
                    word_action_id = None
                data_type = (
                    "button"
                    if action_id
                    in api_resources.storage.action_collection.get_all_collections()
                    else "text"
                )
                """Screen objects are data that store information from 
                    GUI elements and/or actions"""
                screen_object_json = {
                    "id": f"{word_id}",
                    "type": data_type,
                    "action_id": word_action_id,
                    "timestamp": timestamp,
                    "text": text,
                    "x1": x1 + word_x1,
                    "y1": y1 + word_y1,
                    "x2": x1 + word_x1 + word_width,
                    "y2": y1 + word_y1 + word_height,
                }
                response = models.JsonResource(
                    screen_object_json
                ).store_resource()
                logging.debug(response)
                if response.get("data").startswith("Saved"):
                    count = count + 1
                else:
                    logging.debug(response)
    """Screen Data JSON files are mainly kept for debugging purposes"""
    screen_data_json = {
        "id": screenshot_id,
        "timestamp": timestamp,
        "base64str": b64_string,
        "screen_obj_ids": screen_obj_ids,
    }
    if count > 0:
        response = models.JsonResource(screen_data_json).store_resource()
        logging.debug(response)
    if count == 0:
        response = {"data": "No screen objects found"}
        logging.warning(response)
    elif testing:
        variables = [
            ", ".join(screen_obj_ids),
            ", ".join(screen_obj_values),
        ]
        test_result_dict = {
            "function": "capture_screen_data",
            "variables": variables,
            "x1": x1,
            "x2": x2,
            "y1": y1,
            "y2": y2,
            "screen_data_id": screenshot_id,
            "timestamp": timestamp,
            "base64str": b64_string,
            "screen_obj_ids": screen_obj_ids,
        }
        return test_result_dict
    elif (
        action_id
        not in api_resources.storage.action_collection.get_all_collections()
    ):
        """Create new action"""
        variables = [
            ", ".join(screen_obj_ids),
            ", ".join(screen_obj_values),
        ]
        new_action = {
            "function": "capture_screen_data",
            "variables": variables,
            "x1": x1,
            "x2": x2,
            "y1": y1,
            "y2": y2,
        }
        new_action_obj = models.Action(**new_action)
        response = api.add_action(new_action=new_action_obj)
    else:
        """Update action with captured screen info"""
        updated_action = api.get_action(action_id=action_id)
        variables = [
            ", ".join(screen_obj_ids),
            ", ".join(screen_obj_values),
        ]
        logging.debug(updated_action)
        updated_action["variables"] = variables
        updated_action_obj = models.Action(**updated_action)
        response = api.update_action(
            action_id=action_id, new_action=updated_action_obj
        )
    return response


def screen_snip(
    x1: int, y1: int, x2: int, y2: int, image: models.Image
) -> dict:
    """This function is used to capture a section of the screen and
    store in resources/images as png and json files"""
    base64str = image.base64str
    decoded64str = base64.b64decode(base64str)
    image_id = uuid.uuid4()
    image_path = str(image_dir / f"{image_id}.png")
    with open(image_path, "wb") as f:
        f.write(decoded64str)
    img = cv2.imread(image_path)
    cv2.imwrite(image_path, img[y1:y2, x1:x2, :])
    snip_img = cv2.imread(image_path)
    snip_png_img = cv2.imencode(".png", snip_img)
    b64_string = base64.b64encode(snip_png_img[1]).decode("utf-8")
    height = snip_img.shape[0]
    width = snip_img.shape[1]
    """Build json object"""
    image_json = {
        "id": f"{image_id}",
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "width": width,
        "height": height,
        "base64str": f"{b64_string}",
    }
    image_obj = models.Image(**image_json)
    response = models.JsonResource(image_json).store_resource()
    if response.get("data").startswith("Saved"):
        response = image_obj
    logging.debug(response)
    return response


def screenshot_snip(x1: int, y1: int, x2: int, y2: int) -> Path:
    img, image_path = screen_shot_image()
    cv2.imwrite(str(image_path), img[y1:y2, x1:x2, :])
    return image_path


def screen_shot_image() -> (Any, Path):
    """This function uses the current display and returns an image"""
    timestamp = round(time.time() * 1000)
    screenshot_path = (
        models.resources_dir / "screenshot" / f"screenshot_{timestamp}.png"
    )
    pyautogui.screenshot(screenshot_path)
    img = cv2.imread(str(screenshot_path))
    return img, screenshot_path


def screen_shot_response() -> dict:
    """This function uses the current display and returns a base-64 image"""
    img, screenshot_path = screen_shot_image()
    png_img = cv2.imencode(".png", img)
    b64_string = base64.b64encode(png_img[1]).decode("utf-8")
    screenshot_path.unlink()
    response = {"data": b64_string}
    return response


def save_screenshot() -> str:
    """This is used by the task manager to pass screenshots to the celery workers"""
    file_name = f"{uuid.uuid4()}.png"
    file_path = image_dir / file_name
    pyautogui.screenshot(file_path)
    return file_name
