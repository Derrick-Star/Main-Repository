import pyautogui
import string
import random
import time
import os

# Open Notepad (optional)
os.system("start notepad")
time.sleep(2)

# Duration to run (in seconds)
RUN_TIME = 7 * 60  # 7 minutes

# All hacker-looking characters
characters = string.ascii_letters + string.digits + string.punctuation

while True:
    start = time.time()
    stroke_count = 0

    while time.time() - start < RUN_TIME:
        char = random.choice(characters)
        pyautogui.typewrite(char)
        stroke_count += 1

        if stroke_count % 700 == 0:
            pyautogui.press("enter")

        time.sleep(0.01)  # adjust for speed — lower = faster typing

    # After 7 mins, press Enter and restart
    pyautogui.press("enter")
    pyautogui.typewrite(">>> Restarting sequence <<<", interval=0.05)
    pyautogui.press("enter")
    time.sleep(1)