# DM_Tasklist
This project is a basic RPA system that uses Fast API endpoints as a backend for storing action 
sequences and it streams screen data to the React.js frontend project (DM_React)

To run this project via uvicorn you will need to install the following:
1. Navigate to app/core/resources and make these directories: "images", "screen_data" and "screenshot"
2. Create a new virtual environment and install requirements.txt
3. Run fast_api_taskboard in a docker container or run fast_api_automation on host

Note: In the future I will modify the docker container with a virtual xvfb display once most
of the core features are completed

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
