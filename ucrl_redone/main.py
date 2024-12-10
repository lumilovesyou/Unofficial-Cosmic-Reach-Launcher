import os
import sys
import json
import random as ran
import subprocess # Needed for future use with launching the .jar files
import configparser
import darkdetect
import qdarktheme
from functools import partial
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QSize, Qt, QRect, QPoint
from PySide6.QtWidgets import *
import crl_import as crl

runningInstances = []

def updateTheme():
#Updates theme to user's preference
    crl.checkForConfig()
    currentAppTheme = crl.checkInConfig("App Settings", "app_theme")
    if currentAppTheme == "Auto":
        if darkdetect.isDark():
            qdarktheme.setup_theme()
        else:
            qdarktheme.setup_theme("light")
    elif currentAppTheme == "Dark":
        qdarktheme.setup_theme(currentAppTheme.lower())
    else:
        qdarktheme.setup_theme("light")

def developerModeWidgets(visibility, self):
#Toggles visibility for dev buttons
            if not visibility or visibility == "False":
                self.relistButton.hide()
            else:
                self.relistButton.show()

#Defining FlowLayout
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.itemList = []
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
    
    def addItem(self, item):
        self.itemList.append(item)
    
    def count(self):
        return len(self.itemList)
    
    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size
    
    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        
        for item in self.itemList:
            widget = item.widget()
            spaceX = self.spacing() + widget.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
            spaceY = self.spacing() + widget.style().layoutSpacing(QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)
            
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y += lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        
        return y + lineHeight - rect.y()

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        ###Creating Tabs
        #Define Tabs
        self.tabs = QTabWidget(self)
        self.homeTab = QScrollArea()
        self.settingsTab = QScrollArea()
        # Set QScrollArea to be resizable
        self.homeTab.setWidgetResizable(True)
        self.settingsTab.setWidgetResizable(True)
        #Add tabs to window
        self.tabs.addTab(self.homeTab, "Home")
        self.tabs.addTab(self.settingsTab, "Settings")
        
        ###Modify & Defining tabs' layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.homeLayout = QtWidgets.QHBoxLayout(self.homeTab)
        settingsLayout = QtWidgets.QVBoxLayout(self.settingsTab)
        self.homeTab.setLayout(self.homeLayout)
        self.settingsTab.setLayout(settingsLayout)
        #Create content widgets
        homeContent = QWidget()
        settingsContent = QWidget()
        #Set layout for content widgets
        self.homeLayout = QtWidgets.QVBoxLayout(homeContent)
        settingsLayout = QtWidgets.QVBoxLayout(settingsContent)
        #Add content widgets to scroll areas
        self.homeTab.setWidget(homeContent)
        self.settingsTab.setWidget(settingsContent)
        
        ###Defining Setting's Widgets
        #Labels
        self.themeLabel = QLabel(self.settingsTab)
        self.themeLabel.setText("<div style ='font-size: 18px;'><b>Application Theme</b></div>")
        self.updateLabel = QLabel(self.settingsTab)
        self.updateLabel.setText("<div style ='font-size: 18px;'><b>Update</b></div>")
        self.infoLabel = QLabel(self.settingsTab)
        self.infoLabel.setText("<div style ='font-size: 18px;'><b>Info</b></div>")
        self.versionLabel = QLabel(self.settingsTab)
        self.versionLabel.setText("<div style ='font-size: 13px;'>UCRL 0.0.6</div>")
        self.authorsLabel = QLabel(self.settingsTab)
        self.authorsLabel.setText("<div style ='font-size: 13px;'>By <a href='https://github.com/ieatsoulsmeow'>IEatSoulsMeow</a> and <a href='https://github.com/felisaraneae'>FelisAraneae</a>")
        self.authorsLabel.setOpenExternalLinks(True)
        self.githubLabel = QLabel(self.settingsTab)
        self.githubLabel.setText("<div style ='font-size: 13px;'>Source can be found on <a href='https://github.com/FelisAraneae/Unofficial-Cosmic-Reach-Launcher'>Github</a>")
        self.githubLabel.setOpenExternalLinks(True)
        self.discordLabel = QLabel(self.settingsTab)
        self.discordLabel.setText("<div style ='font-size: 13px;'>Join the unofficial <a href='https://discord.gg/jRs9q7FMSu'>Discord</a> for other Cosmic Reach launchers")
        self.discordLabel.setOpenExternalLinks(True)
        self.developerLabel = QLabel(self.settingsTab)
        self.developerLabel.setText("<div style ='font-size: 18px;'><b>Developer Settings</b></div>")
        #QComboBox
        self.themeDropdown = QComboBox()
        dropdownFill = ["Dark", "Light", "Auto"]
        self.themeDropdown.addItems(dropdownFill)
        self.themeDropdown.currentIndexChanged.connect(self.updateThemeComboBox)
        self.themeDropdown.setCurrentIndex((dropdownFill).index(crl.checkInConfig("App Settings", "app_theme")))
        #Buttons
        self.updateButton = QPushButton("Update Application")
        self.updateButton.setIcon(QIcon("assets/button_icons/update_darkmode.svg"))
        self.updateButton.clicked.connect(self.magic)
        #Buttons
        self.relistButton = QPushButton("Reload Instances")
        self.relistButton.clicked.connect(lambda: self.reloadInstances(self, self.homeLayout))
        #Toggle
        self.developerToggle = QPushButton("Developer Mode: ", self)
        self.developerToggle.setCheckable(True)
        self.developerToggle.setChecked(True)
        self.developerToggle.clicked.connect(self.toggleDeveloper)
        if crl.checkInConfig("App Settings", "dev_mode") == "True":
            self.developerToggle.setText("Developer Mode: Enabled")
            self.developerToggle.setStyleSheet("QPushButton {background-color:#43904b; color:#dfdfdf}")
        else:
            self.developerToggle.setChecked(False)
            self.developerToggle.setText("Developer Mode: False")
            self.developerToggle.setStyleSheet("QPushButton {background-color:#904343; color:#dfdfdf}")
        
        # Adding Widgets to Settings
        settingsLayout.addWidget(self.themeLabel)
        settingsLayout.addWidget(self.themeDropdown)
        settingsLayout.addSpacing(35)
        settingsLayout.addWidget(self.updateLabel)
        settingsLayout.addWidget(self.updateButton)
        settingsLayout.addSpacing(35)
        settingsLayout.addWidget(self.infoLabel)
        settingsLayout.addWidget(self.versionLabel)
        settingsLayout.addWidget(self.authorsLabel)
        settingsLayout.addWidget(self.githubLabel)
        settingsLayout.addWidget(self.discordLabel)
        settingsLayout.addSpacing(70)
        settingsLayout.addWidget(self.developerLabel)
        settingsLayout.addWidget(self.developerToggle)
        settingsLayout.addWidget(self.relistButton)
        settingsLayout.addStretch()
        
        #Hides developer settings
        developerModeWidgets(crl.checkInConfig("App Settings", "dev_mode"), self)
        self.reloadInstances(self.homeLayout)
        
    def reloadInstances(self, homeLayout):
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
        buttonLayout = FlowLayout(buttonWidget)
        #List read from
        list = []
        #The actual reading of instances
        instancesPath = "instances"
        ##Checking if path exists
        crl.checkDirValidity(instancesPath)
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
                    instanceButton.clicked.connect(partial(self.launchInstance, instanceName, instanceButton))
                    instanceButton.setContextMenuPolicy(Qt.CustomContextMenu)
                    instanceButton.customContextMenuRequested.connect(self.showInstanceContextMenu)
                    
                    # Add button to layout
                    buttonLayout.addWidget(instanceButton)
        homeLayout.addWidget(buttonWidget)
        #Adds "Add Instance" button
        addInstance = QPushButton("Add Instance")
        addInstance.clicked.connect(self.addInstance)
        homeLayout.addWidget(addInstance)
        #Adds "Edit Instances" button
        editInstances = QPushButton("Edit Instances")
        editInstances.clicked.connect(self.editInstances)
        homeLayout.addWidget(editInstances)

        homeLayout.addStretch()
        
    def launchInstance(self, instanceName, senderButton):
        global runningInstances
        #Gets the button that called
        #Handles the instance launch
        print(f"Launching instance: {instanceName}")
        filePath = "instances/" + instanceName + "/about.json"
        if os.path.exists(filePath):
        #Checks if file exists
            if not instanceName in runningInstances:
                instanceVersion = json.load(open(filePath, "r"))
                print(instanceVersion["version"])
                check = crl.checkForVersion(instanceVersion["version"])
                if check == True:
                    senderButton.setStyleSheet("border-radius: 10px; background-color: #9043437d;")
                    print("Can run version!")
                    PID = crl.runVersion(str(instanceVersion["version"]), "placeholder", "placeholder", "placeholder")
                    runningInstances.append(instanceName)
                else:
                    print(check)
            else:
                print(f"Already running {instanceName}")
                
    def showInstanceContextMenu(self, pos):
        # Identify the button that triggered the context menu
        senderButton = self.sender()
        print(f"Sender {senderButton}")

        # Create the right-click menu for the instance button
        menu = QMenu(self)

        # Define the QMenu buttons
        editAction = menu.addAction("Edit Instance")
        editAction.triggered.connect(lambda: self.editInstance(senderButton))
        ssAction = menu.addAction("Stop Instance" if True else "Start Instance")  # Toggle based on instance status
        ssAction.triggered.connect(lambda: self.editInstance(senderButton))
        reloadAction = menu.addAction("Reload Instances")
        reloadAction.triggered.connect(lambda: self.reloadInstances(self.homeLayout))

        # Show the QMenu at the cursor position, relative to the sender button
        if senderButton:
            menu.exec(senderButton.mapToGlobal(pos))
        
    @QtCore.Slot()
    #Test
    def magic(self):
        print("working!")

    @QtCore.Slot()
    #Developer mode toggle & button colour update
    def toggleDeveloper(self):
        if self.developerToggle.isChecked():
        #Developer mode enabled
            self.developerToggle.setStyleSheet("QPushButton {background-color:#43904b; color:#dfdfdf}")
            self.developerToggle.setText("Developer Mode: Enabled")
        else:
        #Developer mode disabled
            self.developerToggle.setStyleSheet("QPushButton {background-color:#904343; color:#dfdfdf}")
            self.developerToggle.setText("Developer Mode: Disabled")
        #Updates in config and reloads developer mode widgets
        crl.updateInConfig("App Settings", "dev_mode", str(self.developerToggle.isChecked()))
        developerModeWidgets(self.developerToggle.isChecked(), self)

    @QtCore.Slot(int)
    #Updates theme when user selects a different one
    def updateThemeComboBox(self, value):
        crl.updateInConfig("App Settings", "app_theme", ["Dark", "Light", "Auto"][value])
        updateTheme()

    @QtCore.Slot()
    #Opens a new test window
    def editInstances(self):
        self.editInstance = QMainWindow()
        self.editInstance.setWindowTitle("New Window")
        self.editInstance.resize(300, 200)
        layout = QVBoxLayout()
        label = QLabel("This is a new window", self.editInstance)
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        layout.addWidget(label)
        self.editInstance.setCentralWidget(centralWidget)
        self.editInstance.show()

    @QtCore.Slot()
    def addInstance(self):
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
        self.instanceName.setText("New Instance")
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
        
    @QtCore.Slot()
    def selectIcon(self):
        filePath, _ = crl.openDialog("Select Icon", "Images (*.png *.xpm *.jpg)", self)
        if filePath:
            self.iconPathEdit.setText(filePath)
            pixmap = QPixmap(filePath)
            scaledPixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.iconLabel.setPixmap(scaledPixmap)
            
    @QtCore.Slot(str, str, str, str)
    def createInstance(self, loader, version, name, icon):
        crl.createFolder("instances")
        crl.createFolder("instances/" + name)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    updateTheme()
    
    window = MyWidget()
    window.resize(800, 600)
    window.setMinimumSize(420, 260)
    #Checks and creates files
    crl.checkDirValidity("instances")
    crl.checkDirValidity("meta/versions")
    #Sets window title based on OS
    if crl.checkOs():
        #macOs
        window.setWindowTitle("Unofficial Cosmic Reach Launcher - macOS")
        window.setWindowIcon(QIcon("assets/app_icons/icon.icns"))
        tray = QSystemTrayIcon()
        tray.setIcon(QIcon("assets/app_icons/icon.icns"))
        tray.setVisible(True)
        print()
    else:
        #Windows
        window.setWindowTitle("Unofficial Cosmic Reach Launcher - Windows")
        window.setWindowIcon(QIcon("assets/app_icons/ucrl_icon.png"))
    window.show()
    sys.exit(app.exec())