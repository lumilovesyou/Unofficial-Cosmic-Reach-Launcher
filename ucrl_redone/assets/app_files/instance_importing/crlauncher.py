import os
import json
import tempfile
import platform

def findInstances(path: str, namesOnly: bool = False):
    if platform.system() == "Darwin":
        crlInstances = []
        if path != None and path != "~/Library/":
            directory = os.listdir(path)
            for folder in directory:
                if os.path.exists(f"{path}/{folder}/instance.json"):
                    if namesOnly:
                        crlInstances.append(folder)
                    else:
                        crlInstances.append(f"{path}/{folder}")
            return(crlInstances)                  
    else:
        print("Other")
        
def findInstancesFolder():
    tmpdir = tempfile.gettempdir() #Gets the temp directory
    for root, dirs, files in os.walk(tmpdir): #Steps through looking for the folder
        if root.endswith("cosmic-reach/instances") or root.endswith("cosmic-reach/instances/"):
            return root
    return "~/Library/"

def importCrlInstances(self, path: str, instanceNames: list):
    instanceFiles = findInstances(path)
    instanceData = []
    for i in range(len(instanceFiles)):
        if instanceFiles[i].split("instances/")[1] in instanceNames:
            with open(f"{instanceFiles[i]}/instance.json", "r") as file:
                instanceFile = json.loads(file.read())
                instanceData.append({
                    "loader": instanceFile["modLoader"],
                    "version": instanceFile["cosmicVersion"],
                    "name": instanceFile["name"],
                    "icon": f"{instanceFiles[i].split("instances/")[0]}/icons/{instanceFile["iconFileName"]}",
                    "autoUpdate": instanceFile["autoUpdateToLatest"]
                })
                self.createInstance(instanceData[i]["loader"], instanceData[i]["version"], instanceData[i]["name"], instanceData[i]["icon"], instanceData[i]["autoUpdate"], f"{instanceFiles[i]}/cosmic-reach", True)
          
def importCrlInstance2(self, location):
    for root, dirs, files in os.walk(location):
        if "instance.json" in files:        
            instanceData = []
            with open(os.path.join(root, "instance.json"), "r") as file:
                instanceFile = json.loads(file.read())
                instanceData.append({
                    "loader": instanceFile["modLoader"],
                    "version": instanceFile["cosmicVersion"],
                    "name": instanceFile["name"],
                    "icon": f"{location.split("instances")[0]}/icons/{instanceFile["iconFileName"]}",
                    "autoUpdate": instanceFile["autoUpdateToLatest"]
                })
                self.createInstance(instanceData["loader"], instanceData["version"], instanceData["name"], instanceData["icon"], instanceData["autoUpdate"], f"{os.path.join(root, 'cosmic-reach')}", True)