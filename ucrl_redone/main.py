import sys
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWidgets import *
from assets.app_files import config, developer
from assets.app_files import file_management
from assets.app_files import instance_management
from assets.app_files import system
from assets.app_files import instance_ui_management

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.runningInstances = []
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
        self.versionLabel.setText("<div style ='font-size: 13px;'>UCRL 0.0.8</div>")
        self.authorsLabel = QLabel(self.settingsTab)
        self.authorsLabel.setText("<div style ='font-size: 13px;'>By <a href='https://github.com/ieatsoulsmeow'>IEatSoulsMeow</a> and <a href='https://github.com/lumilovesyou'>FelisAraneae</a>")
        self.authorsLabel.setOpenExternalLinks(True)
        self.githubLabel = QLabel(self.settingsTab)
        self.githubLabel.setText("<div style ='font-size: 13px;'>Source can be found on <a href='https://github.com/lumilovesyou/Unofficial-Cosmic-Reach-Launcher'>Github</a>")
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
        self.themeDropdown.setCurrentIndex((dropdownFill).index(config.checkInConfig("App Settings", "app_theme")))
        #Buttons
        self.updateButton = QPushButton("Update Application")
        self.updateButton.setIcon(QIcon("assets/button_icons/update_darkmode.svg"))
        self.updateButton.clicked.connect(self.magic)
        #Buttons
        self.relistButton = QPushButton("Reload Instances")
        self.relistButton.clicked.connect(lambda: instance_ui_management.reloadInstances(self, self.homeLayout, self.runningInstances))
        #Toggle
        self.developerToggle = QPushButton("Developer Mode: ", self)
        self.developerToggle.setCheckable(True)
        self.developerToggle.setChecked(True)
        self.developerToggle.clicked.connect(self.callToggleDeveloper)
        if config.checkInConfig("App Settings", "dev_mode") == "True":
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
        developer.developerModeWidgets(config.checkInConfig("App Settings", "dev_mode"), self)
        instance_ui_management.reloadInstances(self, self.homeLayout, self.runningInstances)
    
    # I tried to move this to instance_ui_management but it didn't work. I'll probably revisit that in the future and figure it out. Or not.
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
        reloadAction.triggered.connect(lambda: instance_ui_management.reloadInstances(self, self.homeLayout, self.runningInstances))

        # Show the QMenu at the cursor position, relative to the sender button
        if senderButton:
            menu.exec(senderButton.mapToGlobal(pos))

    @QtCore.Slot()
    def magic(self):
        print("Magic!")

    @QtCore.Slot()
    #Developer mode toggle & button colour update
    def callToggleDeveloper(self):
        developer.toggleDeveloper(self)

    @QtCore.Slot(int)
    #Updates theme when user selects a different one
    def updateThemeComboBox(self, value):
        config.updateInConfig("App Settings", "app_theme", ["Dark", "Light", "Auto"][value])
        config.updateTheme()

    @QtCore.Slot()
    #Opens a new test window
    def editInstances(self):
        system.openTestWindow(self)

    @QtCore.Slot()
    def callAddInstance(self):
        instance_management.addInstance(self)
        
    @QtCore.Slot()
    def selectIcon(self):
        filePath, _ = system.openDialog("Select Icon", "Images (*.png *.xpm *.jpg)", self)
        if filePath:
            self.iconPathEdit.setText(filePath)
            pixmap = QPixmap(filePath)
            scaledPixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.iconLabel.setPixmap(scaledPixmap)
            
    @QtCore.Slot(str, str, str, str)
    def createInstance(self, loader, version, name, icon):
        file_management.createFolder("instances")
        file_management.createFolder("instances/" + name)
        
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    config.updateTheme()
    
    window = MyWidget()
    window.resize(800, 600)
    window.setMinimumSize(420, 260)
    #Checks and creates files
    file_management.checkDirValidity("instances")
    file_management.checkDirValidity("meta/versions")
    #Sets window title based on OS
    if system.checkOs():
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