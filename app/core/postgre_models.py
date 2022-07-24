import pandas as pd
from sqlalchemy import Column, Float, Integer, SmallInteger, String, Table
from postgre_db import Base, db, session
try:
     from . import models
except:
     import models


class Action(Base):
    """Actions represent the smallest process of a task"""
    __tablename__ = 'action'
    name = Column(String(50), primary_key=True)
    function = Column(String(20), nullable=False)
    x1 = Column(Integer, nullable=True)
    x2 = Column(Integer, nullable=True)
    y1 = Column(Integer, nullable=True)
    y2 = Column(Integer, nullable=True)
    images = Column(String(255), nullable=True)
    image_conditions = Column(String(255), nullable=True)
    variables = Column(String(255), nullable=True)
    variable_conditions = Column(String(255), nullable=True)
    comparison_values = Column(String(255), nullable=True)
    created_at = Column(String(50), nullable=True)
    time_delay = Column(Float, nullable=True)
    key_pressed = Column(String(10), nullable=True)
    true_case = Column(String(50), nullable=True)
    false_case = Column(String(50), nullable=True)
    error_case = Column(String(50), nullable=True)
    repeat = Column(SmallInteger, default=0)
    num_repeats = Column(Integer, nullable=True)
    random_path = Column(SmallInteger, default=0)
    random_range = Column(Integer, nullable=True)
    random_delay = Column(Float, nullable=True)


class Task(Base):
    """Tasks represent a collection of actions that complete a goal"""
    __tablename__ = 'task'
    name = Column(String, primary_key=True)
    task_dependency_id = Column(Integer, nullable=True)
    action_id_list = Column(String(255), nullable=True)


class Schedule(Base):
    """Schedule is a series of tasks to run over a given timeframe"""
    __tablename__ = 'schedule'
    name = Column(String, primary_key=True)
    schedule_dependency_id = Column(Integer, nullable=True)
    task_id_list = Column(String(255), nullable=True)


def create():
    Base.metadata.create_all(db)


def seed_db():
    """Seeds json_collection, task_collection, and schedule_lis to the database"""
    action_collection = models.JsonCollectionResource(models.Action)
    task_collection = models.JsonCollectionResource(models.Task)
    schedule_collection = models.JsonCollectionResource(models.Schedule)
    if action_collection.json_collection not in [None, {}]:
        for key in action_collection.json_collection:
            action = action_collection.json_collection[key]
            insert_action(action)
    if task_collection.json_collection not in [None, {}]:
        for key in task_collection.json_collection:
            task = task_collection.json_collection[key]
            insert_task(task)
    if schedule_collection.json_collection not in [None, {}]:
        for key in schedule_collection.json_collection:
            schedule = schedule_collection.json_collection[key]
            insert_schedule(schedule)


def get_actions():
    query = session.query(Action).statement
    actions = pd.read_sql(query, db)
    return actions


def save_actions_to_json():
    df = get_actions()
    df_json = df.to_dict()
    print(df_json)
    action_collection = models.JsonCollectionResource(models.Action)
    new_json_collection = {}
    for index in df.index:
        print(index)
        images = df_json.get("images").get(index).split(', ') if df_json.get("images").get(index) else []
        if df_json.get("images").get(index):
            image_conditions = df_json.get("image_conditions").get(index).split(', ')
        else:
            image_conditions = []
        variables = df_json.get("variables").get(index).split(', ') if df_json.get("images").get(index) else []
        if df_json.get("variable_conditions").get(index):
            variable_conditions = df_json.get("variable_conditions").get(index).split(', ')
        else:
            variable_conditions = []
        if df_json.get("comparison_values").get(index):
            comparison_values = df_json.get("comparison_values").get(index).split(', ')
        else:
            comparison_values = []
        new_json_collection[index] = {
            "id": index,
            "name": df_json.get("name").get(index),
            "function": df_json.get("function").get(index),
            "x1": df_json.get("x1").get(index),
            "x2": df_json.get("x2").get(index),
            "y1": df_json.get("y1").get(index),
            "y2": df_json.get("y2").get(index),
            "images": images,
            "image_conditions": image_conditions,
            "variables": variables,
            "variable_conditions": variable_conditions,
            "comparison_values": comparison_values,
            "created_at": df_json.get("created_at").get(index),
            "time_delay": df_json.get("time_delay").get(index),
            "key_pressed": df_json.get("key_pressed").get(index),
            "true_case": df_json.get("true_case").get(index),
            "false_case": df_json.get("false_case").get(index),
            "error_case": df_json.get("error_case").get(index),
            "repeat": True if df_json.get("repeat").get(index) == 1 else False,
            "num_repeats": df_json.get("num_repeats").get(index),
            "random_path": True if df_json.get("random_path").get(index) == 1 else False,
            "random_range": df_json.get("random_range").get(index),
            "random_delay": df_json.get("random_delay").get(index)
        }
    action_collection.json_collection = new_json_collection
    action_collection.save_collection()


def insert_action(new_action: models.Action):
    images = new_action.get('images')
    images_str = ', '.join(str(x) for x in images)
    image_conditions = new_action.get('image_conditions')
    image_conditions_str = ', '.join(str(x) for x in image_conditions)
    variables = new_action.get('variables')
    variables_str = ', '.join(str(x) for x in variables)
    variable_conditions = new_action.get('variable_conditions')
    variable_conditions_str = ', '.join(str(x) for x in variable_conditions)
    comparison_values = new_action.get('comparison_values')
    comparison_values_str = ', '.join(str(x) for x in comparison_values)
    repeat = 0 if new_action.get('repeat') is False else 1
    random_path = 0 if new_action.get('random_path') is False else 1
    insert_new_action = Action(name=new_action.get('name'),
                               function=new_action.get('function'),
                               x1=new_action.get('x1'),
                               x2=new_action.get('x2'),
                               y1=new_action.get('y1'),
                               y2=new_action.get('y2'),
                               images=images_str,
                               image_conditions=image_conditions_str,
                               variables=variables_str,
                               variable_conditions=variable_conditions_str,
                               comparison_values=comparison_values_str,
                               created_at=new_action.get('created_at'),
                               time_delay=new_action.get('time_delay'),
                               key_pressed=new_action.get('key_pressed'),
                               true_case=new_action.get('true_case'),
                               false_case=new_action.get('false_case'),
                               error_case=new_action.get('error_case'),
                               repeat=repeat,
                               num_repeats=new_action.get('num_repeats'),
                               random_path=random_path,
                               random_range=new_action.get('random_range'),
                               random_delay=new_action.get('random_delay'))
    session.add(insert_new_action)
    session.commit()


def delete_action(name: str):
    address_table = Table('action', Base.metadata, autoload=True)
    session.query(address_table).where(address_table.c.name == name).delete()
    session.commit()


def get_tasks():
    query = session.query(Task).statement
    tasks = pd.read_sql(query, db)
    return tasks


def save_tasks_to_json():
    df = get_tasks()
    df_json = df.to_dict()
    print(df_json)
    task_collection = models.JsonCollectionResource(models.Task)
    new_task_collection = {}
    for index in df.index:
        ids = df_json.get("action_id_list").get(index).split(', ') if df_json.get("action_id_list").get(index) else []
        new_task_collection[index] = {
            "id": index,
            "name": df_json.get("name").get(index),
            "task_dependency_id": df_json.get("task_dependency_id").get(index),
            "action_id_list": ids,
        }
    task_collection.task_collection = new_task_collection
    task_collection.save_collection()


def insert_task(new_task: models.Task):
    action_id_list = new_task.get('action_id_list')
    action_id_list_str = ', '.join(str(x) for x in action_id_list)
    insert_new_task = Task(name=new_task.get('name'),
                           task_dependency_id=new_task.get('task_dependency_id'),
                           action_id_list=action_id_list_str)
    session.add(insert_new_task)
    session.commit()

def delete_task(name: str):
    address_table = Table('task', Base.metadata, autoload=True)
    session.query(address_table).where(address_table.c.name == name).delete()
    session.commit()


def get_schedules():
    query = session.query(Schedule).statement
    schedules = pd.read_sql(query, db)
    return schedules


def save_schedules_to_json():
    df = get_schedules()
    df_json = df.to_dict()
    schedule_collection = models.JsonCollectionResource(models.Schedule)
    new_json_collection = {}
    for index in df.index:
        ids = df_json.get("task_id_list").get(index).split(', ') if df_json.get("task_id_list").get(index) else []
        new_json_collection[index] = {
            "id": index,
            "name": df_json.get("name").get(index),
            "schedule_dependency_id": df_json.get("schedule_dependency_id").get(index),
            "task_id_list": ids,
        }
    schedule_collection.json_collection = new_json_collection
    schedule_collection.save_collection()


def insert_schedule(new_schedule: models.Schedule):
    task_id_list = new_schedule.get('task_id_list')
    task_id_list_str = ', '.join(str(x) for x in task_id_list)
    insert_new_schedule = Schedule(name=new_schedule.get('name'),
                                   schedule_dependency_id=new_schedule.get('schedule_dependency_id'),
                                   task_id_list=task_id_list_str)
    session.add(insert_new_schedule)
    session.commit()


def delete_schedule(name: str):
    address_table = Table('schedule', Base.metadata, autoload=True)
    session.query(address_table).where(address_table.c.name == name).delete()
    session.commit()

"""
#  Tests for functions
if __name__ == "__main__":
    create()
    seed_db()
    actions_df = get_actions()
    print(actions_df)
    delete_action("2022-06-06T23:56:36.025Z")
    actions_df = get_actions()
    print(actions_df)
    save_actions_to_json()
"""
