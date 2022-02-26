from fastapi import FastAPI, Path
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel


app = FastAPI()


class Action(BaseModel):
    name: str
    code: List[str]


actions = [
    Action(name='sayhello', code=['Hello user!']),
    Action(name='init', code=['What tasks would you like to add?']),
    Action(name='finished', code=['Task finished.'])
]

tasks = {
    'startup': [
        Action(name='sayhello', code=['print(\'Hello user!\')']),
        Action(name='init', code=['print(\'What tasks would you like to add?\')'])
    ]
}


schedule = {
    0: {
        'name': 'Task1',
        'numActions': len(tasks['startup']),
        'tasklist': tasks['startup']
    }
}


@app.get('/')
def home():
    return {'Data': 'Testing'}


@app.get("/get-schedule/")
def get_schedule():
    if len(schedule) > 0:
        return schedule
    return {'Data': 'Not found'}


@app.get("/get-schedule/{schedule_id}")
def get_schedule(schedule_id: int = Path(1, description="The ID of the schedule you would like to view.")):
    return schedule[schedule_id]


@app.get("/get-tasks")
def get_tasks():
   if len(tasks) > 0:
        return tasks
   return {'Data': 'Not found'}


@app.get("/get-task/{task_name}")
def get_task(task_name: str = Path(1, description="The name of the task you would like to view.")):
   if tasks[task_name]:
        return tasks[task_name]
   return {'Data': 'Not found'}


@app.get("/get-actions/")
def get_actions():
    return actions


@app.get("/get-action/{action_id}")
def get_action(action_id: int = Path(None, description="The ID of the action you would like to view.")):
    return actions[action_id]


@app.get("/get-task-action-by-name/{task_name}")
def get_task_action_by_name(task_name: str, action_name: str):
    for action_index in tasks[task_name]:
        if action_index.name == action_name:
            return action_index
    return {'Data': 'Not found'}

@app.post('/add-action')
def add_action(newaction: Action):
    if newaction in actions:
        return {'Data': f'{newaction.name} already exists.'}

    actions.append(newaction)
    return actions[-1]


@app.post('/add-tasklist')
def add_tasklist(tasklist_name: str):
    if tasklist_name in tasks:
        return {'Data': 'Tasklist already exists.'}
    else:
        tasks[tasklist_name] = []
        return {'Data': 'Tasklist has been added to tasks.'}


@app.post('/tasks-add-action/{tasklist_name}')
def tasklist_add_action(tasklist_name: str, newaction: Action):
    if newaction in actions:
        tasks[tasklist_name].append(newaction)
        return {'Data': 'Action has been added to the task list.'}
    else:
        actions.append(newaction)
        tasks[tasklist_name].append(newaction)
        return {'Data': 'New action has been added action and task lists.'}

@app.post('/schedule-add-task/{tasklist_name}')
def tasklist_add_task(tasklist_name: str):
    if tasklist_name in tasks:
        schedule[len(schedule)] = tasks[tasklist_name]
        return {'Data': 'Tasklist has been added to the schedule.'}
    else:
        return {'Data': 'Tasklist does not exist.'}

@app.put("/update-action/{action_id}")
def update_action(action_id: int, newaction: Action):
    if action_id >= len(actions) or action_id < 0:
        return {'Data': 'Invalid ID entered.'}
    if actions[action_id].name == newaction.name and actions[action_id].code == newaction.code:
        return {'Data': 'New data matches old data.'}
    else:
        actions[action_id] = newaction
        return {'Data': 'Action updated.'}

