from . import config

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
    config.updateInConfig("App Settings", "dev_mode", str(self.developerToggle.isChecked()))
    developerModeWidgets(self.developerToggle.isChecked(), self)
    
def developerModeWidgets(visibility, self):
#Toggles visibility for dev buttons
            if not visibility or visibility == "False":
                self.relistButton.hide()
            else:
                self.relistButton.show()