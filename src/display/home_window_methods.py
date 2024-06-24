



from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QToolButton, QTextEdit, 
    QMessageBox, QFileDialog, QTabBar, QSizePolicy, QStyle
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class HomeWindowMethods:

    '''
    creates the screen that displays the logo when there are no query tabs
    '''
    def create_logo_screen(self):
        logo_widget = QWidget()
        layout = QVBoxLayout(logo_widget)
        image_label = QLabel()
        image_label.setFixedSize(450, 450)
        image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(image_label, alignment=Qt.AlignCenter)
        pixmap = QPixmap(self.background_image)
        image_label.setPixmap(pixmap.scaled(
            image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
        return logo_widget
    
    '''
    creates a new 
    '''

    def new_query_tab(self):
        if self.stackedCentralWidget.currentWidget() == self.logo_screen:
            self.stackedCentralWidget.setCurrentWidget(self.tabWidget)
        name = f"Query {self.new_query_counter}"
        self.new_query_counter += 1
        new_editor = QTextEdit()
        new_editor.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        new_index = self.tabWidget.addTab(new_editor, name)
        self.tabWidget.setCurrentIndex(new_index)
        self.add_close_button(new_index)
        self.set_initial_zoom(new_editor)

    def add_close_button(self, index):
        tab = QWidget()
        tabLayout = QHBoxLayout()
        tabLayout.setContentsMargins(0, 0, 0, 0)
        closeButton = QToolButton()
        closeButton.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        closeButton.setStyleSheet("background: transparent;")
        closeButton.clicked.connect(lambda: self.close_tab_with_prompt(index))
        tabLayout.addWidget(closeButton)
        tab.setLayout(tabLayout)
        self.tabWidget.tabBar().setTabButton(index, QTabBar.RightSide, tab)

    def close_tab_with_prompt(self, index):
        current_editor = self.tabWidget.widget(index)
        
        if isinstance(current_editor, QTextEdit) and current_editor.document().isModified():
            reply = QMessageBox.question(
                self, 'Save Changes',
                "Do you want to save changes to this tab before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                if not self.save_file():
                    return
            elif reply == QMessageBox.Cancel:
                return
            
        self.tabWidget.removeTab(index)
        if self.tabWidget.count() == 0:
            self.stackedWidget.setCurrentWidget(self.logo_screen)
        else:
            if index < self.tabWidget.count():
                self.tabWidget.setCurrentIndex(index)
            else:
                self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def set_initial_zoom(self, editor):
        current_font = editor.font()
        current_font.setPointSize(current_font.pointSize() + 8)
        editor.setFont(current_font)

    def open_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if fileName:
            try:
                with open(fileName, 'r') as file:
                    text = file.read()
                    self.new_query_tab()
                    current_editor = self.tabWidget.currentWidget()
                    current_editor.setText(text)
                    self.tabWidget.setTabText(self.tabWidget.currentIndex(), fileName)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if fileName:
            try:
                current_editor = self.tabWidget.currentWidget()
                with open(fileName, 'w') as file:
                    file.write(current_editor.toPlainText())
                self.tabWidget.setTabText(self.tabWidget.currentIndex(), fileName)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not save file: {e}")

    def create_import_table(self):
        pass

    def about(self):
        QMessageBox.about(self, "About", "This is a simple text editor example created with PyQt5.")

    def undo_action(self):
        self.tabWidget.currentWidget().undo()

    def redo_action(self):
        self.tabWidget.currentWidget().redo()

    def copy_action(self):
        self.tabWidget.currentWidget().copy()

    def paste_action(self):
        self.tabWidget.currentWidget().paste()

    def zoom_in(self):
        current_editor = self.tabWidget.currentWidget()
        current_font = current_editor.font()
        current_font.setPointSize(current_font.pointSize() + 2)
        current_editor.setFont(current_font)

    def zoom_out(self):
        current_editor = self.tabWidget.currentWidget()
        current_font = current_editor.font()
        current_font.setPointSize(current_font.pointSize() - 2)
        current_editor.setFont(current_font)