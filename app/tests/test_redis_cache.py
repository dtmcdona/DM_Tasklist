from uuid import uuid4

from core import redis_cache


class TestRedisCache:
    def test_redis_set_and_get(self):
        key_name = f"test_key-{uuid4}"
        redis_cache.set_condition_result(key_name, False)
        res = redis_cache.get_condition_result(key_name)
        assert res is False
        key_name = f"test_key-{uuid4}"
        redis_cache.set_condition_result(key_name, True)
        res = redis_cache.get_condition_result(key_name)
        assert res is True

    def test_redis_key_dne(self):
        res = redis_cache.get_condition_result("test_key_dne")
        assert res is None
