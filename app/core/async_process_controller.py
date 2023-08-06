"""
These functions are used to search for multiple images within a screen by
using a ProcessPoolExecutor.  This is used to speed up the search for
multiple images.  The functions are called from app/core/process_controller.py
within asyncio.run().
"""
import asyncio
import tracemalloc
from concurrent.futures.process import ProcessPoolExecutor
from typing import Optional

from . import models, process_controller


async def get_image_present_result(
    action: models.Action, screenshot_file: str = None
) -> bool:
    """Evaluates conditionals for an action"""
    images = action.get("images")
    haystack_image = action.get("haystack_image")
    haystack_file_name = haystack_image or screenshot_file
    with ProcessPoolExecutor(initializer=tracemalloc.start) as ppe:
        batches = [evaluate_image_conditional(ppe, image, haystack_file_name) for image in images]
        done, pending = await asyncio.wait(batches)
    assert len(pending) == 0
    results = [task.result() for task in done]
    return any(results)

async def evaluate_image_conditional(
    pool: ProcessPoolExecutor, variable_value: str, comparison_value: Optional[str] = None
) -> Optional[bool]:
    """Comparison value is provided by user and the variable_value is from
    capture_screen_data action.  This is used to compare the two values
    and return a boolean result."""
    """Check to see if image is present before doing action"""
    loop = asyncio.get_event_loop()
    x, y = await loop.run_in_executor(
        pool, process_controller.image_search, variable_value, comparison_value, 0.9, False
    )
    if x == -1 or y == -1:
        return False
    return True