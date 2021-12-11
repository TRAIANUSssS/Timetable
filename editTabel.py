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

        self.week_days = ['Понедельник']
        self.all_timetabel = self.getAllTimeTabel()


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

        self.svbox = QVBoxLayout()

        self.create_monday_line()
        self.create_update_all_button()
        self.create_tabel()
        #self._create_monday_table()

        self.shedule_tab.setLayout(self.svbox)

    def getAllTimeTabel(self):
        all_tabel = []
        print('----------------')
        for i,boolean in enumerate([True, False]):
            all_tabel.append([])
            for j in range(len(self.week_days)):
                all_tabel[i].append([])
                self.cursor.execute("SELECT * FROM timetabel WHERE parity=%s AND week_day=%s",
                                    (str(boolean), str(self.week_days[j])))
                records = list(self.cursor.fetchall())

                for k in range(len(records)):
                    all_tabel[i][j].append(records[k])
                    print(all_tabel[i][j][k])

        return all_tabel

    def create_update_all_button(self):
        self.update_all = QHBoxLayout()
        self.svbox.addLayout(self.update_all)
        self.update_shedule_button = QPushButton("Update")

        self.update_all.addWidget(self.update_shedule_button)
        self.update_shedule_button.clicked.connect(self._update_shedule)

    def create_monday_line(self):
        self.monday_gbox = QGroupBox("Monday")
        self.monady_nonpar_gbox = QGroupBox("Monday NP")
        self.monday_svbox = QHBoxLayout()
        self.svbox.addLayout(self.monday_svbox)

        self.monday_svbox.addWidget(self.monday_gbox)
        self.monday_svbox.addWidget(self.monady_nonpar_gbox)

    def update_tabel(self, id):
        print(id)

    def create_tabel(self):
        self.monday_table = []
        self.mvbox = []
        for i in range(1):
            self.monday_table.append(QTableWidget())
            self.monday_table[i].setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

            self.monday_table[i].setColumnCount(4)
            self.monday_table[i].setHorizontalHeaderLabels(["Subject", "Time", "Audience", "Teacher"])

            self._update_monday_table(i)

            self.mvbox.append(QVBoxLayout())
            self.mvbox[i].addWidget(self.monday_table[i])
            self.monday_gbox.setLayout(self.mvbox[i])

    def _create_monday_table(self):
        self.monday_table = QTableWidget()
        self.monday_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        self.monday_table.setColumnCount(4)
        self.monday_table.setHorizontalHeaderLabels(["Subject", "Time", "Audience", "Teacher"])

        self._update_monday_table()

        self.mvbox = QVBoxLayout()
        self.mvbox.addWidget(self.monday_table)
        self.monday_gbox.setLayout(self.mvbox)

        self.update_monday_svbox = QHBoxLayout()
        self.mvbox.addLayout(self.update_monday_svbox)
        self.update_mon_par = QPushButton("UPDATE", self)
        self.update_monday_svbox.addWidget(self.update_mon_par)
        self.update_mon_par.clicked.connect(lambda: self.update_tabel(0))


    def _update_monday_table(self, id):
        self.cursor.execute("SELECT * FROM timetabel WHERE parity=%s AND week_day=%s",
                            (str(True), str('Понедельник')))
        records = list(self.cursor.fetchall())
        print(len(records), records)

        self.monday_table[id].setRowCount(len(records))

        for i, r in enumerate(records):
            r = list(r)
            print(i, r)
            #joinButton = buttons[i]
            self.monday_table[id].setItem(i, 0,
                                      QTableWidgetItem(str(r[3])))
            self.monday_table[id].setItem(i, 1,
                                      QTableWidgetItem(str(r[4])))
            self.monday_table[id].setItem(i, 2,
                                      QTableWidgetItem(str(r[5])))
            self.monday_table[id].setItem(i, 3,
                                      QTableWidgetItem(str(r[6])))
            '''self.monday_table.setCellWidget(i, 4, buttons[i])

            #print(i)

            buttons[i].clicked.connect(lambda: print(records[i][0]))
            buttons[i].clicked.connect(
                lambda: self._change_day_from_table(i, "monday"))'''

            #self.create_button(records, i, id)
        self.monday_table[id].resizeRowsToContents()

    def create_button(self, rec, i, id):
        print('created button')
        joinButton = QPushButton("Join", self)
        self.monday_table[id].setCellWidget(i, 4, joinButton)
        joinButton.clicked.connect(lambda: print(rec[i][0]))
        joinButton.clicked.connect(lambda: self._change_day_from_table(i, "monday"))

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
