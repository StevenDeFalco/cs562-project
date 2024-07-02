from src.display.new_table_window_util import NewTableWindowUtil

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget


class NewTableWindow(QMainWindow,NewTableWindowUtil):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initNewTableWindow()

    def initNewTableWindow(self):
        self.setWindowTitle("New Table")
        self.setGeometry(200, 200, 600, 400)

        # Create central widget
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)

        # Create tab widget
        self.tabWidget = QTabWidget()
        self.create_import_postgres_tab()
        #TODO - New Table

        # Set layout for the central widget
        layout = QVBoxLayout(centralWidget)
        layout.addWidget(self.tabWidget)

    def closeEvent(self, event):
        if self.parent is not None:
            self.parent.new_table_window_closed_action()
        event.accept()

    