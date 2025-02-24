import os
import json
import subprocess
import random as ran
from . import instance_management, file_management
from .logs import log
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
            env_vars = json.load(file)
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
def launchInstance(self, instanceName, senderButton):
        #Gets the button that called
        #Handles the instance launch
        log(f"Launching instance: {instanceName}", f"instances/{instanceName}/logs")
        filePath = "instances/" + instanceName + "/about.json"
        if os.path.exists(filePath):
        #Checks if file exists
            if not instanceName in self.runningInstances:
                instanceVersion = json.load(open(filePath, "r"))
                log(instanceVersion["version"])
                check = instance_management.checkForVersion(instanceVersion["version"])
                if check == True:
                    senderButton.setStyleSheet("border-radius: 10px; background-color: #9043437d;")
                    log("Can run version!")
                    PID = instance_management.runVersion(str(instanceVersion["version"]), "placeholder", "placeholder", "placeholder")
                    self.runningInstances.append(instanceName)
                else:
                    log(check)
            else:
                log(f"Already running {instanceName}")
                 
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
    for i in range(1, 100):
        if file_management.checkForDir(f"instances/{instanceName}"):
            instanceName = f"New Instance ({i})"
        elif i == 100:
            instanceName = ran.randint(1, 10000000)
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
    self.loader.addItems(["Vanilla", "Quilt", "Fabric", "Puzzle"])
    layout.addWidget(self.loader, 2, 0, 1, 1)
    
    fill = ["0.1.46"]
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