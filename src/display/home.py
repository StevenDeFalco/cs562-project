import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QTabWidget, QVBoxLayout, QWidget, 
    QListWidget, QPushButton, QHBoxLayout, QSizePolicy, QMenuBar, QStackedWidget
)

from stylesheets import *
from home_window_methods import HomeWindowMethods

class HomeWindow(QMainWindow, HomeWindowMethods):
    def __init__(self):
        super().__init__() 
        
        self.new_query_counter = 1
        self.background_image = '../../public/images/home_icon'
        
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
        '''

        self.logo_screen = self.create_logo_screen()

        self.tabWidget = QTabWidget()
        self.tabWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.stackedCentralWidget= QStackedWidget()
        self.stackedCentralWidget.addWidget(self.logo_screen)
        self.stackedCentralWidget.addWidget(self.tabWidget)
        self.stackedCentralWidget.setCurrentWidget(self.logo_screen)
        self.stackedCentralWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)       

    
        '''
        Left Side Panel 
            - 'Import/Create Table' and 'New Query' buttons to the top left
            - List to display the tables
        '''
        
        self.leftSidePanel = QVBoxLayout()
        self.leftSidePanel.setSpacing(10)
        
        newTableButton = QPushButton("Create/Import Table")
        newTableButton.clicked.connect(self.create_import_table)
       
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
        self.leftSidePanel.addWidget(self.tablesList, 1)

        
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
        mainLayout = QHBoxLayout(self.mainWidget)
        mainLayout.addLayout(self.leftSidePanel)
        mainLayout.addWidget(self.stackedCentralWidget,stretch=4)

    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("ExtendedSQL")
    app.setApplicationDisplayName("ExtendedSQL")
    mainWin = HomeWindow()
    mainWin.show()
    sys.exit(app.exec_())

