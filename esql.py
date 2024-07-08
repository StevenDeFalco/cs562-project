import sys

from PyQt5.QtWidgets import QApplication

import src.display.windows as windows


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    app.setApplicationName("ExtendedSQL")
    app.setApplicationDisplayName("ExtendedSQL")
    
    if sys.platform == 'darwin':
        from Foundation import NSBundle
        bundle = NSBundle.mainBundle()
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        info['CFBundleName'] = 'ExtendedSQL'

    mainWindow = windows.MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())

