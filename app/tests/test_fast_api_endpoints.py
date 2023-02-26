import pytest
from core.fast_api_endpoints import app
from httpx import AsyncClient
from .mixins import ModelMixin

"""
class TestFastAPIEndpoints(ModelMixin):

    async def get_request(self, path):
        async with AsyncClient(app=app, base_url="http://localhost:8003") as ac:
            await ac.get(path)

    @pytest.mark.anyio
    async def test_get_action(self):
        await self.get_request("/get-action/0")

    @pytest.mark.anyio
    async def test_get_action(self):
        await self.get_request("/get-actions")

    @pytest.mark.anyio
    async def test_get_action(self):
        await self.get_request("/get-tasks")
"""
