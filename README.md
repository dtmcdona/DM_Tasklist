# Tasklist
Simple task list that you could use for a todo list in a console or in uvicorn running fastapi endpoints.

To run this project via uvicorn you will need to install the following:
1. ```pip install fastapi```
2. ```pip install uvicorn```

Next you can run the app with uvicorn with the following command:
```angular2html
cd app
uvicorn core.fast_api_taskboard:app --host 0.0.0.0 --port 8002 --reload
```

If you want pyautogui automation then use the following command:
```angular2html
cd app
uvicorn core.fast_api_automation:app --host 0.0.0.0 --port 8002 --reload
```