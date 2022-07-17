import base64
import datetime
import logging
import pathlib
import time
import uuid

import cv2
import enchant
import os

import pyautogui as pyautogui
import pytesseract
import numpy as np
from pyautogui import screenshot, size
from core import models
from core import fast_api_automation as api


base_dir = pathlib.Path('.').absolute()
resources_dir = os.path.join(base_dir, 'resources')
if not os.path.isdir(resources_dir):
    resources_dir = os.path.join(base_dir, 'core', 'resources')
image_dir = os.path.join(resources_dir, 'images')
screen_width, screen_height = size()


def image_search(needle_file_name: str, haystack_file_name: str = "", percent_similarity: float = .9):
    # Search for needle in a haystack
    needle_file_path = os.path.join(image_dir, needle_file_name)
    needle = cv2.imread(needle_file_path, cv2.IMREAD_UNCHANGED)
    grayscale_needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)
    if haystack_file_name in ["", None]:
        image_id = uuid.uuid4()
        haystack_file_path = os.path.join(image_dir, f'{image_id}.png')
        pyautogui.screenshot(haystack_file_path)
    else:
        haystack_file_path = os.path.join(image_dir, haystack_file_name)
    haystack = cv2.imread(haystack_file_path, cv2.IMREAD_UNCHANGED)
    grayscale_haystack = cv2.cvtColor(haystack, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(grayscale_haystack, grayscale_needle, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # Max location has the best match with max_val to be % accuracy
    width = needle.shape[1]
    height = needle.shape[0]
    bottom_right = (max_loc[0] + width, max_loc[1] + height)
    # Threshold is the % accuracy compared to original needle
    threshold = percent_similarity
    yloc, xloc = np.where(result >= threshold)
    # Keep track of all matches and identify unique cases
    matches = []
    # Delete haystack image since it is a representation of current screen
    if os.path.exists(haystack_file_path):
        os.remove(haystack_file_path)
    if len(xloc) > 0:
        # print("There are {0} total matches in the haystack.".format(len(xloc)))
        for (x, y) in zip(xloc, yloc):
            # Twice to ensure singles are kept after picking unique cases
            matches.append([int(x), int(y), int(width), int(height)])
            matches.append([int(x), int(y), int(width), int(height)])
        # Grouping function
        matches, weights = cv2.groupRectangles(matches, 1, 0.2)
        # print("There are {0} unique matches in the haystack.".format(len(matches)))
        # Assuming the first match was a good match
        if len(matches) > 0:
            center_x = matches[0][0] + width / 2
            center_y = matches[0][1] + height / 2
            return center_x, center_y
    else:
        print("There are no matches.")
        return -1, -1


def capture_screen_data(x1: int, y1: int, x2: int, y2: int, action_id: int):
    """This function captures data within the region within (x1, y1) and (x2, y2)"""
    response = {'data': 'Screen data not captured'}
    screenshot_id = str(uuid.uuid4())
    base_dir = pathlib.Path('.').absolute()
    resources_dir = os.path.join(base_dir, 'resources', 'screenshot')
    if not os.path.isdir(resources_dir):
        resources_dir = os.path.join(base_dir, 'core', 'resources', 'screenshot')
    screenshot_path = os.path.join(resources_dir, f'{screenshot_id}.png')
    screenshot(screenshot_path)
    img = cv2.imread(screenshot_path)
    width = x2 - x1
    height = y2 - y1
    if width != screen_width and height != screen_height:
        cv2.imwrite(screenshot_path, img[y1:y2, x1:x2, :])
        img = cv2.imread(screenshot_path)
    """Prepare screenshot for Pytesseract OCR"""
    png_img = cv2.imencode('.png', img)
    b64_string = base64.b64encode(png_img[1]).decode('utf-8')
    (h, w) = img.shape[:2]
    img = cv2.resize(img, (w * 5, h * 5))
    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thr = cv2.threshold(gry, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    cv2.imwrite(screenshot_path, thr)
    # There might be some case where inverting the image gives better results
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
        """This loops through all words and numbers found within the region and stores in screen_object json files."""
        if index == 0:
            continue
        word = word_data.split()
        if len(word) == 12:
            if word[11].isnumeric() or english_dict.check(word[11]):
                word_id = str(uuid.uuid4())
                text = word[11]
                screen_obj_ids.append(word_id)
                screen_obj_values.append(text)
                word_x1, word_y1, word_width, word_height = int(word[6]), int(word[7]), int(word[8]), int(word[9])
                if action_id >= len(api.action_list_obj.action_list) or action_id < 0:
                    word_action_id = None
                else:
                    word_action_id = action_id
                data_type = "text" if action_id >= len(api.action_list_obj.action_list) or action_id < 0 else "button"
                """Screen objects are data that store information from GUI elements and/or actions"""
                screen_object_json = {
                    "id": f"{word_id}",
                    "type": data_type,
                    "action_id": word_action_id,
                    "timestamp": timestamp,
                    "text": text,
                    "x1": x1+word_x1,
                    "y1": y1+word_y1,
                    "x2": x1+word_x1+word_width,
                    "y2": y1+word_y1+word_height
                }
                screen_object = models.ScreenObject(**screen_object_json)
                logging.debug(screen_object)
                response = api.screen_data_resource.store_screen_object(screen_object)
                if response.get("data").startswith("Saved"):
                    count = count + 1
                else:
                    logging.debug(response)
    """Screen Data JSON files are mainly kept for debugging purposes"""
    screen_data_json = {
        "id": screenshot_id,
        "timestamp": timestamp,
        "base64str": b64_string,
        "screen_obj_ids": screen_obj_ids
    }
    if count > 0:
        screen_data = models.ScreenData(**screen_data_json)
        response = api.screen_data_resource.store_screen_data(screen_data)
        logging.debug(response)
    if count == 0:
        response = {'data': 'No screen objects found'}
        logging.warning(response)
    elif action_id >= len(api.action_list_obj.action_list) or action_id < 0:
        """Create new action"""
        variables = [", ".join(screen_obj_ids), ", ".join(screen_obj_values)]
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
        variables = [", ".join(screen_obj_ids), ", ".join(screen_obj_values)]
        print(updated_action)
        updated_action["variables"] = variables
        updated_action_obj = models.Action(**updated_action)
        response = api.update_action(action_id=action_id, new_action=updated_action_obj)
    return response


def screen_snip(x1: int, y1: int, x2: int, y2: int, image: models.Image):
    """This function is used to capture a section of the screen and store in resources/images as png and json files"""
    base_dir = pathlib.Path('.').absolute()
    image_dir = os.path.join(base_dir, 'resources', 'images')
    if not os.path.isdir(image_dir):
        image_dir = os.path.join(base_dir, 'core', 'resources', 'images')
    base64str = image.base64str
    decoded64str = base64.b64decode(base64str)
    image_id = uuid.uuid4()
    image_path = os.path.join(image_dir, f'{image_id}.png')
    with open(image_path, 'wb') as f:
        f.write(decoded64str)
    img = cv2.imread(image_path)
    cv2.imwrite(image_path, img[y1:y2, x1:x2, :])
    snip_img = cv2.imread(image_path)
    snip_png_img = cv2.imencode('.png', snip_img)
    b64_string = base64.b64encode(snip_png_img[1]).decode('utf-8')
    width = snip_img.shape[0]
    height = snip_img.shape[1]
    image_json = {
        "id": f"{image_id}",
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "width": width,
        "height": height,
        "base64str": f"{b64_string}"
    }
    image_obj = models.Image(**image_json)
    response = api.image_resource.store_image(image_obj)
    if response.get("data").startswith("Saved"):
        response = image_obj
    logging.debug(response)
    return response


def screen_shot():
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    timestamp = round(time.time() * 1000)
    base_dir = pathlib.Path('.').absolute()
    resources_dir = os.path.join(base_dir, 'resources', 'screenshot')
    if not os.path.isdir(resources_dir):
        resources_dir = os.path.join(base_dir, 'core', 'resources', 'screenshot')
    screenshot_path = os.path.join(resources_dir, f'screenshot_{timestamp}.png')
    screenshot(screenshot_path)
    img = cv2.imread(screenshot_path)
    png_img = cv2.imencode('.png', img)
    b64_string = base64.b64encode(png_img[1]).decode('utf-8')
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)
    response = {'data': b64_string}
    logging.debug(response)
