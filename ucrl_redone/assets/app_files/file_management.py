import os

def createFolder(location, overwrite=False):
    if not os.path.exists(location) or overwrite:
            os.makedirs(location)
            
def checkDirValidity(file_to_check):
    if not os.path.exists("./" + file_to_check + "/"):
        os.mkdir("./" + file_to_check)
        print("Created " + file_to_check)
    else:
        print(file_to_check + " already exists!")