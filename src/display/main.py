from src.display.main_window_util import MainWindowUtil
from src.display.stylesheets import darkmode_stylesheet

import sys

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QDir
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QTabWidget, QVBoxLayout, QWidget, QLabel,
    QListWidget, QPushButton, QHBoxLayout, QSizePolicy, QMenuBar, QStackedWidget, QSplitter
)


class MainWindow(QMainWindow, MainWindowUtil):
    def __init__(self):
        super().__init__() 
        
        self.new_query_counter = 1
        self.background_image = 'public/images/home_icon'
        
        self.initHomeWindow()
        self.showLayout()

    def initHomeWindow(self):
        self.setWindowTitle("ExtendedSQL")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(darkmode_stylesheet)     # Default to dark mode theme

        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)


        ''' 
        Central Widget 
            - defaults to a screen with a logo
            - tabs can be added to with a text editor for writing queries
            - bottom panel for execution output
            - execution button on panel
        '''

        self.logo_screen = self.create_logo_screen()

        self.tabWidget = QTabWidget()
        self.tabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tabWidget.tabBar().tabCloseRequested.connect(self.close_tab_with_prompt)
        self.tabWidget.currentChanged.connect(self.toggle_output_screen)

        self.execution_output_screen = self.create_execution_output_screen()

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.tabWidget)
        self.splitter.addWidget(self.execution_output_screen)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setSizes([500, 250])

        # Create the execute button
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute_button_clicked)

        # Create a container widget and layout for the button
        self.execute_button_container = QWidget()
        self.execute_button_layout = QVBoxLayout()
        self.execute_button_layout.addWidget(self.execute_button)
        self.execute_button_layout.addStretch(1)  # Add stretch to push the button to the top
        self.execute_button_container.setLayout(self.execute_button_layout)

        self.splitter.addWidget(self.execute_button_container)

        self.stackedCentralWidget= QStackedWidget()
        self.stackedCentralWidget.addWidget(self.logo_screen)
        self.stackedCentralWidget.addWidget(self.splitter)
        self.stackedCentralWidget.setCurrentWidget(self.logo_screen)
        self.stackedCentralWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)      



    
        '''
        Left Side Panel 
            - 'Import Table' and 'New Query' buttons to the top left
            - List to display the tables
        '''
        
        self.leftSidePanel = QVBoxLayout()
        self.leftSidePanel.setSpacing(10)
        
        newTableButton = QPushButton("Import Table")
        newTableButton.clicked.connect(self.create_new_table_window)
       
        newQueryButton = QPushButton("New Query")
        newQueryButton.clicked.connect(self.new_query_tab)
        
        newQueryTableLayout = QHBoxLayout()
        newQueryTableLayout.addWidget(newTableButton)
        newQueryTableLayout.addWidget(newQueryButton)
        
        buttonPanelWidget = QWidget()
        buttonPanelWidget.setLayout(newQueryTableLayout)
        self.leftSidePanel.addWidget(buttonPanelWidget)

        self.tablesList = QListWidget()
        self.tablesList.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        self.tablesList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tablesList.customContextMenuRequested.connect(self.show_table_menu)
        self.tablesList.setSelectionMode(QListWidget.SingleSelection)
        self.leftSidePanel.addWidget(self.tablesList, 1)

        table_list_font = QFont()
        table_list_font.setPointSize(14)  
        self.tablesList.setFont(table_list_font)

        self.load_tables_list()


        '''
        Menu Bar
            - File: Actions for file management
            - Edit: Actions for text editing in the query tabs
        '''

        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        # File menu
        fileMenu = menubar.addMenu('File')

        openAct = QAction(QIcon(), 'Open', self)
        openAct.setShortcut('Ctrl+O')
        openAct.triggered.connect(self.open_file)
        fileMenu.addAction(openAct)

        saveAct = QAction(QIcon(), 'Save', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.triggered.connect(self.save_file)
        fileMenu.addAction(saveAct)

        exitAct = QAction(QIcon(), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.close)
        fileMenu.addAction(exitAct)

        # Edit menu
        editMenu = menubar.addMenu('Edit')

        undoAct = QAction(QIcon(), 'Undo', self)
        undoAct.setShortcut('Ctrl+Z')
        undoAct.triggered.connect(self.undo_action)
        editMenu.addAction(undoAct)

        redoAct = QAction(QIcon(), 'Redo', self)
        redoAct.setShortcut('Ctrl+Y')
        redoAct.triggered.connect(self.redo_action)
        editMenu.addAction(redoAct)

        copyAct = QAction(QIcon(), 'Copy', self)
        copyAct.setShortcut('Ctrl+C')
        copyAct.triggered.connect(self.copy_action)
        editMenu.addAction(copyAct)

        pasteAct = QAction(QIcon(), 'Paste', self)
        pasteAct.setShortcut('Ctrl+V')
        pasteAct.triggered.connect(self.paste_action)
        editMenu.addAction(pasteAct)

        zoomInAct = QAction(QIcon(), 'Zoom In', self)
        zoomInAct.setShortcut('Ctrl++')
        zoomInAct.triggered.connect(self.zoom_in)
        editMenu.addAction(zoomInAct)

        zoomOutAct = QAction(QIcon(), 'Zoom Out', self)
        zoomOutAct.setShortcut('Ctrl+-')
        zoomOutAct.triggered.connect(self.zoom_out)
        editMenu.addAction(zoomOutAct)

        # Help menu
        helpMenu = menubar.addMenu('Help')

        aboutAct = QAction(QIcon(), 'About', self)
        aboutAct.triggered.connect(self.about)
        helpMenu.addAction(aboutAct)


    def showLayout(self):
        main_layout = QHBoxLayout(self.mainWidget)
        main_layout.addLayout(self.leftSidePanel)
        main_layout.addWidget(self.stackedCentralWidget,stretch=4)


    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("ExtendedSQL")
    app.setApplicationDisplayName("ExtendedSQL")
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())

