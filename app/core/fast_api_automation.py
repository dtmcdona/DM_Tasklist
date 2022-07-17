"""IMPORTANT: This version can only run in docker containers with a virtual display or a normal computer"""
import logging

import pyautogui as pyautogui
from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware
from pyautogui import moveTo, click, size, press, KEYBOARD_KEYS
from core import models
from core import celery_worker
from core import screen_reader
from core import process_controller


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
pyautogui.FAILSAFE = False
logging.basicConfig(level=logging.DEBUG)


@app.get('/')
def home():
    """Placeholder for home API"""
    response = {'data': 'Testing'}
    logging.debug(response)
    return response


@app.get("/get-actions/")
def get_actions():
    """Gets all stored actions"""
    response = action_list_obj.action_list
    logging.debug(response)
    return response


@app.get("/get-action/{action_id}")
def get_action(action_id: int = Path(None, description="The ID of the action you would like to view.")):
    """Returns an action by id"""
    if action_list_obj.action_list.get(str(action_id)):
        response = action_list_obj.action_list.get(str(action_id))
    else:
        response = {'data': 'Action not found.'}
    logging.debug(response)
    return response


@app.post('/add-action')
def add_action(new_action: models.Action):
    """Adds a new action to storage"""
    response = action_list_obj.add_action(new_action)
    logging.debug(response)
    return response


@app.post("/update-action/{action_id}")
def update_action(action_id: int, new_action: models.Action):
    """Updates a previous action with new information"""
    if action_id >= len(action_list_obj.action_list) or action_id < 0:
        response = {'data': 'Invalid ID entered.'}
        logging.debug(response)
        return response
    response = action_list_obj.update_action(action_id, new_action)
    logging.debug(response)
    return response


@app.get('/delete-action/{action_id}')
def delete_action(action_id: int):
    """Deletes an action by id"""
    response = action_list_obj.delete_action(action_id)
    logging.debug(response)
    return response


@app.get("/get-tasks")
def get_tasks():
    """Gets all stored tasks"""
    if len(task_list_obj.task_list) > 0:
        response = task_list_obj.task_list
        logging.debug(response)
        return response
    response = {'data': 'Not found'}
    logging.debug(response)
    return response


@app.get("/get-task/{task_name}")
def get_task(task_name: str = Path(1, description="The name of the task you would like to view.")):
    """Returns a task by name"""
    response = {'data': 'Task not found.'}
    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                response = task_list_obj.task_list[key]
    logging.debug(response)
    return response


@app.post('/add-task')
def add_task(task: models.Task):
    """Adds a new task to storage"""
    response = task_list_obj.add_task(task)
    logging.debug(response)
    return response


@app.post('/tasks-add-action/{tasklist_name}')
def task_add_action(task_name: str, new_action: models.Action):
    """Adds a new action to task"""
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
    """Executes a task by looping through the action list and executing each action"""
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
    """Gets all stored schedules"""
    if len(schedule_list_obj.schedule_list) > 0:
        response = schedule_list_obj.schedule_list
    else:
        response = {'data': 'Not found'}
    logging.debug(response)
    return response


@app.get("/get-schedule/{schedule_name}")
def get_schedule(schedule_name: str = Path(1, description="The ID of the schedule you would like to view.")):
    """Returns a schedule by name"""
    response = {'data': 'Not found'}
    if schedule_list_obj.schedule_list not in [None, {}]:
        for key in schedule_list_obj.schedule_list:
            if schedule_name == schedule_list_obj.schedule_list[key].get('name'):
                response = schedule_list_obj.schedule_list[key]
    logging.debug(response)
    return response


@app.post('/schedule-add-task/{schedule_name}/{task_list_name}')
def schedule_add_task(schedule_name: str, task_name: str):
    """Adds a task to a schedule"""
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
    """This function creates a celery task that completes an actions"""
    task = celery_worker.run_action.delay(action_id)
    response = {'data': f'{task}'}
    return response


@app.post('/execute-action/{action_id}')
def execute_action(action_id: int = Path(None, description="The ID of the action you would like to run.")):
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    response = {'data': f'Error with action_id:{action_id}'}
    if action_list_obj.action_list.get(str(action_id)):
        action = action_list_obj.action_list.get(str(action_id))
        if action:
            response = process_controller.action_controller(action)

    logging.debug(response)
    return response


@app.get('/screenshot/')
def screen_shot():
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    return screen_reader.screen_shot()


@app.post('/screen-snip/{x1}/{y1}/{x2}/{y2}/')
def screen_snip(x1: int, y1: int, x2: int, y2: int, image: models.Image):
    """This function is used to capture a section of the screen and store in resources/images as png and json files"""
    return screen_reader.screen_snip(x1, y1, x2, y2, image)


@app.get('/move-mouse/{x}/{y}')
def move_mouse(x: int, y: int):
    """Moves the mouse to (x, y)"""
    screen_width, screen_height = size()
    response = {'data': 'Invalid input'}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        moveTo(x, y)
        response = {'data': f'Moved mouse to ({x},{y})'}
    logging.debug(response)
    return response


@app.get('/mouse-click/{x}/{y}')
def mouse_click(x: int, y: int):
    """Moves and clicks the mouse at point (x, y)"""
    screen_width, screen_height = size()
    response = {'data': 'Invalid input'}
    if x <= screen_width and x >= 0 and y <= screen_height and y >= 0:
        click(x, y)
        response = {'data': f'Moved mouse to ({x},{y})'}
    logging.debug(response)
    return response


@app.get('/keypress/{key_name}')
def keypress(key_name: str):
    """Presses the given key"""
    response = {'data': 'Invalid input'}
    valid_input = KEYBOARD_KEYS
    if key_name in valid_input:
        press(key_name)
        response = {'data': f'Key pressed {key_name}'}
    logging.debug(response)
    return response

@app.get('/capture-screen-data/{x1}/{y1}/{x2}/{y2}/{action_id}')
def capture_screen_data(x1: int, y1: int, x2: int, y2: int, action_id: int):
    """This function captures data within the region within (x1, y1) and (x2, y2)"""
    return screen_reader.capture_screen_data(x1, y1, x2, y2, action_id)
