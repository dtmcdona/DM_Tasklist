"""
Random mouse creates more human and randomized paths for moving the mouse,
clicking a randomized location within a range, and slightly moving the mouse
around.
"""
import random
import time

from . import process_controller


def random_move(x: int, y: int) -> None:
    """Choose a random amount of segments to move to x, y"""
    random_steps = random.randint(6, 17)

    for _ in range(24 - random_steps):
        current_mouse_x, current_mouse_y = process_controller.mouse_pos()

        if x < current_mouse_x:
            step_distance_x = (current_mouse_x - x) // (24 - random_steps)
            random_destination_x = random.randint(
                current_mouse_x - step_distance_x, current_mouse_x
            )
        else:
            step_distance_x = (x - current_mouse_x) // (24 - random_steps)
            random_destination_x = random.randint(
                current_mouse_x, current_mouse_x + step_distance_x
            )

        if y < current_mouse_y:
            step_distance_y = (current_mouse_y - y) // (24 - random_steps)
            random_destination_y = random.randint(
                current_mouse_y - step_distance_y, current_mouse_y
            )
        else:
            step_distance_y = (y - current_mouse_y) // (24 - random_steps)
            random_destination_y = random.randint(
                current_mouse_y, current_mouse_y + step_distance_y
            )

        random_move_duration = random.randrange(0, 250, 6) / 1000
        process_controller.mouse_move(
            random_destination_x, random_destination_y, random_move_duration
        )

    random_move_duration = random.randrange(0, 500, 6) / 1000
    process_controller.mouse_move(x, y, random_move_duration)


def random_click(
    x: int,
    y: int,
    rand_range: int = 0,
    delay_duration: float = 0,
    mouse_button: str = "left",
) -> None:
    """Click a random destination within a radius of rand_range and delay the click by delay_duration"""
    random_x = (
        x + random.randint(-rand_range, rand_range) if rand_range > 0 else x
    )
    random_y = (
        y + random.randint(-rand_range, rand_range) if rand_range > 0 else y
    )

    time.sleep(delay_duration)

    random_duration = random.randrange(150, 450, 6) / 1000
    process_controller.mouse_up(mouse_button=mouse_button)
    process_controller.mouse_move(random_x, random_y)
    process_controller.mouse_down(mouse_button=mouse_button)
    time.sleep(random_duration)
    process_controller.mouse_up(mouse_button=mouse_button)


def mouse_drift() -> None:
    """Function to make the user seem more human with slight mouse movement"""
    for _ in range(random.randint(0, 5)):
        current_mouse_x, current_mouse_y = process_controller.mouse_pos()
        rand = random.randint(0, 14)
        random_destination_x = current_mouse_x + random.randint(-rand, rand)
        random_destination_y = current_mouse_y + random.randint(-rand, rand)
        random_move_duration = random.randrange(0, 500, 6) / 1000
        process_controller.mouse_move(
            random_destination_x, random_destination_y, random_move_duration
        )
