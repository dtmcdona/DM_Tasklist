from fastapi import FastAPI, Path
from models import Action, ActionList, Task, TaskList, Schedule, ScheduleList


app = FastAPI()


action_list_obj = ActionList()
action_list_obj.load_action_list()
task_list_obj = TaskList()
task_list_obj.load_task_list()
schedule_list_obj = ScheduleList()
schedule_list_obj.load_schedule_list()


@app.get('/')
def home():
    return {'Data': 'Testing'}


@app.get("/get-actions/")
def get_actions():
    return action_list_obj.action_list


@app.get("/get-action/{action_id}")
def get_action(action_id: int = Path(None, description="The ID of the action you would like to view.")):
    if action_list_obj.action_list.get(str(action_id)):
        response = action_list_obj.action_list.get(str(action_id))
    else:
        response = {'Data': 'Action not found.'}
    return response


@app.post('/add-action')
def add_action(new_action: Action):
    response = action_list_obj.add_action(new_action)
    return response


@app.put("/update-action/{action_id}")
def update_action(action_id: int, new_action: Action):
    if action_id >= len(action_list_obj.action_list) or action_id < 0:
        return {'Data': 'Invalid ID entered.'}
    if action_list_obj.action_list[str(action_id)].get('name') == new_action.name and \
            action_list_obj.action_list[str(action_id)].get('code') == new_action.code:
        return {'Data': 'New data matches old data.'}
    action_list_obj.action_list[str(action_id)] = new_action
    return {'Data': 'Action updated'}


@app.get("/get-tasks")
def get_tasks():
    if len(task_list_obj.task_list) > 0:
        return task_list_obj.task_list
    return {'Data': 'Not found'}


@app.get("/get-task/{task_name}")
def get_task(task_name: str = Path(1, description="The name of the task you would like to view.")):
    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                return task_list_obj.task_list[key]
    return {'Data': 'Task not found.'}


@app.post('/add-task')
def add_task(task: Task):
    response = task_list_obj.add_task(task)
    return response


@app.post('/tasks-add-action/{tasklist_name}')
def task_add_action(task_name: str, new_action: Action):
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
                return {'Data': 'Action has been added to the task list.'}
    return {'Data': f'Task {task_name} does not exist.'}


@app.get("/get-schedules/")
def get_schedules():
    if len(schedule_list_obj.schedule_list) > 0:
        return schedule_list_obj.schedule_list
    return {'Data': 'Not found'}


@app.get("/get-schedule/{schedule_name}")
def get_schedule(schedule_name: str = Path(1, description="The ID of the schedule you would like to view.")):
    if schedule_list_obj.schedule_list not in [None, {}]:
        for key in schedule_list_obj.schedule_list:
            if schedule_name == schedule_list_obj.schedule_list[key].get('name'):
                return schedule_list_obj.schedule_list[key]
    return {'Data': 'Not found'}


@app.post('/schedule-add-task/{schedule_name}/{task_list_name}')
def schedule_add_task(schedule_name: str, task_name: str):
    task_id = None
    if task_list_obj.task_list not in [None, {}]:
        for key in task_list_obj.task_list:
            if task_name == task_list_obj.task_list[key].get('name'):
                task_id = task_list_obj.task_list[key].get('id')
    if task_id is None:
        return {'Data': 'Task does not exist.'}
    if schedule_list_obj.schedule_list not in [None, {}]:
        for key in schedule_list_obj.schedule_list:
            if schedule_name == schedule_list_obj.schedule_list[key].get('name'):
                schedule_list_obj.schedule_list[key]['task_id_list'].append(task_id)
                return {'Data': 'Added task to schedule.'}
    return {'Data': 'Schedule does not exist.'}
