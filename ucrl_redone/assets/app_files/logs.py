import sys
import os
import datetime as dt
import random as ran
import inspect
from .system import checkOs, returnOsName
from .app_info_and_update import returnAppVersion

savedSelf = None

#Need to add system information to logs

def log(text: str, filePath: str = "logs"):
    caller_frame = inspect.stack()[1]
    caller_file = os.path.basename(caller_frame.filename)
    date = dt.datetime.now()
    identifier = str(text)[0:2]
    if identifier == "%e":
        message = f"%e [{date.hour}.{date.minute}.{date.second}] {caller_file}: {text[2:len(text)]}" #Error
    elif identifier == "%i":
        message = f"%i [{date.hour}.{date.minute}.{date.second}] {caller_file}: {text[2:len(text)]}" #Important
    else:
        message = f"[{date.hour}.{date.minute}.{date.second}] {caller_file}: {text}"
    with open(f"{filePath}/latest.log", "a") as file:
        file.write(f"{message}\n")
        file.close
    with open(f"{filePath}/latest.log", "r") as file:
        output = file.readlines()
        file.close
    print(output[-2])
        
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
  
def removeOldLogs(filePath: str = "logs"):
    for i in os.listdir(filePath):
        if i != "latest.log":
            if logContainsError(f"{filePath}/{i}"):
                discardLog(f"{filePath}/{i}")
          
def logContainsError(filePath: str = "logs"):
    if filePath.split(".DS_Store")[0] == filePath:
        with open(filePath, "r") as file:
            output = file.read()
        return output.split("%e")[0] == output

def discardLog(filePath: str = "logs"):
    os.remove(filePath)

def prepareLogs(filePath: str = "logs"):
    cleanLatest(filePath)
    checkLatest(filePath)
    
def systemInfo():
    return f"%iSystem identified: {checkOs()}\n%i System identity: {returnOsName()}\n%i App version: {returnAppVersion()}\n%i Python version: {sys.version.split(' ')[0]}"

def passSelf(self):
    savedSelf = self