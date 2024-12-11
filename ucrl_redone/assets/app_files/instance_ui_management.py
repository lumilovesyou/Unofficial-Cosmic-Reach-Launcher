import os
from PySide6.QtWidgets import QWidget, QToolButton, QPushButton
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QMenu
from functools import partial
from . import flow_layout, file_management, instance_management

def reloadInstances(self, homeLayout, runningInstances):
        print("Reloading instances!")
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
        instancesPath = "instances"
        ##Checking if path exists
        file_management.checkDirValidity(instancesPath)
        ##
        #Checks if the instances path exists and if it's a directory
        if os.path.exists(instancesPath) and os.path.isdir(instancesPath):
            #Loops for each file in that path
            for instanceName in os.listdir(instancesPath):
                instancePath = os.path.join(instancesPath, instanceName)
                #Checks if the instance is a folder and isn't macOS's DS_Store file
                if os.path.isdir(instancePath) and instancePath != ".DS_Store":
                    #Makes the instance a button
                    instanceButton = QToolButton()
                    instanceButton.setText(instanceName)
                    #Sets the icon
                    iconPath = os.path.join(instancePath, "icon.png")
                    print(str(os.path.isfile(iconPath)) + " - " + instancePath)
                    if os.path.isfile(iconPath):
                        icon = QIcon(iconPath)
                    else:
                        icon = QIcon("assets/app_icons/ucrl_icon.png")
                    instanceButton.setIcon(icon)
                    instanceButton.setFixedSize(QSize(100, 100))
                    instanceButton.setIconSize(QSize(48, 48))
                    instanceButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                    #Checks if instance is running
                    instanceButton.setStyleSheet("border-radius: 10px;")
                    if instanceName in runningInstances:
                        instanceButton.setStyleSheet("background-color: #9043437d;")
                    
                    #Button clicked events
                    instanceButton.clicked.connect(partial(instance_management.launchInstance, self, instanceName, instanceButton))
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
        editInstances = QPushButton("Edit Instances")
        editInstances.clicked.connect(self.editInstances)
        homeLayout.addWidget(editInstances)

        homeLayout.addStretch()