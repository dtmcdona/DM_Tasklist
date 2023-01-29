from uuid import uuid4

from core import redis_cache


class TestRedisCache:
    def test_redis_set_and_get(self):
        key = f"test_key-{uuid4()}"
        redis_cache.set_condition_result(key, False)
        res = redis_cache.get_condition_result(key)
        assert res is False
        redis_cache.set_condition_result(key, True)
        res = redis_cache.get_condition_result(key)
        assert res is True

    def test_redis_key_dne(self):
        res = redis_cache.get_condition_result("test_key_dne")
        assert res is None

    def test_json_set_and_get(self):
        json_dict = {
            "str": "str",
            "int": 1,
            "bool": True,
            "str_array": ["str1", "str2"],
            "int_array": [1, 2],
            "bool_array": [True, False],
            "nested_dict": {
                "0": "str",
                "1": 1,
                "2": False,
            }
        }
        json_type = "json_type_test"
        id = str(uuid4())
        redis_cache.set_json(json_type, id, json_dict)
        res = redis_cache.get_json(json_type, id)
        assert res == json_dict

    def test_get_json_dne(self):
        json_type = f"dne_test"
        index = 0
        assert not redis_cache.get_json(json_type, index)

