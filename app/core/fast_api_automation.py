"""IMPORTANT: This version can only run in docker containers with a virtual display or a normal computer"""
import base64
import pathlib
import time

import cv2
import os
from PIL import Image
from fastapi import Body, FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from pyautogui import moveTo, click, keyUp, keyDown, screenshot
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


@app.post('/execute_celery_action/{action_id}')
def execute_celery_action(action_id: int = Path(None, description="The ID of the action you would like to run.")):
    if action_list_obj.action_list.get(str(action_id)):
        action = action_list_obj.action_list.get(str(action_id))
        task = celery_worker.run_action.delay(action["code"])
        response = {'data': f'{task}'}
    else:
        response = {'data': 'Action not found.'}
    return response


@app.post('/execute_action/{action_id}')
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
