import os
from .logs import log

def createFolder(location, overwrite=False):
    if not os.path.exists(location) or overwrite:
            os.makedirs(location)
            
def checkDirValidity(fileToCheck: str):
    if not os.path.exists("./" + fileToCheck + "/"):
        os.mkdir("./" + fileToCheck)
        log("Created " + fileToCheck)
    else:
        log(fileToCheck + " already exists!")

def checkForDir(fileToCheck: str):
    return os.path.exists(fileToCheck)