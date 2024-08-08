from src.connect.postgres_oids import NUMERICAL_OIDs, STRING_OIDs, DATE_OID, BOOLEAN_OID

import os
import csv
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QMenu, QMessageBox, QAction


TABLES_DIRECTORY_PATH = '.tables'


class SidePanelActions:

    '''
    Table Menu Display
    '''
    
    def load_tables_list(self):
        self.tablesList.clear()

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
        deleteAction.triggered.connect(self.delete_table)
        infoAction = QAction('Get Info', self)
        infoAction.triggered.connect(self.get_table_info)
        menu.addAction(deleteAction)
        menu.addAction(infoAction)
        menu.exec_(self.tablesList.viewport().mapToGlobal(position))


    '''
    Table Menu Operations
    '''

    def delete_table(self):
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

        

    def get_table_info(self):
        if not hasattr(self, 'right_clicked_item') or self.right_clicked_item is None:
            return
        
        table_folder_name = self.right_clicked_item.text()
        path_to_table_folder = os.path.join(TABLES_DIRECTORY_PATH, table_folder_name)
        path_to_column_datatype_file = os.path.join(path_to_table_folder,'column_datatypes')


        if not os.path.exists(path_to_column_datatype_file):
            QMessageBox.critical(None, "Error", f"Could not retrieve table information. Delete and import the table again to be able to view the table information.")
            return

        column_data = []
        with open(path_to_column_datatype_file, mode='r') as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                column_oid = int(row[1].strip())
                print(column_oid)
                if column_oid in NUMERICAL_OIDs:
                    row[1] = 'Number'
                elif column_oid in STRING_OIDs:
                    row[1] = 'String'
                elif column_oid == DATE_OID:
                    row[1] = 'Date'
                elif column_oid == BOOLEAN_OID:
                    row[1] = 'Boolean'
                else:
                    row[1] = 'Unknown'

                column_data.append(row)


        headers = ['Column','Datatype']

        message = f"<h2>{table_folder_name.upper()} Table Column Information:</h2>"
        message += '<div style="text-align: center;">' 
        message += "<table border='1' cellpadding='5'>"
        message += "<tr><th>" + "</th><th>".join(headers) + "</th></tr>"
        for row in column_data:
            message += "<tr><td>" + "</td><td>".join(row) + "</td></tr>"
        message += "</table>"
        message += '</div>'
        
        info_window = QMessageBox()
        info_window.setTextFormat(Qt.RichText)
        info_window.setText(message)
        info_window.exec_()

        self.right_clicked_item = None
        

        
