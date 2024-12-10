from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMenu
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create buttons
        self.button1 = QPushButton("Right-Click Me!")
        self.button2 = QPushButton("Don't Right-Click Me!")

        # Add buttons to the layout
        layout.addWidget(self.button1)
        layout.addWidget(self.button2)

        self.setCentralWidget(central_widget)

        # Connect the right-click menu to button1
        self.button1.setContextMenuPolicy(Qt.CustomContextMenu)
        self.button1.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        # Create the menu
        menu = QMenu(self)

        # Add actions
        action1 = menu.addAction("Action 1")
        action2 = menu.addAction("Action 2")
        action3 = menu.addAction("Action 3")

        # Map actions to functions
        action1.triggered.connect(lambda: self.menu_action_triggered("Action 1"))
        action2.triggered.connect(lambda: self.menu_action_triggered("Action 2"))
        action3.triggered.connect(lambda: self.menu_action_triggered("Action 3"))

        # Display the menu at the cursor's position
        menu.exec(self.button1.mapToGlobal(pos))

    def menu_action_triggered(self, action_name):
        print(f"{action_name} triggered!")

# Run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()
