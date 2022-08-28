# DM_Tasklist
This project is a basic RPA system that uses Fast API endpoints as a backend for storing action 
sequences and streams screen data to the React.js frontend project (DM_React)

To run this project via uvicorn you will need to install the following:
1. This project uses a virtual xvfb display but if you would like to disable this feature then 
comment out or remove this from process_controller.py
   ```angular2html
   """Virtual display setup has to be setup before pyautogui is imported"""
   import Xlib.display
   from pyvirtualdisplay.display import Display
   disp = Display(visible=True, size=(1920, 1080), backend="xvfb", use_xauth=True)
   disp.start()
   ```
   ```angular2html
   """Virtual display"""
   pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ["DISPLAY"])
   ```
2. You can build the project or run locally with a new virtual environment and install requirements.txt
   1. If you decide to run the project locally then install tesseract-ocr 
      ```angular2html
      sudo apt install tesseract-ocr -y
      ```
4. Run fast_api_taskboard in a docker container or run fast_api_automation on your local system

This terminal commands will run the system on your local system:
```angular2html
cd app
uvicorn core.fast_api_automation:app --host 0.0.0.0 --port 8003 --reload
```

I created two PostgreSQL adapter files with credentials in settings.py. The adapters are not part of the back-end.
If you would like to use the PostgreSQL adapters then you need to setup a PostgreDB that match settings.py and connect
the adapters to the endpoints.
Currently, there is no need for a database but in the future it might be useful.
