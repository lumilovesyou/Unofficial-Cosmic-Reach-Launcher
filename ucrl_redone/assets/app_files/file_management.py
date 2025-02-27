import os

def createFolder(location, overwrite=False):
    if not os.path.exists(location) or overwrite:
            os.makedirs(location)
            
def checkDirValidity(fileToCheck: str):
    if not os.path.exists("./" + fileToCheck + "/"):
        os.mkdir("./" + fileToCheck)

def checkForDir(fileToCheck: str):
    return os.path.exists(fileToCheck)

def checkForFile(fileToCheck: str):
    return os.path.isfile(fileToCheck)