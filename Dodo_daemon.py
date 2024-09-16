import keyboard
import subprocess
from Dodo_config import PYTHON,HOTKEY
import os

cwd = os.getcwd()

keyboard.add_hotkey(HOTKEY, lambda: subprocess.Popen('cmd /c '+PYTHON+' '+cwd+'\\DodoUI2.py'))
keyboard.wait()