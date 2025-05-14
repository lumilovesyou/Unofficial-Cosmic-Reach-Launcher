import os
import json
import signal
import psutil
import threading
import subprocess
import random as ran
from . import instance_management, file_management, app_info_and_update, web_interaction, system, config
from .instance_importing import crlauncher
from .logs import log, prepareLogs
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices

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
    
def openInstanceFolder(instancePath):
    file_url = QUrl.fromLocalFile(f"{os.getcwd()}/instances/{instancePath}")
    QDesktopServices.openUrl(file_url)
    log(f"Opening instance folder {os.getcwd()}/instances/{instancePath}")
    
def loadEnvironmentVars(file_path):
    with open(file_path, "r") as file:
            env_vars = json.loads(file.read())
    env = os.environ.copy()
    env.update(env_vars["keys"])
    return env

def runVersion(version, keys, type, instancePath):
    json_file = f"meta/versions/{version}/about.json"
    jar_file = f"meta/versions/{version}/Cosmic-Reach-{version}.jar"
    
    env = loadEnvironmentVars(json_file)
    
    file_management.checkDirValidity(f"instances/{instancePath}/files/")
    xStartMode = config.checkInConfig("App Settings", "xStart")
    if (system.returnOsName() == "Darwin" and xStartMode == "Auto") or xStartMode == "Enabled":
        process = subprocess.Popen( #I also noticed that you can no longer stop the process by clicking on the instance icon
            ["java", "-XstartOnFirstThread", "-jar", str(jar_file), "--save-location", f"instances/{instancePath}/files/"], #Doesn't work on Windows or Linux because of -XstartOnFirstThread, so I'll add a toggle in the future to fix this
            env=env,
            preexec_fn=os.setsid
        )
    else:
        process = subprocess.Popen(
            ["java", "-jar", str(jar_file), "--save-location", f"instances/{instancePath}/files/"],
            env=env,
            preexec_fn=os.setsid
        )
    
    log(f"Subprocess started with PID {process.pid}")
    return(process)

def endProcess(self, instancePath, senderButton):
    process = self.runningInstancesProcess[instancePath]
    process = psutil.Process(process.pid)
    processChildren = process.children(True) #Gets the children process to properly kill
    for process in processChildren:
        process.send_signal(signal.SIGTERM)
    process.send_signal(signal.SIGTERM)
    senderButton.setStyleSheet("border-radius: 10px;")
    
    log(f"Subprocess terminated with PID {process.pid}")

#Higher-level functions
def launchInstance(self, instancePath, senderButton):
    if self.editingInstances:
        editInstance(self, instancePath)
    else:
        log(f"Instance path: {instancePath}")
        filePath = "instances/" + instancePath + "/about.json"
        if os.path.exists(filePath):
        #Checks if file exists
            if not instancePath in self.runningInstances:
                with open(filePath, "r") as file:
                    instanceInfo = json.loads(file.read())
                    file.close()
                filePath = f"instances/{filePath.split("/")[1]}"
                instanceVersion = instanceInfo["version"]
                instanceUpdatePreference = instanceInfo["autoUpdate"] if "autoUpdate" in instanceInfo else False
                if instanceUpdatePreference:
                    with open("meta/version.json", "r") as file:
                        latestVersion = json.loads(file.read())["absLatestVersion"]
                        file.close()
                    if instanceVersion != latestVersion:
                        log(f"Updating {instancePath}")
                        with open(f"{filePath}/about.json", "r") as file:
                            fileLoaded = json.loads(file.read())
                            file.close()
                        with open(f"{filePath}/about.json", "w") as file:
                            fileLoaded["version"] = latestVersion
                            file.write(json.dumps(fileLoaded))
                            file.close()
                        instanceVersion = latestVersion
                        if not app_info_and_update.hasVersionInstalled(latestVersion):
                            app_info_and_update.installVersion(latestVersion)
                    
                log(f"Instance {instancePath}'s version is {instanceVersion}")
                check = checkForVersion(instanceVersion)
                if check == True:
                    senderButton.setStyleSheet("border-radius: 10px; background-color: #9043437d;")
                    log("Can run version!")
                    openedProcess = runVersion(str(instanceVersion), "placeholder", "placeholder", instancePath)
                    self.runningInstances.append(instancePath)
                    self.runningInstancesProcess[instancePath] = openedProcess
                    threading.Thread(target=onSubprocessExit, args=(self, senderButton,self.runningInstancesProcess[instancePath],instancePath,), daemon=True).start()
                else:
                    system.openErrorWindow(f"Failed to load instance! Version {instanceVersion} was missing and is now being installed.")
                    app_info_and_update.installVersion(instanceVersion)
            else:
                log(f"Already running {instancePath}")
                endProcess(self, instancePath, senderButton)
                
def onSubprocessExit(self, senderButton, process, instancePath):
    process.wait()
    senderButton.setStyleSheet("border-radius: 10px;")
    self.runningInstancesProcess.pop(instancePath)
    self.runningInstances.remove(instancePath)
                 
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
    latestVersion = web_interaction.getFile("CRModders", "CosmicArchive", "latest_version.txt")
    if latestVersion:
        latestVersion = latestVersion.split(" ")[0]
    
    #app_info_and_update.downloadAndProcessVersions()
    with open("meta/version.json", "r") as file:
        file = json.loads(file.read())["versions"]
        
        if not latestVersion in file:
            app_info_and_update.downloadAndProcessVersions()
        
        for version in file:
            fill.append(version)
        
    
    #Define the QComboBox for the version selection menu
    self.version = QComboBox()
    self.version.addItems(fill)
    layout.addWidget(self.version, 2, 1, 1, 3)

    #Defining QCheckBox
    self.autoUpdateBox = QCheckBox("Auto Update Instance")
    layout.addWidget(self.autoUpdateBox, 3, 1, 1, 2)

    #Defining PushButton
    self.selectIconButton = QPushButton("Select Icon", self.newInstance)
    self.selectIconButton.clicked.connect(self.selectIcon)
    layout.addWidget(self.selectIconButton, 1, 3, 1, 1)
    
    self.finaliseInstanceButton = QPushButton("Create Instance")
    self.finaliseInstanceButton.clicked.connect(lambda: self.createInstance(self.loader.currentText(), self.version.currentText(), self.instanceName.text(), self.iconPathEdit.text(), self.autoUpdateBox.isChecked()))
    layout.addWidget(self.finaliseInstanceButton, 4, 1, 1, 2)

    #Setting Layout
    centralWidget = QWidget()
    centralWidget.setLayout(layout)
    self.newInstance.setCentralWidget(centralWidget)
    centralWidget.setContentsMargins(10, 10, 10, 10)
    self.newInstance.show()
    
def importInstance(self):
    #Checking if instance folder exists
    file_management.checkDirValidity("/instances")

    #Defining Window
    self.importInstance = QMainWindow()
    self.importInstance.setWindowTitle("Import Instances")
    self.importInstance.setMinimumSize(530, 300)
    self.importInstance.setMaximumSize(530, 300)
    
    #Layout
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignTop)
    
    #Tabs
    self.importInstanceTabs = QTabWidget(self)
    self.importInstanceFromFile = QScrollArea()
    self.importInstanceTESCRL = QScrollArea() #TheEntropyShard Cosmic Reach Launcher
    self.importInstanceTESCRL.setWidgetResizable(True)
    
    ##CRLauncher Tab Layout
    contentWidget = QWidget()
    self.tescrlLayout = QVBoxLayout(contentWidget)
    instancesFolder = crlauncher.findInstancesFolder()
    
    self.filePath = QLineEdit("Placeholder Path")
    self.filePath.setText(instancesFolder)
    self.filePath.textChanged.connect(self.updateCrlCheckboxes)
    
    filePathSelect = QPushButton("Select Path")
    filePathSelect.clicked.connect(self.selectPath)
    
    self.tescrlLayout.addWidget(self.filePath)
    self.tescrlLayout.addWidget(filePathSelect)
    
    self.importInstanceTESCRL.setWidget(contentWidget)
    
    updateCrlCheckboxes(self, instancesFolder)
    self.tescrlLayout.addStretch()
    ##
    
    #Add tabs to window
    self.importInstanceTabs.addTab(self.importInstanceFromFile, "From File")
    self.importInstanceTabs.addTab(self.importInstanceTESCRL, "Cosmic Reach Launcher")
    layout.addWidget(self.importInstanceTabs)
    
    #Import button
    self.finaliseInstanceButton = QPushButton("Import Selected")
    self.finaliseInstanceButton.setDisabled(True)
    self.finaliseInstanceButton.clicked.connect(self.importInstances)
    layout.addWidget(self.finaliseInstanceButton)

    #Setting Layout
    centralWidget = QWidget()
    centralWidget.setLayout(layout)
    self.importInstance.setCentralWidget(centralWidget)
    self.importInstance.show()
    
def updateCrlCheckboxes(self, path):
        for i in reversed(range(self.tescrlLayout.count())):
            item = self.tescrlLayout.itemAt(i)

            if item.widget() and isinstance(item.widget(), (QCheckBox, QLabel)):
                checkbox = item.widget()
                self.tescrlLayout.removeWidget(checkbox)
                checkbox.deleteLater()

            elif item.spacerItem():
                self.tescrlLayout.removeItem(item)
                
        if os.path.isdir(path):
            crlauncherInstances = crlauncher.findInstances(path, True)
            crlauncherInstances = [] if crlauncherInstances == None else crlauncherInstances
            if len(crlauncherInstances) < 1:
                self.tescrlEmpty = QLabel("No Instances Found")
                self.tescrlLayout.insertWidget(self.tescrlLayout.count(), self.tescrlEmpty)
            else:
                for i in range(len(crlauncherInstances)):
                    checkBox = QCheckBox(crlauncherInstances[i])
                    checkBox.clicked.connect(self.importCheckBoxClicked)
                    self.tescrlLayout.insertWidget(self.tescrlLayout.count(), checkBox)
        else:
            self.tescrlEmpty = QLabel("No Instances Found")
            self.tescrlLayout.insertWidget(self.tescrlLayout.count(), self.tescrlEmpty)
    
def editInstance(self, instancePath):
    #Checking if instance's folder exists
    instancePath = f"instances/{instancePath}"
    if not file_management.checkForDir(instancePath):
        return

    #Get the name of the instance
    aboutLocation = f"{instancePath}/about.json"
    if file_management.checkForFile(aboutLocation):
        with open(aboutLocation) as file:
            openedFile = json.loads(file.read())
            instanceName = openedFile["name"] if "name" in openedFile else instancePath.split("/")[1]
            instanceVersion = openedFile["version"] if "version" in openedFile else "Null"
            autoUpdate = openedFile["autoUpdate"] if "autoUpdate" in openedFile else False
    else:
        instanceName = instancePath.split("/")[1]

    #Defining Window
    self.editedInstance = QMainWindow()
    self.editedInstance.setWindowTitle(f"Edit Instance - {instanceName}")
    self.editedInstance.setMinimumSize(530, 300)
    self.editedInstance.setMaximumSize(530, 300)
    layout = QGridLayout()
    layout.setAlignment(Qt.AlignTop)

    #Defining Icon
    iconPath = os.path.join(instancePath, "icon.png")
    if os.path.isfile(iconPath):
        icon = iconPath
    else:
        icon = "assets/app_icons/ucrl_icon.png"

    self.iconLabel = QLabel(self.editedInstance)
    pixmap = QPixmap(icon)
    scaledPixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    self.iconLabel.setPixmap(scaledPixmap)
    self.iconLabel.setAlignment(Qt.AlignCenter)
    layout.addWidget(self.iconLabel, 0, 0, 1, 1)

    #Defining LineEdits
    self.instanceName = QLineEdit(self.editedInstance)
    self.instanceName.setText(instanceName)
    self.instanceName.setMinimumWidth(360)
    layout.addWidget(self.instanceName, 0, 1, 1, 3)
    
    self.iconPathEdit = QLineEdit(self.editedInstance)
    self.iconPathEdit.setText(icon)
    self.iconPathEdit.setMinimumWidth(365)
    layout.addWidget(self.iconPathEdit, 1, 0, 1, 2)

    #Defining QComboBox
    self.loader = QComboBox()
    self.loader.addItems(["Vanilla"])
    layout.addWidget(self.loader, 2, 0, 1, 1)
    
    #Define the version selection menu's options
    fill = []
    latestVersion = web_interaction.getFile("CRModders", "CosmicArchive", "latest_version.txt")
    if latestVersion:
        print(latestVersion)
        latestVersion = latestVersion.split(" ")[0]
    
    #app_info_and_update.downloadAndProcessVersions()
    with open("meta/version.json", "r") as file:
        file = json.loads(file.read())["versions"]
        
        if not latestVersion in file:
            app_info_and_update.downloadAndProcessVersions()
        
        for version in file:
            fill.append(version)
        
    
    #Define the QComboBox for the version selection menu
    self.version = QComboBox()
    self.version.addItems(fill)
    index = self.version.findText(instanceVersion, Qt.MatchFlag.MatchFixedString)
    if index >= 0:
        self.version.setCurrentIndex(index)
    layout.addWidget(self.version, 2, 1, 1, 3)

    #Defining QCheckBox
    self.autoUpdateBox = QCheckBox("Auto Update Instance")
    self.autoUpdateBox.setChecked(autoUpdate)
    layout.addWidget(self.autoUpdateBox, 3, 1, 1, 2)

    #Defining PushButton
    self.selectIconButton = QPushButton("Select Icon", self.editedInstance)
    self.selectIconButton.clicked.connect(self.selectIcon)
    layout.addWidget(self.selectIconButton, 1, 3, 1, 1)
    
    self.finaliseInstanceButton = QPushButton("Delete Instance")
    self.finaliseInstanceButton.setStyleSheet("background-color: red; color: white;")
    self.finaliseInstanceButton.clicked.connect(lambda: self.deleteInstance(instancePath))
    layout.addWidget(self.finaliseInstanceButton, 4, 0, 1, 2)
    
    self.finaliseInstanceButton = QPushButton("Save Instance")
    self.finaliseInstanceButton.clicked.connect(lambda: self.saveEditedInstance(self.loader.currentText(), self.version.currentText(), self.instanceName.text(), instancePath, iconPath, self.iconPathEdit.text(), self.autoUpdateBox.isChecked()))
    layout.addWidget(self.finaliseInstanceButton, 4, 2, 1, 2)

    #Setting Layout
    centralWidget = QWidget()
    centralWidget.setLayout(layout)
    self.editedInstance.setCentralWidget(centralWidget)
    centralWidget.setContentsMargins(10, 10, 10, 10)
    self.editedInstance.show()