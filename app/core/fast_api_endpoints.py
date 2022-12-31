"""
Fast API Endpoints
    These endpoints are used to:
        - CRUD JSON Data
        - Open the browser within the xvfb virtual display
        - Capture screen data from the xvfb virtual display
        - Interact with the process controller:
            1. Execute Actions
            2. Execute Tasks
            3. Execute Schedules
"""
from core import api_resources, celery_worker, models, process_controller, task_manager

from fastapi import FastAPI, Path
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
storage = api_resources.APICollections()

@app.get("/")
def home():
    """Placeholder for home API"""
    return {"data": "Testing"}


@app.post("/open_broswer/")
def open_broswer(url: str):
    """Opens a browser on local machine in xvfb display (does not work in docker container)"""
    return process_controller.open_browser(url)


@app.get("/get-actions/")
def get_actions():
    """Gets all stored actions"""
    return storage.get_action_collection()


@app.get("/get-action/{action_id}")
def get_action(
    action_id: int = Path(
        None,
        description="The ID of the action you would like to view.",
    )
):
    """Returns an action by id"""
    return storage.get_action(action_id)


@app.post("/add-action")
def add_action(new_action: models.Action):
    """Adds a new action to storage"""
    return storage.add_action(new_action)


@app.post("/update-action/{action_id}")
def update_action(action_id: int, new_action: models.Action):
    """Updates a previous action with new information"""
    return storage.update_action(action_id, new_action)


@app.get("/delete-action/{action_id}")
def delete_action(action_id: int):
    """Deletes an action by id"""
    return storage.delete_action(action_id)


@app.get("/get-tasks")
def get_tasks():
    """Gets all stored tasks"""
    return storage.get_task_collection()


@app.get("/get-task/{task_name}")
def get_task(
    task_name: str = Path(
        1, description="The name of the task you would like to view."
    )
):
    """Returns a task by name"""
    return storage.get_task_by_name(task_name)


@app.post("/add-task")
def add_task(task: models.Task):
    """Adds a new task to storage"""
    return storage.add_task(task)


@app.post("/tasks-add-action/{task_name}")
def task_add_action(task_name: str, new_action: models.Action):
    """Adds a new action to task"""
    action_response = storage.add_action(new_action)
    new_action_id = None
    actions = storage.get_action_collection()
    if actions not in [None, {}]:
        for index, action in actions:
            if new_action.name == action.get(
                "name"
            ):
                new_action_id = action.get("id")
    response = {"data": f"Task {task_name} does not exist."}
    tasks = storage.get_task_collection()
    if tasks not in [None, {}]:
        for key, task in tasks:
            if task_name == task.get("name"):
                task["action_id_list"].append(
                    new_action_id
                )
                response = {
                    "data": "Action has been added to the task collection."
                }
    storage.logging.debug(response)
    return response


@app.get("/execute-task/{task_id}")
def execute_task(task_id: int):
    """Executes a task by looping through the action collection and executing each action"""
    task = storage.get_task(task_id)
    if not task or task.get("action_id_list") in [None, []]:
        response = {"data": "Task not found"}
    else:
        task_manager_obj = task_manager.TaskManager(task, False)
        response = task_manager_obj.start_playback()
    storage.logging.debug(response)
    return response


@app.get("/get-schedules/")
def get_schedules():
    """Gets all stored schedules"""
    return storage.get_schedule_collection()


@app.get("/get-schedule/{schedule_name}")
def get_schedule(
    schedule_name: str = Path(
        1,
        description="The name of the schedule you would like to view.",
    )
):
    """Returns a schedule by name"""
    return storage.get_schedule_by_name(schedule_name)


@app.post("/schedule-add-task/{schedule_name}/{task_name}")
def schedule_add_task(schedule_name: str, task_name: str):
    """Adds a task to a schedule"""
    response = {"data": "Schedule does not exist."}
    task_id = None
    tasks = storage.get_task_collection()
    if tasks not in [None, {}]:
        for index, task in tasks:
            if task_name == task.get(
                "name"
            ):
                task_id = task.get("id")
    if task_id is None:
        response = {"data": "Task does not exist."}
        storage.logging.debug(response)
        return response
    schedules = storage.get_schedule_collection()
    if schedules not in [None, {}]:
        for index, schedule in schedules:
            if schedule_name == schedule.get(
                "name"
            ):
                schedule["task_id_list"].append(
                    task_id
                )
                response = {"data": "Added task to schedule."}
    storage.logging.debug(response)
    return response


@app.post("/execute-celery-action/{action_id}")
def execute_celery_action(
    action_id: int = Path(
        None,
        description="The ID of the action you would like to run.",
    )
):
    """This function creates a celery task that completes an actions"""
    return celery_worker.run_action.delay(action_id)


@app.get("/execute-action/{action_id}")
def execute_action(
    action_id: int = Path(
        None,
        description="The ID of the action you would like to run.",
    )
):
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    response = {"data": f"Error with action_id:{action_id}"}
    action = storage.get_action(action_id)
    if action:
        response = process_controller.action_controller(action)

    storage.logging.debug(response)
    return response


@app.get("/screenshot/")
def screen_shot():
    """This function only works with Fast API running on your local machine since docker containers run headless"""
    return process_controller.screen_shot()


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


@app.get("/keypress/{key_name}")
def keypress(key_name: str):
    return process_controller.keypress(key_name)


@app.get("/capture-screen-data/{x1}/{y1}/{x2}/{y2}/{action_id}")
def capture_screen_data(x1: int, y1: int, x2: int, y2: int, action_id: int):
    """This function captures data within the region within (x1, y1) and (x2, y2)"""
    return process_controller.capture_screen_data(x1, y1, x2, y2, action_id)
