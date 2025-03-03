from github import Github
import requests
#from .logs import log //Stupid circular imports. I'll need to find a way around this in the future.
from .system import openErrorWindow

g = Github()

def checkConnection(ip: str = "8.8.8.8"):
    try:
        response = requests.get(f"https://{ip}", timeout=5)
        if response.status_code == 200:
            return True
        else:
            return checkConnectionBackup()
    except requests.RequestException:
        return checkConnectionBackup()

def checkConnectionBackup(ip: str = "github.com"): #20.175.192.147 didn't work for some reason
    try:
        response = requests.get(f"https://{ip}", timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False

def getLatestRelease(repoOwner: str, repoName: str):
    repo = g.get_repo(f"{repoOwner}/{repoName}")
    return repo.get_latest_release()

def getFile(repoOwner: str, repoName: str, fileName: str):
    try:
        repo = g.get_repo(f"{repoOwner}/{repoName}")
        file = repo.get_contents(fileName)
        return file.decoded_content.decode()
    except Exception as e:
        #log(f"Failed to connect to GitHub: {e}")
        openErrorWindow(str(e), "Error")
        return

def getFileUrl(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        openErrorWindow(str(response.status_code), "Error")