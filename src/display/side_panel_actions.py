import os
import shutil

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QMenu, QMessageBox, QAction


TABLES_DIRECTORY_PATH = '.tables'


class SidePanelActions:

    '''
    Table Menu Display
    '''
    
    def load_tables_list(self):
        dir = QDir(TABLES_DIRECTORY_PATH) 
        dir.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        tables = dir.entryList()
        for table in tables:
            self.tablesList.addItem(table)

    def show_table_menu(self, position):
        item = self.tablesList.itemAt(position)
        if not item:
            return

        self.right_clicked_item = item

        menu = QMenu()
        deleteAction = QAction('Delete', self)
        deleteAction.triggered.connect(self.delete_folder)
        infoAction = QAction('Get Info', self)
        infoAction.triggered.connect(self.get_folder_info)
        menu.addAction(deleteAction)
        menu.addAction(infoAction)
        menu.exec_(self.tablesList.viewport().mapToGlobal(position))


    '''
    Table Menu Operations
    '''

    def delete_folder(self):
        if not hasattr(self, 'right_clicked_item') or self.right_clicked_item is None:
            return
        
        table_name = self.right_clicked_item.text()
        path = os.path.join(TABLES_DIRECTORY_PATH, table_name)
    
        reply = QMessageBox.question(
            self, 'Delete Table',
            f"Are you sure you want to delete the table '{table_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
    
        if reply == QMessageBox.Yes:
            if os.path.exists(path):
                shutil.rmtree(path)  
                self.tablesList.takeItem(self.tablesList.row(self.right_clicked_item))
            self.right_clicked_item = None

        

    def get_folder_info(self):
        if not hasattr(self, 'right_clicked_item') or self.right_clicked_item is None:
            return
        
        '''
        folder_name = self.right_clicked_item.text()
        path = os.path.join(QDir.currentPath(), folder_name)
        
        if os.path.exists(path):
            folder_info = f"Folder: {folder_name}\nPath: {path}\n"
            QMessageBox.information(self, "Folder Info", folder_info)
        self.right_clicked_item = None
        '''
