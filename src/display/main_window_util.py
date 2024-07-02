from src.display.side_panel_util import SidePanelUtil
from src.display.central_widget_util import CentralWidgetUtil
from src.display.new_table_window import NewTableWindow

from PyQt5.QtWidgets import QMessageBox


class MainWindowUtil(CentralWidgetUtil,SidePanelUtil):

    def create_new_table_window(self):
        self.new_table_window = NewTableWindow(self)
        self.new_table_window.show()

    def new_table_window_closed_action(self):
        self.load_tables_list()

    def execute_button_clicked(self):
        #TODO
        print("Execute button clicked")

    def about(self):
        QMessageBox.about(self, "About", "")

    