import sys
import shutil
import traceback
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import *
from assets.app_files import config, developer, app_info_and_update, web_interaction
from assets.app_files.logs import prepareLogs, log, passSelf, systemInfo
from assets.app_files import file_management
from assets.app_files import instance_management
from assets.app_files import system
from assets.app_files import instance_ui_management

prepareLogs()

log(systemInfo())

app_info_and_update.checkInstalledVersions()

class LogReaderThread(QThread):
    #Sends the updated log to the main thread
    logUpdated = Signal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False

    def run(self):
        self.running = True
        log("Starting log tab")
        #Reads the log file in a separate thread
        try:
            with open("logs/latest.log", "r") as file:
                log("Log tab started")
                text = file.read()
                self.logUpdated.emit(text, True)
                file.seek(0)
                line = len(file.readlines())
                file.seek(0, 2)
                while self.running:
                    text = file.readline()
                    if text:
                        file.seek(0)
                        lineList = file.readlines()
                        text = "".join(lineList[line:])
                        line = len(lineList)
                        self.logUpdated.emit(text, False)    
                        file.seek(0, 2)
                    QtCore.QThread.msleep(500)
        except Exception as e:
            log("Failed to start log tab!")
            log(f"Error reading log file: {e}")
            self.logUpdated.emit(f"Error reading log file: {e}")
        
    def stop(self):
        log("Exiting log tab")
        self.running = False

def customExceptHook(type, value, tb):
    formatted_traceback = ''.join(traceback.format_exception(type, value, tb)) #Tb stands for Traceback
    log(f"Unhandled exception:\nType: {type.__name__}\nValue: {value}\nTraceback:\n{formatted_traceback}")
    
    error_handling_mode = config.checkInConfig("App Settings", "error_handling_mode")
    log(f"Error Handling Mode: {error_handling_mode}")
    
    if error_handling_mode == "Shutdown":
        #Shuts down the application
        QtWidgets.QApplication.quit()
        sys.exit(1)
    
    elif error_handling_mode == "Alert":
        #Shows an error dialog
        QtWidgets.QMessageBox.warning(None, "Error", f"An unhandled exception occurred:\n{value}\n\nPlease check the logs.")
    
    #Lets the app keep running
    else:
        #Shows an error dialog
        pass
    
sys.excepthook = customExceptHook

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        #Sets up thread for logs
        self.logUpdateThread = LogReaderThread()
        self.logUpdateThread.logUpdated.connect(self.updateLogs)
        
        self.runningInstances = []
        self.runningInstancesProcess = {}
        
        ###Creating Tabs
        #Define Tabs
        self.tabs = QTabWidget(self)
        self.tabs.currentChanged.connect(self.onTabChanged) #Sends signal when tab changes
        self.homeTab = QScrollArea()
        self.settingsTab = QScrollArea()
        self.logTab = QScrollArea()
        # Set QScrollArea to be resizable
        self.homeTab.setWidgetResizable(True)
        self.settingsTab.setWidgetResizable(True)
        self.logTab.setWidgetResizable(True)
        #Add tabs to window
        self.tabs.addTab(self.homeTab, "Home")
        self.tabs.addTab(self.settingsTab, "Settings")
        self.tabs.addTab(self.logTab, "Logs")
        
        ###Modify & Defining tabs' layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.homeLayout = QtWidgets.QHBoxLayout(self.homeTab)
        settingsLayout = QtWidgets.QVBoxLayout(self.settingsTab)
        logLayout = QtWidgets.QVBoxLayout(self.logTab)
        self.homeTab.setLayout(self.homeLayout)
        self.settingsTab.setLayout(settingsLayout)
        self.logTab.setLayout(logLayout)
        #Create content widgets
        homeContent = QWidget()
        settingsContent = QWidget()
        logContent = QWidget()
        #Set layout for content widgets
        self.homeLayout = QtWidgets.QVBoxLayout(homeContent)
        self.logTab = QtWidgets.QVBoxLayout(logContent)
        #Add content widgets to scroll areas
        self.homeTab.setWidget(homeContent)
        self.settingsTab.setWidget(settingsContent)
        
        ###Defining Setting's Widgets
        ##Application theme label
        self.themeLabel = QLabel(self.settingsTab)
        self.themeLabel.setText("<div style ='font-size: 18px;'><b>Application Theme</b></div>")
        #Application theme dropdown box
        self.themeDropdown = QComboBox()
        dropdownFill = ["Dark", "Light", "Auto"]
        self.themeDropdown.addItems(dropdownFill)
        self.themeDropdown.currentIndexChanged.connect(self.updateThemeComboBox)
        self.themeDropdown.setCurrentIndex((dropdownFill).index(config.checkInConfig("App Settings", "app_theme")))
        #Startup Height and Width Spinners
        self.widthInput = QSpinBox()
        self.widthInput.setRange(420, 999999)
        self.widthInput.setValue(int(config.checkInConfig("App Settings", "defaultWidth")))
        self.heightInput = QSpinBox()
        self.heightInput.setRange(260, 999999)
        self.heightInput.setValue(int(config.checkInConfig("App Settings", "defaultHeight")))
        #A Horizontal Box For the Spinners
        self.tinyBoxWidthAndHeight = QHBoxLayout()
        self.tinyBoxWidthAndHeight.addWidget(self.widthInput)
        self.tinyBoxWidthAndHeight.addWidget(self.heightInput)
        #Startup Size Update Button
        self.updateDefaultSizeButton = QPushButton("Update Startup Size")
        self.updateDefaultSizeButton.clicked.connect(self.updateDefaultStartupSize)
        ##Update label
        self.updateLabel = QLabel(self.settingsTab)
        self.updateLabel.setText("<div style ='font-size: 18px;'><b>Update</b></div>")
        #Check for updates button
        self.updateButton = QPushButton("Check for Updates")
        self.updateButton.setIcon(QIcon("assets/button_icons/update_darkmode.svg"))
        self.updateButton.clicked.connect(self.magic)
        ##Info label
        self.infoLabel = QLabel(self.settingsTab)
        self.infoLabel.setText("<div style ='font-size: 18px;'><b>Info</b></div>")
        #Info (sub) labels
        self.versionLabel = QLabel(self.settingsTab)
        self.versionLabel.setText(f"<div style ='font-size: 13px;'>U.C.R.L. {app_info_and_update.returnAppVersion()}</div>") 
        self.authorsLabel = QLabel(self.settingsTab)
        self.authorsLabel.setText("<div style ='font-size: 13px;'>By <a href='https://github.com/ieatsoulsmeow'>IEatSoulsMeow</a> and <a href='https://github.com/lumilovesyou'>FelisAraneae</a>")
        self.authorsLabel.setOpenExternalLinks(True)
        self.githubLabel = QLabel(self.settingsTab)
        self.githubLabel.setText("<div style ='font-size: 13px;'>Source can be found on <a href='https://github.com/lumilovesyou/Unofficial-Cosmic-Reach-Launcher'>Github</a>")
        self.githubLabel.setOpenExternalLinks(True)
        self.discordLabel = QLabel(self.settingsTab)
        self.discordLabel.setText("<div style ='font-size: 13px;'>Join the unofficial <a href='https://discord.gg/jRs9q7FMSu'>Discord</a> for other Cosmic Reach launchers")
        self.discordLabel.setOpenExternalLinks(True)
        ##Developer settings label
        self.developerLabel = QLabel(self.settingsTab)
        self.developerLabel.setText("<div style ='font-size: 18px;'><b>Developer Settings</b></div>")
        #Developer mode enabled button
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
        #Application error mode label
        self.errorModeLabel = QLabel(self.settingsTab)
        self.errorModeLabel.setText("<div style ='font-size: 12px;'><b>Application Error Mode</b></div>")
        #Application error mode dropdown box
        self.errorDropdown = QComboBox()
        dropdownFill = ["Shutdown", "Alert", "Continue"]
        self.errorDropdown.addItems(dropdownFill)
        self.errorDropdown.currentIndexChanged.connect(self.updateErrorComboBox)
        self.errorDropdown.setCurrentIndex((dropdownFill).index(config.checkInConfig("App Settings", "error_handling_mode")))
        #Developer buttons
        self.relistButton = QPushButton("Reload Instances")
        self.relistButton.clicked.connect(lambda: instance_ui_management.reloadInstances(self, self.homeLayout, self.runningInstances))
        self.checkVersionsButton = QPushButton("Check Installed Versions")
        self.checkVersionsButton.clicked.connect(lambda: app_info_and_update.checkInstalledVersions())
        
        ###Defining Log's Widgets
        #Log text area
        self.logTextArea = QTextEdit("Testing Testing 1... 2... 3...")
        self.logTextArea.setReadOnly(True)
        #Send log text area
        self.devLogTextArea = QTextEdit()
        self.devLogTextArea.setFixedHeight(50)
        #Send log button
        self.devLogSendButton = QPushButton("Log")
        self.devLogSendButton.clicked.connect(lambda: log(f"[dev] {self.devLogTextArea.toPlainText()}"))
        
        ###Adding Widgets to Settings
        settingsLayout.addWidget(self.themeLabel)
        settingsLayout.addWidget(self.themeDropdown)
        settingsLayout.addLayout(self.tinyBoxWidthAndHeight)
        settingsLayout.addWidget(self.updateDefaultSizeButton)
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
        settingsLayout.addWidget(self.errorModeLabel)
        settingsLayout.addWidget(self.errorDropdown)
        settingsLayout.addWidget(self.relistButton)
        settingsLayout.addWidget(self.checkVersionsButton)
        settingsLayout.addStretch()
        
        #Adding Widgets to Logs
        logLayout.addWidget(self.logTextArea)
        logLayout.addWidget(self.devLogTextArea)
        logLayout.addWidget(self.devLogSendButton)
        
        #Hides developer settings
        developer.developerModeWidgets(config.checkInConfig("App Settings", "dev_mode"), self)
        instance_ui_management.reloadInstances(self, self.homeLayout, self.runningInstances)
        
        passSelf(self)
        app_info_and_update.downloadAndProcessVersions()
        if not web_interaction.checkConnection():
            log("%e No connection!")
    
    # I tried to move this to instance_ui_management but it didn't work. I'll probably revisit that in the future and figure it out. Or not.
    def showInstanceContextMenu(self, pos):
        # Identify the button that triggered the context menu
        senderButton = self.sender()
        log(f"Sender {senderButton}")

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
    
    ### Logs related stuff     
    def updateLogs(self, text: str, set: bool = False):
        #Updates the log text
        if set:
            self.logTextArea.setText(text)
        else:
            self.logTextArea.moveCursor(QtGui.QTextCursor.End)
            self.logTextArea.insertPlainText(text)
            if type(text) is list:
                pass
        
    def onTabChanged(self, index):
        if self.tabs.tabText(index) == "Logs" and not self.logUpdateThread.isRunning():
            self.logUpdateThread.start() #Starts the thread to update logs
        else:
            self.logUpdateThread.stop() #Stops the thread
    ###

    @QtCore.Slot()
    def magic(self):
        log("Magic!")

    @QtCore.Slot()
    #Developer mode toggle & button colour update
    def callToggleDeveloper(self):
        developer.toggleDeveloper(self)
        
    @QtCore.Slot()
    def updateDefaultStartupSize(self):
        config.updateInConfig("App Settings", "defaultWidth", self.widthInput.value())
        config.updateInConfig("App Settings", "defaultHeight", self.heightInput.value())

    @QtCore.Slot(int)
    #Updates theme when user selects a different one
    def updateThemeComboBox(self, value):
        config.updateInConfig("App Settings", "app_theme", ["Dark", "Light", "Auto"][value])
        config.updateTheme()
        
    @QtCore.Slot(int)
    def updateErrorComboBox(self, value):
        config.updateInConfig("App Settings", "error_handling_mode", ["Shutdown", "Alert", "Continue"][value])

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
        try:
            ##Makes sure file path is valid
            validCharacters = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789()-_ ")
            filePath = list(name)
            for i in range(len(filePath)):
                if not filePath[i] in validCharacters:
                    filePath[i] = "_"
            filePath = "".join(filePath)
            ##
            ##Creates the instances folder
            location = "instances/" + filePath
            file_management.createFolder("instances")
            ##
            ##Checks if the instance name is taken
            if file_management.checkForDir(location):
                '''
                log(f"Couldn't make instance \"{filePath}\" because it already exists!")
                system.openErrorWindow(self, f"Couldn't make instance \"{filePath}\" because it already exists!", "Error")
                return
                '''
                locationAssure = location
                i = 0
                while file_management.checkForDir(locationAssure):
                    i += 1
                    locationAssure = f"{location} ({i})"
                location = locationAssure
            ##
            ##Creates the instance folder, icon, and files
            file_management.createFolder(location)
            with open(f"{location}/about.json", "w") as file:
                name = name.replace('"', '\\"')
                file.write(f'{{"name": "{name}","version": "{version}","keys": {{}}}}')
                file.close()
            if not icon == "assets/app_icons/ucrl_icon.png":
                shutil.copy(icon, f"{location}/icon.{icon.split('.')[-1]}")
            ##
            
            if not app_info_and_update.hasVersionInstalled(version): #Checks to see if the instance version is already installed
                app_info_and_update.installVersion(version) #Installs if not
            
            self.newInstance.close() #Closes the instance window
            instance_ui_management.reloadInstances(self, self.homeLayout, self.runningInstances) #Reloads the displayed instances
        except Exception as e:
            log(f"Failed to create instance: {e}")
            system.openErrorWindow(str(e), "Failed to Create Instance!")
        
        
def onAboutToQuit():
    log("Application Exited")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.aboutToQuit.connect(onAboutToQuit)
    config.updateTheme()

    window = MyWidget()
    window.resize(int(config.checkInConfig("App Settings", "defaultWidth")), int(config.checkInConfig("App Settings", "defaultHeight")))
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
    else:
        #Windows
        window.setWindowTitle("Unofficial Cosmic Reach Launcher - Windows")
        window.setWindowIcon(QIcon("assets/app_icons/ucrl_icon.png"))
    window.show()
    sys.exit(app.exec())