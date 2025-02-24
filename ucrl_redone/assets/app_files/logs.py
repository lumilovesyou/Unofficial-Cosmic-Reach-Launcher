import sys
import os
import datetime as dt
import random as ran
import inspect

savedSelf = None

#Need to add system information to logs

def log(text: str, filePath: str = "logs"):
    caller_frame = inspect.stack()[1]
    caller_file = os.path.basename(caller_frame.filename)
    date = dt.datetime.now()
    if text[0:2] == "%e":
        message = f"%e [{date.hour}.{date.minute}.{date.second}] {caller_file}: {text[2:len(text)]}"
    else:
        message = f"[{date.hour}.{date.minute}.{date.second}] {caller_file}: {text}"
    with open(f"{filePath}/latest.log", "a") as file:
        file.write(f"{message}\n")
        file.close
    with open(f"{filePath}/latest.log", "r") as file:
        output = file.read()
        file.close
    print(output)
        
def cleanLatest(filePath: str = "logs"):
    if not os.path.exists(filePath):
        os.mkdir(filePath)
    elif os.path.exists(f"{filePath}/latest.log"):
        with open(f"{filePath}/latest.log", "r") as file:
            name = file.readline().strip() or ran.randint(23891687, 38214792938479382)
        os.rename(f"{filePath}/latest.log", f"{filePath}/{name}.log")
        
def checkLatest(filePath: str = "logs"):
    if not os.path.exists(f"{filePath}/latest.log"):
        date = dt.datetime.now()
        with open(f"{filePath}/latest.log", "w") as file:
            file.write(f"{date.year}-{date.month}-{date.day} at {date.hour}.{date.minute}.{date.second}\n")

def prepareLogs(filePath: str = "logs"):
    cleanLatest(filePath)
    checkLatest(filePath)

def passSelf(self):
    savedSelf = self