# DM_Tasklist
This project is a basic RPA system that uses Fast API endpoints as a backend for storing action 
sequences and streams screen data to the React.js frontend project (DM_React)

# Docker setup
1. Docker compose up
   ```angular2html
      make dcu
   ```
2. To use the pytest tests:
   ```angular2html
      make tests
   ```

# Local system setup:
1. This project uses a virtual xvfb display but if you would like to disable this feature then 
comment out or remove these from `app/core/process_controller.py`
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
2. Install tesseract-ocr for pytesseract
   ```angular2html
   sudo apt install tesseract-ocr -y
   ```
3. Install this for pyenchant: 
   ```angular2html
   sudo apt-get install libenchant1c2a -y
   ```
4. Make a new virtual environment and install requirements.txt
   ```angular2html
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. This terminal commands will run the system on your local system:
   ```angular2html
   make local
   ```

# Note:
I created two PostgreSQL adapter files with credentials in settings.py. The adapters are not part of the back-end.
If you would like to use the PostgreSQL adapters then you need to setup a PostgreDB that match settings.py and connect
the adapters to the endpoints.
Currently, there is no need for a database but in the future it might be useful.
