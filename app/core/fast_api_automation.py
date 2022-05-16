"""IMPORTANT: This version can only run in docker containers with a virtual display or a normal computer"""
import base64
import pathlib
import time
import uuid

import cv2
import os
from PIL import Image
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


@app.get('/')
def home():
    return {'data': 'Testing'}


@app.get("/get-actions/")
def get_actions():
    return action_list_obj.action_list


@app.get("/get-action/{action_id}")
def get_action(action_id: int = Path(None, description="The ID of the action you would like to view.")):
    if action_list_obj.action_list.get(str(action_id)):
        response = action_list_obj.action_list.get(str(action_id))
    else:
        response = {'data': 'Action not found.'}
    return response


@app.post('/add-action')
def add_action(new_action: models.Action):
    response = action_list_obj.add_action(new_action)
    return response


@app.put("/update-action/{action_id}")
def update_action(action_id: int, new_action: models.Action):
    if action_id >= len(action_list_obj.action_list) or action_id < 0:
        return {'data': 'Invalid ID entered.'}
    if action_list_obj.action_list[str(action_id)].get('name') == new_action.name and \
            action_list_obj.action_list[str(action_id)].get('code') == new_action.code:
        return {'data': 'New data matches old data.'}
    action_list_obj.action_list[str(action_id)] = new_action
    return {'data': 'Action updated'}


@app.post('/delete-action/{action_id}')
def delete_action(action_id: int):
    response = action_list_obj.delete_action(action_id)
    return response


@app.get("/get-tasks")
def get_tasks():
    if len(task_list_obj.task_list) > 0:
        return task_list_obj.task_list
    return {'data': 'Not found'}


@app.get("/get-task/{task_name}")
def get_task(task_name: str = Path(1, description="The name of the task you would like to view.")):
    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                return task_list_obj.task_list[key]
    return {'data': 'Task not found.'}


@app.post('/add-task')
def add_task(task: models.Task):
    response = task_list_obj.add_task(task)
    return response


@app.post('/tasks-add-action/{tasklist_name}')
def task_add_action(task_name: str, new_action: models.Action):
    action_response = action_list_obj.add_action(new_action)
    new_action_id = None
    if action_list_obj.action_list not in [None, {}]:
        for key in action_list_obj.action_list:
            if new_action.name == action_list_obj.action_list[key].get('name'):
                new_action_id = action_list_obj.action_list[key].get('id')

    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                task_list_obj.task_list[key]["action_id_list"].append(new_action_id)
                return {'data': 'Action has been added to the task list.'}
    return {'data': f'Task {task_name} does not exist.'}


@app.get("/get-schedules/")
def get_schedules():
    if len(schedule_list_obj.schedule_list) > 0:
        return schedule_list_obj.schedule_list
    return {'data': 'Not found'}


@app.get("/get-schedule/{schedule_name}")
def get_schedule(schedule_name: str = Path(1, description="The ID of the schedule you would like to view.")):
    if schedule_list_obj.schedule_list not in [None, {}]:
        for key in schedule_list_obj.schedule_list:
            if schedule_name == schedule_list_obj.schedule_list[key].get('name'):
                return schedule_list_obj.schedule_list[key]
    return {'data': 'Not found'}


@app.post('/schedule-add-task/{schedule_name}/{task_list_name}')
def schedule_add_task(schedule_name: str, task_name: str):
    task_id = None
    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                task_id = task_list_obj.task_list[key].get('id')
    if task_id is None:
        return {'data': 'Task does not exist.'}
    if schedule_list_obj.schedule_list not in [None, {}]:
        for key in schedule_list_obj.schedule_list:
            if schedule_name == schedule_list_obj.schedule_list[key].get('name'):
                schedule_list_obj.schedule_list[key]['task_id_list'].append(task_id)
                return {'data': 'Added task to schedule.'}
    return {'data': 'Schedule does not exist.'}


@app.post('/execute-celery-action/{action_id}')
def execute_celery_action(action_id: int = Path(None, description="The ID of the action you would like to run.")):
    if action_list_obj.action_list.get(str(action_id)):
        action = action_list_obj.action_list.get(str(action_id))
        task = celery_worker.run_action.delay(action["code"])
        response = {'data': f'{task}'}
    else:
        response = {'data': 'Action not found.'}
    return response


@app.post('/execute-action/{action_id}')
def execute_action(action_id: int = Path(None, description="The ID of the action you would like to run.")):
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    response = {'data': 'Action not found'}
    if action_list_obj.action_list.get(str(action_id)):
        actions = action_list_obj.action_list.get(str(action_id))
        print(actions)
        for action_str in actions.get('code'):
            if action_str.startswith('click') or action_str.startswith('moveTo'):
                action = 'click'
                if action_str.startswith('click'):
                    params = action_str.lstrip('click(')
                else:
                    action = 'moveTo'
                    params = action_str.lstrip('moveTo(')
                params = params.rstrip(')')
                params = params.split(', ')
                params[0] = params[0].lstrip('x=')
                params[1] = params[1].lstrip('y=')
                x = int(params[0])
                y = int(params[1])

                if len(params) == 2:
                    if action == 'click':
                        click(x=x, y=y)
                        response = {'data': f'Mouse clicked: ({x}, {y})'}
                    else:
                        moveTo(x=x, y=y)
                        response = {'data': f'Mouse moved to: ({x}, {y})'}
                elif 'random_path=true' in params:
                    random_mouse.random_move(x=x, y=y)
                    path_index = params.index('random_path=true')
                    params.pop(path_index)
                # moveTo() cannot have random_delay and random_range
                if len(params) == 3 and params[2].startswith('random_range='):
                    params[2] = params[2].lstrip('random_range=')
                    rand_range = int(params[2])
                    random_mouse.random_click(x=x, y=y, rand_range=rand_range)
                    response = {'data': f'Mouse clicked: ({x}, {y})'}
                elif len(params) == 3 and params[2].startswith('random_range='):
                    params[2] = params[2].lstrip('random_delay=')
                    delay_duration = float(params[2])
                    random_mouse.random_click(x=x, y=y, rand_range=0, delay_duration=delay_duration)
                elif len(params) == 4:
                    params[2] = params[2].lstrip('random_range=')
                    rand_range = int(params[2])
                    params[3] = params[3].lstrip('random_delay=')
                    delay_duration = float(params[3])
                    random_mouse.random_click(x=x, y=y, rand_range=rand_range, delay_duration=delay_duration)
            elif action_str.startswith('keypress'):
                param = action_str.lstrip('keypress(\"')
                param = param.rstrip('\")')
                keyDown(param)
                time.sleep(1)
                keyUp(param)
                response = {'data': f'Key pressed {param}'}
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
        os.remove(os.path.join(resources_dir, screenshot_path))
    return {'data': b64_string}


@app.get('/screen-snip/{x1}/{y1}/{x2}/{y2}/')
def screen_snip(x1: int, y1: int, x2: int, y2: int):
    """This function is used to capture a section of the screen and store in resources/images as png and json files"""
    base_dir = pathlib.Path('.').absolute()
    image_dir = os.path.join(base_dir, 'resources', 'images')
    if not os.path.isdir(image_dir):
        image_dir = os.path.join(base_dir, 'core', 'resources', 'images')
    image_id = uuid.uuid4()
    image_path = os.path.join(image_dir, f'{image_id}.png')
    screenshot(image_path)
    img = cv2.imread(image_path)
    cv2.imwrite(image_path, img[y1:y2, x1:x2, :])
    snip_img = cv2.imread(image_path)
    snip_png_img = cv2.imencode('.png', snip_img)
    b64_string = base64.b64encode(snip_png_img[1]).decode('utf-8')
    width = snip_img.shape[0]
    height = snip_img.shape[1]
    image_json = {
        "id": f"{image_id}",
        "width": width,
        "height": height,
        "base64str": f"{b64_string}"
    }
    image_obj = models.Image(**image_json)
    print(image_obj)
    response = image_resource.store_image(image_obj)
    if response.get("data").startswith("Saved"):
        return image_obj
    else:
        return response


@app.get('/move-mouse/{x}/{y}')
def move_mouse(x: int, y: int):
    screen_width, screen_height = size()
    response = {'data': 'Invalid input'}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        moveTo(x, y)
        response = {'data': f'Moved mouse to ({x},{y})'}

    return response


@app.get('/mouse-click/{x}/{y}')
def mouse_click(x: int, y: int):
    screen_width, screen_height = size()
    response = {'data': 'Invalid input'}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        click(x, y)
        response = {'data': f'Moved mouse to ({x},{y})'}

    return response


@app.get('/keypress/{key_name}')
def keypress(key_name: str):
    response = {'data': 'Invalid input'}
    valid_input = KEYBOARD_KEYS
    if key_name in valid_input:
        press(key_name)
        response = {'data': f'Key pressed {key_name}'}

    return response
