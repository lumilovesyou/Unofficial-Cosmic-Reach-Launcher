from github import Github

g = Github()

def getLatestRelease(repoOwner: str, repoName: str):
    repo = g.get_repo(f"{repoOwner}/{repoName}")
    return repo.get_latest_release()

def getFile(repoOwner: str, repoName: str, fileName: str):
    repo = g.get_repo(f"{repoOwner}/{repoName}")
    file = repo.get_contents(fileName)
    return file.decoded_content.decode()