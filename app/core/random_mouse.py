import random
import time

from . import process_controller


def random_move(x: int, y: int):
    """Choose a random amount of segments to move to x, y"""
    random_steps = random.randrange(6, 18)
    """Loop through all the random moves of mouse to get closer to x, y"""
    while random_steps < 24:
        current_mouse_x, current_mouse_y = process_controller.mouse_pos()
        """Choose a random destination to move the mouse closer to x, y"""
        if x < current_mouse_x:
            step_distance_x = int((current_mouse_x - x) / (24 - random_steps))
            random_destination_x = random.randrange(
                current_mouse_x - step_distance_x, current_mouse_x
            )
        else:
            step_distance_x = int((x - current_mouse_x) / (24 - random_steps))
            random_destination_x = random.randrange(
                current_mouse_x, current_mouse_x + step_distance_x
            )
        if y < current_mouse_y:
            step_distance_y = int((current_mouse_y - y) / (24 - random_steps))
            random_destination_y = random.randrange(
                current_mouse_y - step_distance_y, current_mouse_y
            )
        else:
            step_distance_y = int((x - current_mouse_y) / (24 - random_steps))
            random_destination_y = random.randrange(
                current_mouse_y, current_mouse_y + step_distance_y
            )

        random_move_duration = (random.randrange(0, 250, 6)) / 1000
        process_controller.mouse_move(
            random_destination_x,
            random_destination_y,
            random_move_duration,
        )
        random_steps += 1

    """Finish by moving mouse to x, y"""
    random_move_duration = (random.randrange(0, 500, 6)) / 1000
    process_controller.mouse_move(x, y, random_move_duration)


def random_click(
    x: int,
    y: int,
    rand_range: int = 0,
    delay_duration: float = 0,
    mouse_button: str = "left",
):
    """Click random destionation within radius equal to rand_rang and delay the click by delay_duration"""
    if rand_range > 0:
        random_x = x + random.randrange(-rand_range, rand_range)
        random_y = y + random.randrange(-rand_range, rand_range)
    else:
        random_x = x
        random_y = y

    if delay_duration > 0:
        time.sleep(delay_duration)

    random_duration = (random.randrange(150, 450, 6)) / 1000
    process_controller.mouse_up(mouse_button=mouse_button)
    process_controller.mouse_move(random_x, random_y)
    process_controller.mouse_down(mouse_button=mouse_button)
    time.sleep(random_duration)
    process_controller.mouse_up(mouse_button=mouse_button)


def mouse_drift():
    """Function to make the user seem more human with slightly moving mouse"""
    random_repeat = random.randrange(0, 6)
    while random_repeat < 3:
        current_mouse_x, current_mouse_y = process_controller.mouse_pos()
        rand = random.randrange(0, 15)
        random_destination_x = current_mouse_x + random.randrange(-rand, rand)
        rand = random.randrange(0, 15)
        random_destination_y = current_mouse_y + random.randrange(-rand, rand)
        random_move_duration = (random.randrange(0, 500, 6)) / 1000
        process_controller.mouse_move(
            random_destination_x,
            random_destination_y,
            random_move_duration,
        )
        random_repeat += 1
