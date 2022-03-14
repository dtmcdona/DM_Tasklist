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
    return action_list_obj.action_list[action_id]


@app.post('/add-action')
def add_action(new_action: Action):
    if new_action in action_list_obj.action_list:
        return {'Data': f'{new_action.name} already exists.'}
    action_list_obj.add_action(new_action)
    return {'Data': 'Action added'}


@app.put("/update-action/{action_id}")
def update_action(action_id: int, new_action: Action):
    if action_id >= len(action_list_obj.action_list) or action_id < 1:
        return {'Data': 'Invalid ID entered.'}
    if action_list_obj.action_list[action_id].name == new_action.name and action_list_obj.action_list[action_id].code == new_action.code:
        return {'Data': 'New data matches old data.'}
    action_list_obj.action_list[action_id] = new_action
    return {'Data': 'Action updated'}


@app.get("/get-tasks")
def get_tasks():
    if len(task_list_obj.task_list) > 0:
        return task_list_obj.task_list
    return {'Data': 'Not found'}


@app.get("/get-task/{task_name}")
def get_task(task_name: str = Path(1, description="The name of the task you would like to view.")):
    for index in task_list_obj.task_list:
        if index[task_name]:
            return index
    return {'Data': 'Not found'}


@app.post('/add-tasklist')
def add_tasklist(task: Task):
    if task in task_list_obj.task_list:
        return {'Data': 'Tasklist already exists.'}
    else:
        task_list_obj.add_task(task)
        return {'Data': 'Tasklist has been added to tasks.'}


@app.post('/tasks-add-action/{tasklist_id}')
def tasklist_add_action(tasklist_id: int, new_action: Action):
    if new_action in action_list_obj.action_list:
        task_list_obj.action_list[tasklist_id].append(new_action.id)
        return {'Data': 'Action has been added to the task list.'}
    else:
        action_list_obj.add_action(new_action)
        task_list_obj.action_list[tasklist_id].append(new_action.id)
        return {'Data': 'New action has been added action and task lists.'}


@app.get("/get-schedule/")
def get_schedule():
    if len(schedule_list_obj.schedule_list) > 0:
        return schedule_list_obj.schedule_list
    return {'Data': 'Not found'}


@app.get("/get-schedule/{schedule_id}")
def get_schedule(schedule_id: int = Path(1, description="The ID of the schedule you would like to view.")):
    return schedule_list_obj.schedule_list[schedule_id]


@app.post('/schedule-add-task/{task_list_id}')
def tasklist_add_task(task_list_id: int):
    if task_list_id < len(task_list_obj.task_list):
        schedule_list_obj.schedule_list[len(schedule_list_obj.schedule_list)].task_id_list.append(task_list_id)
        return {'Data': 'Tasklist has been added to the schedule.'}
    else:
        return {'Data': 'Tasklist does not exist.'}
