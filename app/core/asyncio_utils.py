import asyncio
import logging
from typing import List, Union

import aiohttp

logging.basicConfig(level=logging.DEBUG)


async def get_requests(urls: List[str]):
    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*[session.get(url) for url in urls])
        return {"data": [response.status for response in responses]}


async def post_requests(
    urls: List[str], json_payloads: Union[dict, List[dict]]
):
    if not isinstance(json_payloads, list):
        json_payloads = [json_payloads for _ in range(len(urls))]
    post_args = zip(urls, json_payloads)
    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(
            *[session.post(url=url, json=payload) for url, payload in post_args]
        )
        return {"data": [response.status for response in responses]}
