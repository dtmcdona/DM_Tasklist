import time
import pyautogui
import random


def random_move(x: int, y: int):
    # Choose a random amount of segments to move to x, y
    random_steps = random.randrange(3, 9)
    # Loop through all the random moves of mouse to get closer to x, y
    while random_steps < 12:
        current_mouse_x, current_mouse_y = pyautogui.position()
        # Choose a random destination to move the mouse closer to x, y
        if x < current_mouse_x:
            step_distance_x = int((current_mouse_x - x) / (12 - random_steps))
            random_destination_x = random.randrange(current_mouse_x, current_mouse_x - step_distance_x)
        else:
            step_distance_x = int((x - current_mouse_x) / (12 - random_steps))
            random_destination_x = random.randrange(current_mouse_x, current_mouse_x + step_distance_x)
        if y < current_mouse_y:
            step_distance_y = int((current_mouse_y - y) / (12 - random_steps))
            random_destination_y = random.randrange(current_mouse_y, current_mouse_y - step_distance_y)
        else:
            step_distance_y = int((x - current_mouse_y) / (12 - random_steps))
            random_destination_y = random.randrange(current_mouse_y, current_mouse_y + step_distance_y)

        random_move_duration = (random.randrange(0, 500, 6)) / 1000
        pyautogui.moveTo(random_destination_x, random_destination_y, random_move_duration)
        random_steps += 1

    # Finish by moving mouse to x, y
    pyautogui.moveTo(x, y)


def random_click(x: int, y: int, rand_range: int = 0, delay_duration: float = 0, mouse_button: str = 'left'):
    if rand_range > 0:
        random_x = x + random.randrange(-rand_range, rand_range)
        random_y = y + random.randrange(-rand_range, rand_range)
    else:
        random_x = x
        random_y = y

    if delay_duration > 0:
        time.sleep(delay_duration)

    random_duration = (random.randrange(150, 450, 6)) / 1000
    pyautogui.moveTo(random_x, random_y)
    pyautogui.mouseDown(button=mouse_button)
    time.sleep(random_duration)
    pyautogui.mouseUp(button=mouse_button)


def mouse_drift():
    # Function to make the user seem more human with slightly moving mouse on accident/boredom
    random_repeat = random.randrange(0, 6)
    while random_repeat < 3:
        current_mouse_x, current_mouse_y = pyautogui.position()
        rand = random.randrange(0, 15)
        random_destination_x = random.randrange(-rand, rand)
        rand = random.randrange(0, 15)
        random_destination_y = random.randrange(-rand, rand)
        random_move_duration = (random.randrange(0, 500, 6)) / 1000
        pyautogui.moveTo(random_destination_x, random_destination_y, random_move_duration)
        random_repeat += 1