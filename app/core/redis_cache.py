import redis


rc = redis.Redis(host="redis", port=6379, db=0)


def set_condition_result(key, result):
    rc.set(key, str(result))


def get_condition_result(key):
    cached_value = rc.get(str(key))
    return eval(cached_value.decode("utf-8")) if cached_value else None
