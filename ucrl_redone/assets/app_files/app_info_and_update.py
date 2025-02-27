import json
from . import github_interaction

def returnAppVersion():
    return "0.0.0" #This can be used in the future for updating the application so only this needs to be set to change the version

def downloadAndProcessVersions():
    versionsInfoFile = json.loads(github_interaction.getFile("CRModders", "CosmicArchive", "versions.json"))
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
                print(e)
                print(i)
                print(version["id"])
        
        writeToFile["versions"] = (listOfVersions)
        writeToFile["links"] = (listOfVersionsAndLink)
        writeToFile["latestVersion"] = versionsInfoFile["latest"]["pre_alpha"]
        json.dump(writeToFile, file)
        file.close()