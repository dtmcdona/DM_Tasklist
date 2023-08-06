import pytest
from core.async_process_controller import get_image_present_result


class TestAsyncProcessController:
    @pytest.mark.asyncio
    async def test_get_image_present_result__images_found(self):
        test_action = {
            "function": "capture_screen_data",
            "x1": 0,
            "y1": 0,
            "x2": 132,
            "y2": 32,
            "images": ["test_image_present_1.png", "test_image.png"],
            "haystack_image": "test_image.png",
            "image_conditions": ["if_image_present"],
        }
        result = await get_image_present_result(test_action)
        assert result == True

    @pytest.mark.asyncio
    async def test_get_image_present_result__images_not_found(self):
        test_action = {
            "function": "capture_screen_data",
            "x1": 0,
            "y1": 0,
            "x2": 132,
            "y2": 32,
            "images": ["test_image_present_1.png" for _ in range(3)],
            "haystack_image": "test_image.png",
            "image_conditions": ["if_image_present"],
        }
        result = await get_image_present_result(test_action)
        assert result == False
