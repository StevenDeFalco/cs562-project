import sys

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QTabWidget, QVBoxLayout, QWidget, QSplitter, QMessageBox,
    QListWidget, QPushButton, QHBoxLayout, QSizePolicy, QStackedWidget
)


import src.display.stylesheets as ss
from src.display.side_panel_actions import SidePanelActions
from src.display.central_widget_actions import CentralWidgetActions
from src.display.new_table_window_actions import NewTableWindowActions



class MainWindow(QMainWindow,CentralWidgetActions,SidePanelActions):
    
    def __init__(self):
        super().__init__() 
        
        self.new_query_counter = 1
        self.background_image = 'assets/images/home_icon'
        
        self.initHomeWindow()
        self.showLayout()

    def initHomeWindow(self):
        self.setWindowTitle("ExtendedSQL")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(ss.darkmode_stylesheet)     # Default to dark mode theme

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

        # Create the buttons
        self.execute_button = QPushButton("Execute")
        self.execute_button.clicked.connect(self.execute)

        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.open_file)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_file)

        # Set the same size for all buttons
        self.execute_button.setFixedSize(80, 30)
        self.open_button.setFixedSize(80, 30)
        self.save_button.setFixedSize(80, 30)

        # Create a layout for the buttons
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.open_button)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addStretch(1)
        self.button_layout.addWidget(self.execute_button)
        

        # Create a widget to hold the buttons
        self.button_widget = QWidget()
        self.button_widget.setLayout(self.button_layout)

        # Create a layout to hold the tab widget and the button widget
        self.top_layout = QVBoxLayout()
        self.top_layout.addWidget(self.tabWidget)
        self.top_layout.addWidget(self.button_widget)

        # Create a widget to hold the top layout
        self.top_widget_container = QWidget()
        self.top_widget_container.setLayout(self.top_layout)

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.top_widget_container)
        self.splitter.addWidget(self.execution_output_screen)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setSizes([500, 250])

        self.stackedCentralWidget = QStackedWidget()
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

        menubar = self.menuBar()

        
        # Application menu
        applicationMenu = menubar.addMenu('')

        aboutAct = QAction(QIcon(), 'About', self)
        aboutAct.triggered.connect(self.about)
        applicationMenu.addAction(aboutAct)
        
        exitAct = QAction(QIcon(), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.close)
        applicationMenu.addAction(exitAct)


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


        # Run menu
        runMenu = menubar.addMenu('Run')

        executeAct = QAction(QIcon(), 'Execute', self)
        executeAct.triggered.connect(self.execute)
        executeAct.setShortcut('F5')
        runMenu.addAction(executeAct)


    def showLayout(self):
        main_layout = QHBoxLayout(self.mainWidget)
        main_layout.addLayout(self.leftSidePanel)
        main_layout.addWidget(self.stackedCentralWidget,stretch=4)
    

    def create_new_table_window(self):
        self.new_table_window = NewTableWindow(self)
        self.new_table_window.show()

    def new_table_window_closed_action(self):
        self.load_tables_list()

    def about(self):
        #TODO
        QMessageBox.about(self, "About", "")




class NewTableWindow(QMainWindow,NewTableWindowActions):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initNewTableWindow()

    def initNewTableWindow(self):
        self.setWindowTitle("New Table")
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet(ss.darkmode_stylesheet)     # Default to dark mode theme

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

    