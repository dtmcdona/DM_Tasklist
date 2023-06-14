"""
Fast API Endpoints
    These endpoints are used to:
        - CRUD JSON Data
        - Open the browser within the xvfb virtual display
        - Capture screen data from the xvfb virtual display
        - Interact with the process controller:
            1. Execute Actions
            2. Execute Tasks
"""
import asyncio
import logging
from typing import List

from . import (
    api_resources,
    asyncio_utils,
    celery_worker,
    models,
    process_controller,
)
from . import task_manager as manager

from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:3000", "http://localhost:8003"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=api_resources.storage.logging_level)


@app.get("/")
async def home():
    """Placeholder for home API"""
    return {"data": "Testing"}


@app.post("/open_broswer/")
async def open_broswer(url: str):
    """Opens a browser on local machine in xvfb display (does not work in docker container)"""
    return process_controller.open_browser(url)


@app.get("/get-actions/")
async def get_actions():
    """Gets all stored actions"""
    return api_resources.storage.get_action_collection()


@app.get("/get-action/{action_id}")
async def get_action(
    action_id: str = Path(
        None,
        description="The ID of the action you would like to view.",
    )
):
    """Returns an action by id"""
    return api_resources.storage.get_action(action_id)


@app.post("/add-action")
def add_action(new_action: models.Action):
    """Adds a new action to api_resources.storage"""
    return api_resources.storage.add_action(new_action)


@app.post("/add-execute-action")
def add_execute_action(new_action: models.Action):
    """Adds a new action to api_resources.storage"""
    response = api_resources.storage.add_action(new_action)
    if isinstance(response, models.Action):
        execution = process_controller.process_action(response, False)
        logging.debug(execution)
    return response


@app.get("/execute-action/{action_id}")
async def execute_action(
    action_id: str = Path(
        None,
        description="The ID of the action you would like to run.",
    ),
    instant_playback: bool = False,
):
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    response = {"data": f"Error with action_id:{action_id}"}
    action = api_resources.storage.get_action(action_id)
    if action:
        if instant_playback:
            response = process_controller.process_action(
                action, instant_playback
            )
        else:
            response = process_controller.action_controller(action)

    logging.debug(response)
    return response


@app.post("/update-action/{action_id}")
def update_action(action_id: str, new_action: models.Action):
    """Updates a previous action with new information"""
    return api_resources.storage.update_action(action_id, new_action)


@app.get("/delete-action/{action_id}")
def delete_action(action_id: str):
    """Deletes an action by id"""
    return api_resources.storage.delete_action(action_id)


@app.get("/get-tasks")
async def get_tasks():
    """Gets all stored tasks"""
    return api_resources.storage.get_task_collection()


@app.get("/get-task/{task_id}")
async def get_task(
    task_id: str = Path(
        1, description="The id of the task you would like to view."
    )
):
    """Returns a task by id"""
    return api_resources.storage.get_task(task_id)


@app.post("/add-task")
async def add_task(task: models.Task):
    """Adds a new task to api_resources.storage"""
    return api_resources.storage.add_task(task)


@app.post("/update-task/{task_id}")
def update_task(task_id: str, new_task: models.Task):
    """Updates a previous task with new information"""
    return api_resources.storage.update_task(task_id, new_task)


@app.post("/task-add-action/{task_id}/{action_id}")
async def task_add_action(task_id: str, action_id: str):
    """Adds an action to a task"""
    response = {"data": "Task does not exist."}
    action = api_resources.storage.get_action(action_id)
    if not action:
        response = {"data": "Action does not exist."}
        logging.debug(response)
        return response
    task = api_resources.storage.get_task(task_id)
    if not task:
        response = {"data": "Task does not exist."}
        logging.debug(response)
        return response
    else:
        task["action_id_list"].append(action_id)
        api_resources.storage.update_task(task_id, task)
        response = {"data": "Added action to task."}
    logging.debug(response)
    return response


@app.get("/execute-task/{task_id}")
def execute_task(task_id: str):
    """Executes a task by looping through the action collection and executing each action"""
    task = api_resources.storage.get_task(task_id)
    if not task or task.get("action_id_list") in [None, []]:
        response = {"data": "Task not found"}
    else:
        task_manager_obj = manager.TaskManager(models.Task(**task), False)
        response = task_manager_obj.start_playback()
    logging.debug(response)
    return response


@app.post("/execute-celery-action/{action_id}")
async def execute_celery_action(
    action_id: str = Path(
        None,
        description="The ID of the action you would like to run.",
    )
):
    """This function creates a celery task that completes an actions"""
    return celery_worker.run_action.delay(action_id)


@app.get("/screenshot/")
async def screen_shot():
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    return process_controller.screen_shot_response()


@app.post("/screen-snip/{x1}/{y1}/{x2}/{y2}/")
def screen_snip(x1: int, y1: int, x2: int, y2: int, image: models.Image):
    """This function is used to capture a section of the screen and store in resources/images as png and json files"""
    return process_controller.screen_snip(x1, y1, x2, y2, image)


@app.get("/move-mouse/{x}/{y}")
def move_mouse(x: int, y: int):
    return process_controller.move_mouse(x, y)


@app.get("/mouse-click/{x}/{y}")
def mouse_click(x: int, y: int):
    """Moves and clicks the mouse at point (x, y)"""
    return process_controller.mouse_click(x, y)


@app.get("/keypress/{key_id}")
def keypress(key_name: str):
    return process_controller.keypress(key_name)


@app.get("/capture-screen-data/{x1}/{y1}/{x2}/{y2}/{action_id}")
def capture_screen_data(x1: int, y1: int, x2: int, y2: int, action_id: int):
    """This function captures data within the region within (x1, y1) and (x2, y2)"""
    return process_controller.capture_screen_data(x1, y1, x2, y2, action_id)


@app.post("/fetch-all/")
async def fetch_all(async_req: models.AsyncRequest):
    return await asyncio.create_task(asyncio_utils.get_requests(async_req.urls))


@app.post("/fan-out/")
async def fan_out(action_ids: List[str], instant_playback: bool):
    for action_id in action_ids:
        celery_worker.run_action.delay(
            action_id, instant_playback=instant_playback
        )
    return {"data": "Created celery tasks"}
