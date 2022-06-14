"""IMPORTANT: This version can only run in docker containers with a virtual display or a normal computer"""
import base64
import datetime
import logging
import pathlib
import random
import time
import uuid

import cv2
import enchant
import os

import pyautogui as pyautogui
from PIL import Image
import pytesseract
from fastapi import Body, FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from pyautogui import moveTo, click, keyUp, keyDown, screenshot, size, press, KEYBOARD_KEYS
try:
     from . import models
except:
     import models
try:
     from . import celery_worker
except:
     import celery_worker
try:
     from . import random_mouse
except:
     import random_mouse
try:
     from . import screen_reader
except:
     import screen_reader


app = FastAPI()

origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
action_list_obj = models.ActionList()
action_list_obj.load_action_list()
task_list_obj = models.TaskList()
task_list_obj.load_task_list()
schedule_list_obj = models.ScheduleList()
schedule_list_obj.load_schedule_list()
image_resource = models.ImageResource()
screen_data_resource = models.ScreenDataResource()
screen_width, screen_height = size()
pyautogui.FAILSAFE = False
logging.basicConfig(level=logging.DEBUG)


@app.get('/')
def home():
    response = {'data': 'Testing'}
    logging.debug(response)
    return response


@app.get("/get-actions/")
def get_actions():
    response = action_list_obj.action_list
    logging.debug(response)
    return response


@app.get("/get-action/{action_id}")
def get_action(action_id: int = Path(None, description="The ID of the action you would like to view.")):
    if action_list_obj.action_list.get(str(action_id)):
        response = action_list_obj.action_list.get(str(action_id))
    else:
        response = {'data': 'Action not found.'}
    logging.debug(response)
    return response


@app.post('/add-action')
def add_action(new_action: models.Action):
    response = action_list_obj.add_action(new_action)
    logging.debug(response)
    return response


@app.post("/update-action/{action_id}")
def update_action(action_id: int, new_action: models.Action):
    if action_id >= len(action_list_obj.action_list) or action_id < 0:
        response = {'data': 'Invalid ID entered.'}
        logging.debug(response)
        return response
    action_list_obj.update_action(action_id, new_action)
    response = {'data': 'Action updated'}
    logging.debug(response)
    return response


@app.get('/delete-action/{action_id}')
def delete_action(action_id: int):
    response = action_list_obj.delete_action(action_id)
    logging.debug(response)
    return response


@app.get("/get-tasks")
def get_tasks():
    if len(task_list_obj.task_list) > 0:
        response = task_list_obj.task_list
        logging.debug(response)
        return response
    response = {'data': 'Not found'}
    logging.debug(response)
    return response


@app.get("/get-task/{task_name}")
def get_task(task_name: str = Path(1, description="The name of the task you would like to view.")):
    response = {'data': 'Task not found.'}
    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                response = task_list_obj.task_list[key]
    logging.debug(response)
    return response


@app.post('/add-task')
def add_task(task: models.Task):
    response = task_list_obj.add_task(task)
    logging.debug(response)
    return response


@app.post('/tasks-add-action/{tasklist_name}')
def task_add_action(task_name: str, new_action: models.Action):
    action_response = action_list_obj.add_action(new_action)
    new_action_id = None
    if action_list_obj.action_list not in [None, {}]:
        for key in action_list_obj.action_list:
            if new_action.name == action_list_obj.action_list[key].get('name'):
                new_action_id = action_list_obj.action_list[key].get('id')
    response = {'data': f'Task {task_name} does not exist.'}
    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                task_list_obj.task_list[key]["action_id_list"].append(new_action_id)
                response = {'data': 'Action has been added to the task list.'}
    logging.debug(response)
    return response


@app.get("/execute-task/{task_id}")
def execute_task(task_id: int):
    task = task_list_obj.task_list[str(task_id)]
    action_id_list = [] if task.get('action_id_list') in [None, []] else task["action_id_list"]
    for action_id in action_id_list:
        execute_action(action_id)
    if action_id_list in [None, []]:
        response = {'data': 'Task not found'}
    else:
        response = {'data': 'Task complete'}
    logging.debug(response)
    return response


@app.get("/get-schedules/")
def get_schedules():
    if len(schedule_list_obj.schedule_list) > 0:
        response = schedule_list_obj.schedule_list
    else:
        response = {'data': 'Not found'}
    logging.debug(response)
    return response


@app.get("/get-schedule/{schedule_name}")
def get_schedule(schedule_name: str = Path(1, description="The ID of the schedule you would like to view.")):
    response = {'data': 'Not found'}
    if schedule_list_obj.schedule_list not in [None, {}]:
        for key in schedule_list_obj.schedule_list:
            if schedule_name == schedule_list_obj.schedule_list[key].get('name'):
                response = schedule_list_obj.schedule_list[key]
    logging.debug(response)
    return response


@app.post('/schedule-add-task/{schedule_name}/{task_list_name}')
def schedule_add_task(schedule_name: str, task_name: str):
    response = {'data': 'Schedule does not exist.'}
    task_id = None
    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                task_id = task_list_obj.task_list[key].get('id')
    if task_id is None:
        response = {'data': 'Task does not exist.'}
        logging.debug(response)
        return response
    if schedule_list_obj.schedule_list not in [None, {}]:
        for key in schedule_list_obj.schedule_list:
            if schedule_name == schedule_list_obj.schedule_list[key].get('name'):
                schedule_list_obj.schedule_list[key]['task_id_list'].append(task_id)
                response = {'data': 'Added task to schedule.'}
    logging.debug(response)
    return response


@app.post('/execute-celery-action/{action_id}')
def execute_celery_action(action_id: int = Path(None, description="The ID of the action you would like to run.")):
    if action_list_obj.action_list.get(str(action_id)):
        action = action_list_obj.action_list.get(str(action_id))
        task = celery_worker.run_action.delay(action["code"])
        response = {'data': f'{task}'}
    else:
        response = {'data': 'Action not found.'}
    logging.debug(response)
    return response


@app.post('/execute-action/{action_id}')
def execute_action(action_id: int = Path(None, description="The ID of the action you would like to run.")):
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    response = {'data': f'Error with action_id:{action_id}'}
    if action_list_obj.action_list.get(str(action_id)):
        action = action_list_obj.action_list.get(str(action_id))
        repeat = True if action.get("repeat") not in [False, None] else False
        num_repeats = action.get("num_repeats") if action.get("num_repeats") not in [0, None] else 0
        # Repeat action until num_repeats is 0 or repeat is false
        while True:
            if action.get("time_delay") not in [0.0, None]:
                delay = float(action["time_delay"])
                time.sleep(delay)
            if action.get("function") not in ["", None]:
                x = -1
                y = -1
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
                        logging.debug(response)
                        return response
                    x1 = action["x1"]
                    y1 = action["y1"]
                    x2 = action["x2"]
                    y2 = action["y2"]
                    x_range = x2 - x1
                    y_range = y2 - y1
                    if action.get("random_range") not in [0, None]:
                        # This fixes any errors with random mouse click range with region click
                        if x_range > random_range*2:
                            x1 = x1 + random_range
                            x2 = x2 - random_range
                        elif x_range < random_range and x_range > 4:
                            random_range = 1
                            x1 = x1 + random_range
                            x2 = x2 - random_range
                        else:
                            random_range = 0
                        if y_range > random_range*2:
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
                        click(x,y)
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
            if num_repeats <= 0 or not repeat:
                break
            elif num_repeats > 0:
                num_repeats = num_repeats - 1
    logging.debug(response)
    return response


@app.get('/screenshot/')
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
    return response


@app.post('/screen-snip/{x1}/{y1}/{x2}/{y2}/')
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
    response = image_resource.store_image(image_obj)
    if response.get("data").startswith("Saved"):
        response = image_obj
    logging.debug(response)
    return response


@app.get('/move-mouse/{x}/{y}')
def move_mouse(x: int, y: int):
    screen_width, screen_height = size()
    response = {'data': 'Invalid input'}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        moveTo(x, y)
        response = {'data': f'Moved mouse to ({x},{y})'}
    logging.debug(response)
    return response


@app.get('/mouse-click/{x}/{y}')
def mouse_click(x: int, y: int):
    screen_width, screen_height = size()
    response = {'data': 'Invalid input'}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        click(x, y)
        response = {'data': f'Moved mouse to ({x},{y})'}
    logging.debug(response)
    return response


@app.get('/keypress/{key_name}')
def keypress(key_name: str):
    response = {'data': 'Invalid input'}
    valid_input = KEYBOARD_KEYS
    if key_name in valid_input:
        press(key_name)
        response = {'data': f'Key pressed {key_name}'}
    logging.debug(response)
    return response

@app.get('/capture-screen-data/{x1}/{y1}/{x2}/{y2}/{action_id}')
def capture_screen_data(x1: int, y1: int, x2: int, y2: int, action_id: int):
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
    english_dict = enchant.Dict("en_US")
    for index, word_data in enumerate(img_data.splitlines()):
        if index == 0:
            continue
        word = word_data.split()
        if len(word) == 12:
            if word[11].isnumeric() or english_dict.check(word[11]):
                word_id = str(uuid.uuid4())
                screen_obj_ids.append(word_id)
                word_x1, word_y1, word_width, word_height = int(word[6]), int(word[7]), int(word[8]), int(word[9])
                text = word[11]
                word_action_id = None if action_id >= len(action_list_obj.action_list) or action_id < 0 else action_id
                data_type = "text" if action_id >= len(action_list_obj.action_list) or action_id < 0 else "button"
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
                print(screen_object)
                response = screen_data_resource.store_screen_object(screen_object)
                if response.get("data").startswith("Saved"):
                    count = count + 1
                else:
                    print(response)
    screen_data_json = {
        "id": screenshot_id,
        "timestamp": timestamp,
        "base64str": b64_string,
        "screen_obj_ids": screen_obj_ids
    }
    screen_data = models.ScreenData(**screen_data_json)
    res = screen_data_resource.store_screen_data(screen_data)
    if count > 0:
        response = {'data': 'Screen data captured'}
    logging.debug(response)
    return response

