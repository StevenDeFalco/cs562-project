from src.connect.postgres import import_table

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QLineEdit,
    QPushButton, QMessageBox, QShortcut
)


class NewTableWindowUtil:

    '''
    Import from Postgres
    '''

    def create_import_postgres_tab(self):
        import_widget = QWidget()
        import_layout = QVBoxLayout()

        # Table name
        table_label = QLabel("Table name:")
        import_layout.addWidget(table_label)
        self.table_input = QLineEdit()
        import_layout.addWidget(self.table_input)
        
        # Username
        username_label = QLabel("Username:")
        import_layout.addWidget(username_label)
        self.username_input = QLineEdit()
        import_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Password:")
        import_layout.addWidget(password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        import_layout.addWidget(self.password_input)

        # Host and checkbox
        host_label = QLabel("Host:")
        import_layout.addWidget(host_label)
        self.host_input = QLineEdit()
        self.host_input.setText('localhost')
        self.host_input.setDisabled(True)
        import_layout.addWidget(self.host_input)
        self.host_checkbox = QCheckBox("On local machine")
        self.host_checkbox.setChecked(True)
        self.host_checkbox.stateChanged.connect(lambda state: self.toggle_input(self.host_input, state, 'localhost'))
        import_layout.addWidget(self.host_checkbox)

        # Port and checkbox
        port_label = QLabel("Port:")
        import_layout.addWidget(port_label)
        self.port_input = QLineEdit()
        self.port_input.setText('5432')
        self.port_input.setDisabled(True)
        import_layout.addWidget(self.port_input)
        self.port_checkbox = QCheckBox("Use default port")
        self.port_checkbox.setChecked(True)
        self.port_checkbox.stateChanged.connect(lambda state: self.toggle_input(self.port_input, state, '5432'))
        import_layout.addWidget(self.port_checkbox)

        # Import button
        import_button = QPushButton("Import Table")
        import_layout.addWidget(import_button)
        import_button.clicked.connect(self.import_postgres_table)
        import_button_shortcut = QShortcut(QKeySequence(Qt.Key_Return), self)
        import_button_shortcut.activated.connect(import_button.click)

        import_widget.setLayout(import_layout)
        self.tabWidget.addTab(import_widget, "Import from PostgreSQL")

    def import_postgres_table(self):
        try:
            import_table(self.table_input.text(),self.username_input.text(),self.password_input.text(),self.host_input.text(),self.port_input.text())
            self.close()
        except Exception as e:
            QMessageBox.information(self, "ERROR", str(e))

    def toggle_input(self, input, state, default_value):
        if state == Qt.Checked:
            input.setDisabled(True)
            input.setText(default_value)
        else:
            input.setDisabled(False)
            input.clear()
    
   

    #TODO - New Table

    
    
