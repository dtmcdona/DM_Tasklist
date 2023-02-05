"""
Redis is only used for storing and retrieving the result of
celery workers and caching the action collection since it is used
frequently.  This is mainly used by the Task Manager to offload
more expensive image processing to celery workers and allow some
endpoints to be async.
"""
from typing import Optional

import redis
from redis.commands.json.path import Path


rc = redis.Redis(host="redis", port=6379, db=0)


def set_condition_result(key: str, result: bool) -> None:
    rc.set(key, str(result))


def get_condition_result(key: str) -> Optional[bool]:
    cached_value = rc.get(key)
    return eval(cached_value.decode("utf-8")) if cached_value else None


def set_json(json_type: str, obj_id: str, json_dict: dict) -> None:
    json_cache = {json_type: json_dict}
    rc.json().set(f"{json_type}:{obj_id}", Path.root_path(), json_cache)


def get_json(json_type: str, obj_id: str) -> dict:
    cached_value = None
    try:
        cache_dict = rc.json().get(f"{json_type}:{obj_id}")
        cached_value = cache_dict.get(json_type)
    except Exception as e:
        print(e)

    return cached_value


def del_json(json_type: str, obj_id: str) -> None:
    try:
        rc.json().delete(f"{json_type}:{obj_id}", Path.root_path())
    except Exception as e:
        print(e)
