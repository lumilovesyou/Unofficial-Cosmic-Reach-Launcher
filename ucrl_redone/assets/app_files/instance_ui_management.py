import os
import json
from PySide6.QtWidgets import QWidget, QToolButton, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QMenu
from functools import partial
from . import flow_layout, file_management, instance_management, system
from .logs import log

def reloadInstances(self, homeLayout, runningInstances):
        log("Reloading instances!")
        #Updates instances displayed
        #Deletes current instance buttons
        if homeLayout is not None:
            while homeLayout.count() > 0:
                item = homeLayout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        #Defines button
        buttonWidget = QWidget()
        buttonLayout = flow_layout.FlowLayout(buttonWidget)
        #List read from
        list = []
        #The actual reading of instances
        instancesFolderPath = "instances"
        ##Checking if path exists
        file_management.checkDirValidity(instancesFolderPath)
        ##
        #Checks if the instances path exists and if it's a directory
        if os.path.exists(instancesFolderPath) and os.path.isdir(instancesFolderPath):
            #Loops for each file in that path
            for instancePath in os.listdir(instancesFolderPath):
                instancePath = os.path.join(instancesFolderPath, instancePath)
                #Checks if the instance is a folder and isn't macOS's DS_Store file
                if os.path.isdir(instancePath) and instancePath != ".DS_Store":
                    #Makes the instance a button
                    instanceButton = QToolButton()
                    aboutLocation = f"{instancePath}/about.json"
                    if file_management.checkForFile(aboutLocation):
                        with open(aboutLocation) as file:
                            openedFile = json.loads(file.read())
                            if "name" in openedFile:
                                instanceName = openedFile["name"]
                            else:
                                instanceName = instancePath.split("/")[1]
                    else:
                        instanceName = instancePath.split("/")[1]
                        
                    instanceButton.setText(instanceName)
                    #Sets the icon
                    iconPath = os.path.join(instancePath, "icon.png")
                    if os.path.isfile(iconPath):
                        icon = QIcon(iconPath)
                    else:
                        icon = QIcon("assets/app_icons/ucrl_icon.png")
                    instanceButton.setIcon(icon)
                    instanceButton.setFixedSize(QSize(100, 100))
                    instanceButton.setIconSize(QSize(48, 48))
                    instanceButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    instanceButton.setProperty("filepath", instancePath.split("/")[1])
                    #Checks if instance is running
                    instanceButton.setStyleSheet("border-radius: 10px;")
                    if instancePath in runningInstances:
                        instanceButton.setStyleSheet("background-color: #9043437d;")
                    
                    #Button clicked events
                    instanceButton.clicked.connect(partial(instance_management.launchInstance, self, instancePath.split("/")[1], instanceButton))
                    instanceButton.setContextMenuPolicy(Qt.CustomContextMenu)
                    instanceButton.customContextMenuRequested.connect(self.showInstanceContextMenu)
                    
                    # Add button to layout
                    buttonLayout.addWidget(instanceButton)
        homeLayout.addWidget(buttonWidget)
        #Adds "Add Instance" button
        addInstance = QPushButton("Add Instance")
        addInstance.clicked.connect(self.callAddInstance)
        homeLayout.addWidget(addInstance)
        #Adds "Edit Instances" button
        self.editInstancesButton = QPushButton("Edit Instances")
        self.editInstancesButton.clicked.connect(lambda: self.toggleEditingInstances(self.editInstancesButton))
        homeLayout.addWidget(self.editInstancesButton)

        homeLayout.addStretch()