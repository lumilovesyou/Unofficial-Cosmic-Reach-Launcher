def newestVersion(*args):
    compare = []
    for version in args:
        compare.append(version.split("."))
    newestVersion = compare[-1]
    for count in range(len(compare) - 1):
        for i in range(len(compare[count])):
            compare1 = compare[count][i] if i < len(compare[count]) else "0"
            compare2 = newestVersion[i] if i < len(newestVersion) else "0"
            if compare1 < compare2:
                break
            elif compare1 > compare2:
                newestVersion = compare[count]
                break
    return ".".join(newestVersion)

def oldestVersion(*args):
    compare = []
    for version in args:
        compare.append(version.split("."))
    oldestVersion = compare[-1]
    for count in range(len(compare) - 1):
        for i in range(len(compare[count])):
            compare1 = compare[count][i] if i < len(compare[count]) else "0"
            compare2 = oldestVersion[i] if i < len(oldestVersion) else "0"
            if compare1 > compare2:
                break
            elif compare1 < compare2:
                oldestVersion = compare[count]
                break
    return ".".join(oldestVersion)