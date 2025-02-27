import sys
import platform
from PySide6.QtWidgets import QFileDialog, QMainWindow, QVBoxLayout, QLabel, QWidget, QMessageBox

def checkOs():
    if platform.system() == 'Darwin':
        return True
    elif platform.system() == 'Windows':
        return False
    else:
        return ("Unknown")
    
def returnOsName():
    return(platform.system())
    
def openDialog(name, type, self):
    file_path, _ = QFileDialog.getOpenFileName(self, name, "", type)
    return file_path, _

#Opens a new test window
def openTestWindow(self):
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
    
def openErrorWindow(error: str , title:str = "Error"):
    QMessageBox.warning(None, title, error)