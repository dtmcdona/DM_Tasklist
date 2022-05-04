import os

import base64
import cv2
import time
from celery import Celery
from pyautogui import size, position, moveTo, click, keyUp, keyDown, screenshot
from typing import List


celery = Celery(
    __name__,
    broker="amqp://user:password@broker:5672"
)


@celery.task(name="run_action")
def run_action(action_str_list: List[str]):
    for action_str in action_str_list:
        if action_str.startswith("click") or action_str.startswith("moveTo"):
            action = "click"
            if action_str.startswith("click"):
                params = action_str.lstrip("click(x=")
            else:
                action = "moveTo"
                params = action_str.lstrip("moveTo(x=")
            params = params.rstrip(")")
            params = params.split(", y=")
            if len(params) is 2:
                x = params[0]
                y = params[1]
                if action is "click":
                    click(x=x, y=y)
                    return f'Mouse clicked: ({x}, {y})'
                else:
                    moveTo(x=x, y=y)
                    return f'Mouse moved to: ({x}, {y})'
        elif action_str.startswith("keypress"):
            param = action_str.lstrip("keypress(\"")
            param = param.rstrip("\")")
            keyDown(param)
            time.sleep(1)
            keyUp(param)
            return f"Key pressed {param}"
        elif action_str.startswith("screenshot"):
            screenshot("screenshot.png")
            img = cv2.imread('screenshot.png')
            png_img = cv2.imencode('.png', img)
            b64_string = base64.b64encode(png_img[1]).decode('utf-8')
            return b64_string
        elif action_str.startswith("say_hello"):
            param = action_str.lstrip("say_hello(\"")
            param = param.rstrip("\")")
            return f"Hello {param}"

    return 'Action not processed.'

