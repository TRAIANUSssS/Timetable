import psycopg2
import sys

from PyQt5.QtWidgets import (QApplication, QWidget,
                             QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout,
                             QTableWidget, QGroupBox,
                             QTableWidgetItem, QPushButton, QMessageBox)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self._connect_to_db()

        self.setWindowTitle("Shedule")

        self.vbox = QVBoxLayout(self)

        self.tabs = QTabWidget(self)
        self.vbox.addWidget(self.tabs)

        self._create_shedule_tab()

    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="timetabel_db",
                                     user="postgres",
                                     password="123",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()

    def _create_shedule_tab(self):
        self.shedule_tab = QWidget()
        self.tabs.addTab(self.shedule_tab, "Shedule")

        self.monday_gbox = QGroupBox("Monday")

        self.svbox = QVBoxLayout()
        self.shbox1 = QHBoxLayout()
        self.shbox2 = QHBoxLayout()

        self.svbox.addLayout(self.shbox1)
        self.svbox.addLayout(self.shbox2)

        self.shbox1.addWidget(self.monday_gbox)

        self._create_monday_table()

        self.update_shedule_button = QPushButton("Update")
        self.shbox2.addWidget(self.update_shedule_button)
        self.update_shedule_button.clicked.connect(self._update_shedule)

        self.shedule_tab.setLayout(self.svbox)

    def _create_monday_table(self):
        self.monday_table = QTableWidget()
        self.monday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.monday_table.setColumnCount(5)
        self.monday_table.setHorizontalHeaderLabels(["Subject", "Time", "Audience", "Teacher", 'Join'])

        self._update_monday_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.monday_table)
        self.monday_gbox.setLayout(self.mvbox)

    def _update_monday_table(self):
        self.cursor.execute("SELECT * FROM timetabel WHERE parity=%s AND week_day=%s",
                            (str(True), str('Понедельник')))
        records = list(self.cursor.fetchall())
        print(len(records), records)

        self.monday_table.setRowCount(len(records))

        buttons = [QPushButton("Join", self), QPushButton("Join", self), QPushButton("Join", self)]
        for i, r in enumerate(records):
            r = list(r)
            print(i, r)
            joinButton = buttons[i]
            self.monday_table.setItem(i, 0,
                                      QTableWidgetItem(str(r[3])))
            self.monday_table.setItem(i, 1,
                                      QTableWidgetItem(str(r[4])))
            self.monday_table.setItem(i, 2,
                                      QTableWidgetItem(str(r[5])))
            self.monday_table.setItem(i, 3,
                                      QTableWidgetItem(str(r[6])))
            self.monday_table.setCellWidget(i, 4, joinButton)

            #print(i)

            joinButton.clicked.connect(lambda: print(records[i][0]))
            joinButton.clicked.connect(
                lambda: self._change_day_from_table(i, "monday"))

        self.monday_table.resizeRowsToContents()

    def _change_day_from_table(self, rowNum, day):
        row = list()
        for i in range(self.monday_table.columnCount() - 1):
            try:
                row.append(self.monday_table.item(rowNum, i).text())
            except:
                row.append(None)
        print(row)
        try:
            self.cursor.execute(
                "UPDATE timetabel SET  subject = %s, time = %s, audience = %s, teacher = %s WHERE parity=%s AND week_day=%s;",
                (str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(True), 'Понедельник'))
            self.conn.commit()
        except:
            QMessageBox.about(self, "Error", "Enter all fields")

    def _update_shedule(self):
        self._update_monday_table()


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
