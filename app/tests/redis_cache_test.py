from core import redis_cache


class TestRedisCache:
    def test_redis_get_and_set(self):
        redis_cache.set_condition_result("test_key", "test_value")
        res = redis_cache.get_condition_result("test_key")
        assert res is True

    def test_redis_key_dne(self):
        res = redis_cache.get_condition_result("test_key_dne")
        assert res is None
