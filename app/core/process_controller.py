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
import pathlib
import random
import subprocess
import time
import uuid

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

base_dir = pathlib.Path(".").absolute()
resources_dir = os.path.join(base_dir, "resources")
if not os.path.isdir(resources_dir):
    resources_dir = os.path.join(base_dir, "core", "resources")
image_dir = os.path.join(resources_dir, "images")
screen_width, screen_height = pyautogui.size()
logging.basicConfig(level=logging.DEBUG)


def mouse_up(mouse_button="left"):
    """Mouse button up"""
    pyautogui.mouseUp(button=mouse_button)


def mouse_down(mouse_button="left"):
    """Mouse button down"""
    pyautogui.mouseDown(button=mouse_button)


def mouse_pos():
    """Mouse (x, y) position"""
    return pyautogui.position()


def open_browser(url: str):
    """Open a browser window"""
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
    black_screen = os.path.join(
        models.resources_dir, "screenshot", "black_screen.json"
    )
    response = {}
    time.sleep(1)
    logging.debug(black_screen)
    if os.path.exists(black_screen):
        with open(black_screen, "r", encoding="utf-8") as file:
            black_screen_json = json.loads(file.read())
            response = screen_shot()
            while response.get("data") == black_screen_json.get("data"):
                time.sleep(1)
                response = screen_shot()
                logging.debug(
                    response.get("data") == black_screen_json.get("data")
                )
    return response


def evaluate_conditional(condition, variable_value, comparison_value=None):
    """Comparison value is provided by user and the variable_value is from
    capture_screen_data action"""
    if condition not in constants.CONDITIONALS:
        pass
    if condition in ("greater_than", "less_than", "equals"):
        if not comparison_value:
            return False
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


def process_action(action: models.Action):
    """Process a given action based on its function"""
    response = {"data": f'Error with action_id:{action.get("id")}'}
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
        random_range = (
            0
            if action.get("random_range") in [0, None]
            else action["random_range"]
        )
        random_delay = (
            0.0
            if action.get("random_delay") in [0.0, None]
            else float(action["random_delay"])
        )
        if action.get("images") not in [[], None]:
            needle_file_name = action["images"][0]
            if len(action.get("images")) > 1 and action.get("images")[1] not in ["", None]:
                haystack_file_name = action["images"][1]
            else:
                haystack_file_name = ""
            percent_similarity = 0.9
            x, y = image_search(
                needle_file_name=needle_file_name,
                haystack_file_name=haystack_file_name,
                percent_similarity=percent_similarity,
                delete_haystack_file=False
            )
        if action.get("x2") not in [-1, None] and action.get("y2") not in [
            -1,
            None,
        ]:
            if action.get("x1") in [-1, None] or action.get("y1") in [
                -1,
                None,
            ]:
                logging.error(response)
                return response
            x1 = action["x1"]
            y1 = action["y1"]
            x2 = action["x2"]
            y2 = action["y2"]
            x_range = x2 - x1
            y_range = y2 - y1
            if action.get("random_range") not in [0, None]:
                # This fixes any errors with random mouse click range with
                # region click
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
        elif action.get("x1") not in [-1, None] and action.get("y1") not in [
            -1,
            None,
        ]:
            x = action["x1"]
            y = action["y1"]
        if action["function"] == "click" or action["function"] == "click_image":
            if x == -1 or y == -1:
                logging.debug(response)
                return response
            if action.get("random_path") not in [False, None]:
                random_mouse.random_move(x=x, y=y)
            if action.get("random_range") not in [0, None] or action.get(
                    "random_delay"
            ) not in [0.0, None]:
                random_mouse.random_click(
                    x=x,
                    y=y,
                    rand_range=random_range,
                    delay_duration=random_delay,
                )
            else:
                pyautogui.click(x, y)
            response = {"data": f"Mouse clicked: ({x}, {y})"}
        elif (
                action["function"] == "move_to"
                or action["function"] == "move_to_image"
        ):
            if x == -1 or y == -1:
                logging.debug(response)
                return response
            if action.get("random_path") not in [False, None]:
                random_mouse.random_move(x=x, y=y)
            else:
                pyautogui.moveTo(x=x, y=y)
            response = {"data": f"Mouse moved to: ({x}, {y})"}
        elif action["function"] == "key_pressed" and action.get(
                "key_pressed"
        ) not in [
            "",
            None,
        ]:
            action_key = action["key_pressed"]
            keypress(action_key)
            response = {"data": f"Key pressed {action_key}"}
        elif action["function"] == "capture_screen_data":
            if x1 and x2 and y1 and y2:
                action_id = action.get("id")
                response = capture_screen_data(
                    x1=x1, y1=y1, x2=x2, y2=y2, action_id=action_id
                )
    return response


def get_conditionals_result(action: models.Action, screenshot_file: str = None):
    conditionals_result = True
    image_conditions = action.get("image_conditions")
    variable_conditions = action.get("variable_conditions")
    if image_conditions:
        """Image conditionals are specific to png information"""
        images = action.get("images")
        for condition in image_conditions:
            needle_file_name = images[0]
            if images[1] not in ["", None]:
                haystack_file_name = action["images"][1]
            else:
                haystack_file_name = screenshot_file
            conditionals_result = conditionals_result and evaluate_conditional(
                condition, needle_file_name, haystack_file_name
            )
    elif variable_conditions:
        """Variable conditionals are specific to OCR values compared to user input"""
        variables = action.get("variables")
        comparison_values = action.get("comparison_values")
        for count, ele in enumerate(variable_conditions):
            if len(comparison_values) > count + 1:
                conditionals_result = (
                    conditionals_result
                    and evaluate_conditional(
                        variable_conditions[count],
                        variables[(count * 2) + 1],
                    )
                )
            else:
                conditionals_result = (
                    conditionals_result
                    and evaluate_conditional(
                        variable_conditions[count],
                        variables[(count * 2) + 1],
                        comparison_values[count],
                    )
                )
    else:
        conditionals_result = False
    return conditionals_result


def action_controller(action: models.Action, prefetched_condition_result: bool = None):
    """This controller manages different outcomes of the action's conditional
    and then processes the given action"""
    if action.get("function") not in constants.ACTIONS:
        response = {"data": f'Action has invalid function: {action.get("id")}'}
        logging.debug(response)
        return response
    num_repeats = (
        action.get("num_repeats")
        if action.get("num_repeats") not in [0, None]
        else 0
    )
    """Repeat action until num_repeats is 0 or repeat is false"""
    conditionals_true = True
    check_conditional = (
        True if action.get("function") == "capture_screen_data" else False
    )
    while conditionals_true:
        if check_conditional:
            """Capture and analyze screen information then process conditional case"""
            response = process_action(action)
            if prefetched_condition_result:
                conditionals_true = prefetched_condition_result
            else:
                conditionals_true = get_conditionals_result(action)
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
                response = {"data": action.get(f"{conditionals_true}_case".lower())}
                break
        else:
            """Action without conditional"""
            response = process_action(action)
        """Break out of loop if no repeats"""
        if num_repeats <= 0:
            break
        elif num_repeats > 0:
            num_repeats = num_repeats - 1
            if num_repeats <= 0:
                break

    return response


def keypress(key_input: str, duration: float = 0.05):
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


def mouse_click(x: int, y: int):
    """Moves and clicks the mouse at point (x, y)"""
    screen_width, screen_height = pyautogui.size()
    response = {"data": "Invalid input"}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        pyautogui.click(x, y)
        response = {"data": f"Moved mouse to ({x},{y})"}
    logging.debug(response)
    return response


def mouse_move(x: int, y: int, duration: float = 0.0):
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
        delete_haystack_file: bool = True
):
    """Search for 'needle' image in a 'haystack' image and return (x, y) coords"""
    print(needle_file_name)
    needle_file_path = os.path.join(image_dir, needle_file_name)
    needle = cv2.imread(needle_file_path, cv2.IMREAD_UNCHANGED)
    grayscale_needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)
    if haystack_file_name in ["", None]:
        image_id = uuid.uuid4()
        haystack_file_path = os.path.join(image_dir, f"{image_id}.png")
        pyautogui.screenshot(haystack_file_path)
    else:
        haystack_file_path = os.path.join(image_dir, haystack_file_name)
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
    if delete_haystack_file and os.path.exists(haystack_file_path):
        os.remove(haystack_file_path)
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
        x1: int, y1: int, x2: int, y2: int, action_id: int, testing: bool = False
):
    """This function captures data within the region within (x1, y1) and (x2, y2)"""
    response = {"data": "Screen data not captured"}
    screenshot_id = str(uuid.uuid4())
    base_dir = pathlib.Path(".").absolute()
    resources_dir = os.path.join(base_dir, "resources", "screenshot")
    if not os.path.isdir(resources_dir):
        resources_dir = os.path.join(
            base_dir, "core", "resources", "screenshot"
        )
    screenshot_path = os.path.join(resources_dir, f"{screenshot_id}.png")
    pyautogui.screenshot(screenshot_path)
    if testing:
        test_image = os.path.join(
            models.resources_dir, "images", "test_image.png"
        )
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
    # screenshot_path = os.path.join(resources_dir, f'invert_{screenshot_id}.png')
    # inverted_thr = cv2.bitwise_not(thr)
    # cv2.imwrite(screenshot_path, inverted_thr)
    # inverted_img_data = pytesseract.image_to_data(thr)
    img_data = pytesseract.image_to_data(thr)
    timestamp = datetime.datetime.now().isoformat()
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)

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
                        action_id >= len(api_resources.storage.action_collection.json_collection)
                        or action_id < 0
                ):
                    word_action_id = None
                else:
                    word_action_id = action_id
                data_type = (
                    "text"
                    if action_id >= len(api_resources.storage.action_collection.json_collection)
                       or action_id < 0
                    else "button"
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
            "name": datetime.datetime.now().isoformat(),
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
            action_id >= len(api_resources.storage.action_collection.json_collection) or action_id < 0
    ):
        """Create new action"""
        variables = [
            ", ".join(screen_obj_ids),
            ", ".join(screen_obj_values),
        ]
        new_action = {
            "name": datetime.datetime.now().isoformat(),
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


def screen_snip(x1: int, y1: int, x2: int, y2: int, image: models.Image):
    """This function is used to capture a section of the screen and
    store in resources/images as png and json files"""
    base_dir = pathlib.Path(".").absolute()
    image_dir = os.path.join(base_dir, "resources", "images")
    if not os.path.isdir(image_dir):
        image_dir = os.path.join(base_dir, "core", "resources", "images")
    base64str = image.base64str
    decoded64str = base64.b64decode(base64str)
    image_id = uuid.uuid4()
    image_path = os.path.join(image_dir, f"{image_id}.png")
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


def screen_shot():
    """This function uses the current display and returns a base-64 image"""
    timestamp = round(time.time() * 1000)
    base_dir = pathlib.Path(".").absolute()
    resources_dir = os.path.join(base_dir, "resources", "screenshot")
    if not os.path.isdir(resources_dir):
        resources_dir = os.path.join(
            base_dir, "core", "resources", "screenshot"
        )
    screenshot_path = os.path.join(resources_dir, f"screenshot_{timestamp}.png")
    pyautogui.screenshot(screenshot_path)
    img = cv2.imread(screenshot_path)
    png_img = cv2.imencode(".png", img)
    b64_string = base64.b64encode(png_img[1]).decode("utf-8")
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
    response = {"data": b64_string}
    return response


def save_screenshot():
    file_name = f"{uuid.uuid4()}.png"
    haystack_file_path = os.path.join(image_dir, file_name)
    pyautogui.screenshot(haystack_file_path)
    return file_name
