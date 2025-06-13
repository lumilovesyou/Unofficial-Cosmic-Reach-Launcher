import os
import shutil
import platform
import tempfile
from PySide6.QtWidgets import QFileDialog, QCheckBox

def exportInstance(self, filePath: str):
    shutil.make_archive(f"{QFileDialog.getExistingDirectory(self, "Select Folder")}/filePath", "zip", f"{os.getcwd()}/instances/{filePath}")
    
def findInstances(path: str, namesOnly: bool = False):
    if platform.system() == "Darwin":
        crlInstances = []
        if path != None and os.path.exists(path):
            directory = os.listdir(path)
            for folder in directory:
                if os.path.exists(f"{path}/{folder}/about.json"):
                    if namesOnly:
                        crlInstances.append(folder)
                    else:
                        crlInstances.append(f"{path}/{folder}")
            return(crlInstances)  
        else:
            return([])                
    else:
        print("Other")
        
def exportInstances(self, exportPath: str):
    instanceNames = []
    for i in range(self.fileLayout.count()):
        item = self.fileLayout.itemAt(i).widget()
        if isinstance(item, QCheckBox):
            if item.isChecked():
                instanceNames.append(item.text())
    if len(instanceNames) > 0:
        tempDir = mkTempDir("/tmp/ucrl")
        if len(instanceNames) < 2:
            conflictFreePath = f"{exportPath}/{instanceNames[0]}"    
            i = (0, conflictFreePath)
            while os.path.exists(f"{conflictFreePath}.zip"):
                i = (i[0] + 1, i[1])
                conflictFreePath = f"{i[1]} ({i[0]})"
                
            shutil.make_archive(f"{tempDir}/copied", "zip", f"instances/{instanceNames[0]}") #Add custom export names and locations
            os.rename(f"{tempDir}/copied.zip", f"{conflictFreePath}.ucrl") #Untitled Cosmic Reach Launcher 
            rmTempDir(tempDir)
        else:
            conflictFreePath = conflictFreePath = f"{exportPath}/exportedInstances"
            i = (0, conflictFreePath)
            while os.path.exists(f"{conflictFreePath}.ucrla"):
                i = (i[0] + 1, i[1])
                conflictFreePath = f"{i[1]} ({i[0]})"
            for i in instanceNames:
                shutil.copytree(f"instances/{i}", f"{tempDir}/copied/{i}")
            shutil.make_archive(f"{tempDir}/copied", "zip", tempDir)
            os.rename(f"{tempDir}/copied.zip", f"{conflictFreePath}.ucrla") #Untitled Cosmic Reach Launcher Archive
            rmTempDir(tempDir)
        self.importInstance.close()
            
def mkTempDir(tempDir):
    if os.path.exists(tempDir):
        rmTempDir(tempDir)
    os.mkdir(tempDir)
    return tempDir

def rmTempDir(tempDir):
    shutil.rmtree(tempDir)