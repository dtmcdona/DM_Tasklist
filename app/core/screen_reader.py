import time
import uuid
from pathlib import Path
import pyautogui
import cv2
import numpy as np
import os


base_dir = Path('.').absolute()
resources_dir = os.path.join(base_dir, 'resources')
if not os.path.isdir(resources_dir):
    resources_dir = os.path.join(base_dir, 'core', 'resources')
image_dir = os.path.join(resources_dir, 'images')


def image_search(needle_file_name: str, haystack_file_name: str = "", percent_similarity: float = .9):
    # Search for needle in a haystack
    needle_file_path = os.path.join(image_dir, needle_file_name)
    needle = cv2.imread(needle_file_path, cv2.IMREAD_UNCHANGED)
    grayscale_needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)
    if haystack_file_name == "":
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
        print("There are {0} total matches in the haystack.".format(len(xloc)))
        for (x, y) in zip(xloc, yloc):
            # Twice to ensure singles are kept after picking unique cases
            matches.append([int(x), int(y), int(width), int(height)])
            matches.append([int(x), int(y), int(width), int(height)])
        # Grouping function
        matches, weights = cv2.groupRectangles(matches, 1, 0.2)
        print("There are {0} unique matches in the haystack.".format(len(matches)))
        # Assuming the first match was a good match
        if len(matches) > 0:
            center_x = matches[0][0] + width / 2
            center_y = matches[0][1] + height / 2
            return center_x, center_y
    else:
        print("There are no matches.")
        return -1, -1
