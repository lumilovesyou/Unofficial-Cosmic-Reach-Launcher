import os
import json
import subprocess
import random as ran
from . import instance_management, file_management, app_info_and_update, web_interaction, system
from .logs import log, prepareLogs
from PySide6.QtWidgets import QMainWindow, QGridLayout, QLabel, QLineEdit, QComboBox, QPushButton, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

def checkForVersion(version):
    file = f"meta/versions/{version}/about.json"
    log(file)
    log(os.path.exists(file))
    try:
        with open(file, "r") as f:
            file_loaded = json.load(f)
        if file_loaded.get("version") == version:
            return True
        else:
            return f"Couldn't locate correct version in {file}"
    except:
        return f"Couldn't locate file {file}"
    
def loadEnvironmentVars(file_path):
    with open(file_path, "r") as file:
            env_vars = json.loads(file.read())
    env = os.environ.copy()
    env.update(env_vars["keys"])
    return env

def runVersion (version, keys, type, instance_ID):
    json_file = f"meta/versions/{version}/about.json"
    jar_file = f"meta/versions/{version}/Cosmic-Reach-{version}.jar"
    
    env = loadEnvironmentVars(json_file)
    
    process = subprocess.Popen(
        ["java", "-jar", str(jar_file)],
        env=env
    )
    
    log(f"Subprocess started with PID {process.pid}")
    return(process.pid)

#Higher-level functions
def launchInstance(self, instancePath, senderButton):
        log(f"Instance path: {instancePath}")
        #Gets the button that called
        #Handles the instance launch
        prepareLogs(f"instances/{instancePath}/logs")
        log(f"Launching instance: {instancePath}", f"instances/{instancePath}/logs")
        filePath = "instances/" + instancePath + "/about.json"
        if os.path.exists(filePath):
        #Checks if file exists
            if not instancePath in self.runningInstances:
                with open(filePath, "r") as file:
                    instanceVersion = json.loads(file.read())
                    file.close()
                instanceVersion = instanceVersion["version"]
                log(instanceVersion)
                check = instance_management.checkForVersion(instanceVersion)
                if check == True:
                    senderButton.setStyleSheet("border-radius: 10px; background-color: #9043437d;")
                    log("Can run version!")
                    PID = instance_management.runVersion(str(instanceVersion), "placeholder", "placeholder", "placeholder")
                    self.runningInstances.append(instancePath)
                else:
                    app_info_and_update.installVersion(instanceVersion)
                    system.openErrorWindow(f"Failed to load instance! Version {instanceVersion} was missing and is now being installed.")
            else:
                log(f"Already running {instancePath}")
                 
def addInstance(self):
    #Checking if instance folder exists
    file_management.checkDirValidity("/instances")

    #Defining Window
    self.newInstance = QMainWindow()
    self.newInstance.setWindowTitle("New Instance")
    self.newInstance.setMinimumSize(530, 300)
    self.newInstance.setMaximumSize(530, 300)
    layout = QGridLayout()
    layout.setAlignment(Qt.AlignTop)

    #Defining Icon
    self.iconLabel = QLabel(self.newInstance)
    pixmap = QPixmap("assets/app_icons/ucrl_icon.png")
    scaledPixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    self.iconLabel.setPixmap(scaledPixmap)
    self.iconLabel.setAlignment(Qt.AlignCenter)
    layout.addWidget(self.iconLabel, 0, 0, 1, 1)

    #Defining LineEdits
    self.instanceName = QLineEdit(self.newInstance)
    instanceName = "New Instance"
    i = 0
    while True:
        i += 1
        if file_management.checkForDir(f"instances/{instanceName}"):
            instanceName = f"New Instance ({i})"
        else:
            break
    self.instanceName.setText(instanceName)
    self.instanceName.setMinimumWidth(360)
    layout.addWidget(self.instanceName, 0, 1, 1, 3)
    
    self.iconPathEdit = QLineEdit(self.newInstance)
    self.iconPathEdit.setText("assets/app_icons/ucrl_icon.png")
    self.iconPathEdit.setMinimumWidth(365)
    layout.addWidget(self.iconPathEdit, 1, 0, 1, 2)

    #Defining QComboBox
    self.loader = QComboBox()
    self.loader.addItems(["Vanilla"])
    layout.addWidget(self.loader, 2, 0, 1, 1)
    
    #Define the version selection menu's options
    fill = []
    """
    versionsInfoFile = json.loads(github_interaction.getFile("CRModders", "CosmicArchive", "versions.json"))
    for version in versionsInfoFile["versions"]:
        fill.append(version["id"])
    """
    #app_info_and_update.downloadAndProcessVersions()
    with open("meta/version.json", "r") as file:
        for version in json.loads(file.read())["versions"]:
            fill.append(version)
        
    
    #Define the QComboBox for the version selection menu
    self.version = QComboBox()
    self.version.addItems(fill)
    layout.addWidget(self.version, 2, 1, 1, 3)

    #Defining PushButton
    self.selectIconButton = QPushButton("Select Icon", self.newInstance)
    self.selectIconButton.clicked.connect(self.selectIcon)
    layout.addWidget(self.selectIconButton, 1, 3, 1, 1)
    
    self.finalizeInstanceButton = QPushButton("Create Instance")
    self.finalizeInstanceButton.clicked.connect(lambda: self.createInstance( self.loader.currentText(), self.version.currentText(), self.instanceName.text(), self.iconPathEdit.text()))
    layout.addWidget(self.finalizeInstanceButton, 3, 1, 1, 2)

    #Setting Layout
    centralWidget = QWidget()
    centralWidget.setLayout(layout)
    self.newInstance.setCentralWidget(centralWidget)
    centralWidget.setContentsMargins(10, 10, 10, 10)
    self.newInstance.show()