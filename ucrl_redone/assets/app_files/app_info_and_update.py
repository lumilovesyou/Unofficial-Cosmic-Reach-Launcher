import os
import json
from . import file_management, web_interaction, system

def returnAppVersion():
    return "0.0.0" #This can be used in the future for updating the application so only this needs to be set to change the version

def downloadAndProcessVersions():
    if web_interaction.checkConnection():
        versionsInfoFile = web_interaction.getFile("CRModders", "CosmicArchive", "versions.json")
        if versionsInfoFile:
            versionsInfoFile = json.loads(versionsInfoFile)
            writeToFile = {}
            with open("meta/version.json", "w") as file:
                listOfVersions = []
                for version in versionsInfoFile["versions"]:
                    listOfVersions.append(version["id"])
                    
                listOfVersionsAndLink = {}
                i = 0
                for version in versionsInfoFile["versions"]:
                    i += 1
                    try:
                        listOfVersionsAndLink[version["id"]] = (version["client"]["url"])
                    except Exception as e:
                        print("")
                
                writeToFile["versions"] = (listOfVersions)
                writeToFile["links"] = (listOfVersionsAndLink)
                writeToFile["latestVersion"] = versionsInfoFile["latest"]
                print(versionsInfoFile["latest"].keys())
                json.dump(writeToFile, file)
                file.close()
    else:
        system.openErrorWindow(f"Couldn't download versions to process: Not connected!", "Error")
        
def hasVersionInstalled(version: str):
    if not file_management.checkForFile("meta/versions/installed.json"):
        checkInstalledVersions()
    with open("meta/versions/installed.json", "r") as file:
        file = json.loads(file.read())
        return version in file["installedVersions"]
    
def installVersion(version: str, source: str = "vanilla"):
    if web_interaction.checkConnection():
        with open("meta/version.json", "r") as file:
            file = json.loads(file.read())
            file = file["links"]
            if version in file:
                versionLink = file[version]
            else:
                return
        fileContent = web_interaction.getFileUrl(versionLink)
        file_management.checkDirValidity(f"meta/versions/{version}")
        with open(f"meta/versions/{version}/Cosmic-Reach-{version}.jar", "wb") as file:
            file.write(fileContent)
            file.close()
        with open(f"meta/versions/{version}/about.json", "w") as file:
            file.write(f'{{"version": "{version}", "type": "vanilla", "file": "Cosmic-Reach-{version}", "keys": {{}}}}')
        checkInstalledVersions()
    else:
        system.openErrorWindow(f"Couldn't install version {version}: Not connected!", "Error")

def checkInstalledVersions():
    file_management.checkDirValidity("meta/versions")
    fileToWrite = json.loads('{"installedVersions": []}')
    for dir in os.listdir("meta/versions"):
            dir = f"meta/versions/{dir}"
            if os.path.isdir(dir) and file_management.checkForFile(f"{dir}/about.json"):
                with open(f"{dir}/about.json", "r") as file:
                    aboutFile = json.loads(file.read())
                    file.close()
                if "version" in aboutFile:
                    fileToWrite["installedVersions"].append(aboutFile["version"])
    with open("meta/versions/installed.json", "w") as file:
        file.write(json.dumps(fileToWrite))