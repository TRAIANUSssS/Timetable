import psycopg2
import sys
import contextlib

from PyQt5.QtWidgets import (QApplication, QWidget,
                             QTabWidget, QAbstractScrollArea,
                             QVBoxLayout, QHBoxLayout,
                             QTableWidget, QGroupBox,
                             QTableWidgetItem, QPushButton, QComboBox)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.setFixedSize(1080, 640)

        self.setWindowTitle("TimeTabel")

        self.vbox = QVBoxLayout(self)
        self.tabs = QTabWidget(self)

        self.days_par_gbox = []  # QGroupBox("Monday")
        self.days_nonpar_gbox = []  # QGroupBox("Monday NP")
        self.days_lines_svbox = []  # QHBoxLayout()

        self.day_table = []
        self.dvbox = []

        self.subjects_records = []
        self.teachers_records = []

        self.subjects_list_names = []
        # tabs_create
        self.days_tabs = []
        self.tabs_vbox = []
        self.tabs_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Прeподаватели',
                           'Предметы']
        self.tables_names = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'teachers', 'subjects']

        # find_data_for_tabels
        self.subjects_combo_days_table = []
        self.subjects_days_table_list_names = []
        self.teachers_combo_days_table = []
        self.teachers_days_table_list_names = []

        # update_teachers_table
        self.subjects_combo_teachers_table = []
        self.subjects_teachers_table_list_names = []

        # create_update_button
        self.update_all = []



        self.start_work()
        # self._create_shedule_tab()

    # Запуск всех функций
    def start_work(self):
        self._connect_to_db()
        self.create_tabs()
        self.create_week_days()
        self.create_tabel()
        self.create_update_buttons()
        self.create_subject_tabel()
        self.create_teachers_table()
        self.find_data_for_tabels()

        for i in range(8):
            self.days_tabs[i].setLayout(self.tabs_vbox[i])

    # Запуск бд
    def _connect_to_db(self):
        self.conn = psycopg2.connect(database="timetabel_db",
                                     user="postgres",
                                     password="123",
                                     host="localhost",
                                     port="5432")

        self.cursor = self.conn.cursor()

    # Создание вкладок
    def create_tabs(self):
        self.vbox.addWidget(self.tabs)
        for i in range(8):
            self.days_tabs.append(QWidget())
            self.tabs.addTab(self.days_tabs[i], self.tabs_names[i])
            self.tabs_vbox.append(QVBoxLayout())

    # Создание блоков с днями
    def create_week_days(self):
        for i in range(8):
            if i < 6:
                self.days_par_gbox.append(QGroupBox(self.tabs_names[i] + ' чётная неделя'))
                self.days_nonpar_gbox.append(QGroupBox(self.tabs_names[i] + ' нечётная неделя'))
                self.days_lines_svbox.append(QHBoxLayout())

                self.tabs_vbox[i].addLayout(self.days_lines_svbox[i])
                self.days_lines_svbox[i].addWidget(self.days_par_gbox[i])
                self.days_lines_svbox[i].addWidget(self.days_nonpar_gbox[i])
            else:
                self.days_par_gbox.append(QGroupBox(self.tabs_names[i]))
                self.days_lines_svbox.append(QHBoxLayout())

                self.tabs_vbox[i].addLayout(self.days_lines_svbox[i])
                self.days_lines_svbox[i].addWidget(self.days_par_gbox[i])

    # Создание таблиц для дней
    def create_tabel(self):
        for i in range(12):
            self.day_table.append(QTableWidget())
            self.day_table[i].setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

            self.day_table[i].setColumnCount(4)
            self.day_table[i].setHorizontalHeaderLabels(["Subject", "Time", "Audience", "Teacher"])

            # self._update_monday_table(i)

            self.dvbox.append(QVBoxLayout())
            self.dvbox[i].addWidget(self.day_table[i])
            if i % 2 == 0:
                self.days_par_gbox[i // 2].setLayout(self.dvbox[i])
            else:
                self.days_nonpar_gbox[i // 2].setLayout(self.dvbox[i])

    # Находим данные для основных таблиц
    def find_data_for_tabels(self, ):
        for index in range(12):
            self.cursor.execute(f"SELECT * FROM {self.tables_names[index // 2]} Where parity=%s AND week_day=%s",
                                (str(True if index % 2 == 0 else False), str(self.tabs_names[index // 2])))
            records_temp = list(self.cursor.fetchall())
            # print(len(records), records)
            '''if (id == 0):
                print(len(records_temp))'''
            records = []

            for i in range(5):
                for j in range(len(records_temp)):
                    if int(records_temp[j][1]) == i or int(records_temp[j][1]) == i + 6:
                        records.append(records_temp[j])
                try:
                    if records[i] == None:
                        pass
                except:
                    r = ['', i, True if index % 2 == 0 else False, self.tabs_names[index // 2], '', '', '', '']
                    records.append(r)
            '''print(records)'''

            self.day_table[index].setRowCount(len(records))
            self.subjects_combo_days_table.append([])
            self.subjects_days_table_list_names.append([])
            self.teachers_combo_days_table.append([])
            self.teachers_days_table_list_names.append([])

            self.upload_tables(index, records)

    # Загружаем данные в таблицу
    def upload_tables(self, index, records):
        self.subjects_combo_days_table[index] = []
        self.subjects_days_table_list_names[index] = []
        self.teachers_combo_days_table[index] = []
        self.teachers_days_table_list_names[index] = []

        for i, r in enumerate(records):
            r = list(r)
            # print(i, r)
            # joinButton = buttons[i]
            if str(r[4]) == '':
                self.create_days_tables_subjects_list(index, 0, i, True)
                # self.day_table[id].setItem(i, 0, QTableWidgetItem(str(r[4])))
            else:
                self.create_days_tables_subjects_list(index, 0, i, False, str(r[4]))
            self.day_table[index].setItem(i, 1, QTableWidgetItem(str(r[5])))
            self.day_table[index].setItem(i, 2, QTableWidgetItem(str(r[6])))
            if str(r[7]) == '':
                self.create_days_table_teachers_list(index, 3, i, True)
            else:
                self.create_days_table_teachers_list(index, 3, i, False, str(r[7]))
        self.day_table[index].resizeRowsToContents()
        self.day_table[index].resizeColumnsToContents()

    # Создание выпадающего списка с преподователями
    def create_days_table_teachers_list(self, index, column, row, clear=True, first_teacher=None):
        combo = QComboBox(self)
        combo.addItems(self.find_techers(index, row, clear, first_teacher))
        self.teachers_combo_days_table[index].append(QHBoxLayout())
        try:
            self.teachers_combo_days_table[index][len(self.teachers_combo_days_table[index]) - 1].addWidget(combo)
        except:
            pass
        self.day_table[index].setCellWidget(row, column, combo)
        self.teachers_days_table_list_names[index].append(combo.currentText())
        combo.activated[str].connect(
            lambda: self.on_activated(combo.currentText(), row, self.teachers_days_table_list_names[index]))
        # combo.activated[str].connect(
        #    lambda: self.on_activated(self.upload_tabels()))

    # Находим нужных нам учителей
    def find_techers(self, index, row, clear, first_teacher):
        subj = self.subjects_days_table_list_names[index][row]
        index_list = []
        teachers_list = []
        if subj != 'Нет пары':
            print(subj)

        for i in range(len(self.subjects_teachers_table_list_names)):
            # if subj != 'Нет пары':
            #     print(subj, self.subjects_teachers_table_list_names[i])
            if self.subjects_teachers_table_list_names[i] == subj:
                # if subj != 'Нет пары':
                #     print(self.subjects_teachers_table_list_names[i], subj)
                index_list.append(i)
        for i in range(len(index_list)):
            teachers_list.append(self.day_table[13].item(index_list[i], 0).text())
            # print(teachers_list[i])
        if not clear:
            for i in range(len(teachers_list)):
                if teachers_list[i] == first_teacher:
                    teachers_list[i] = teachers_list[0]
                    teachers_list[0] = first_teacher
        return teachers_list

    # Создание и заполнение списка с предматами в таблицах с днями
    def create_days_tables_subjects_list(self, index, column, row, clear=True, first_word=None):
        combo = QComboBox(self)
        if clear:
            combo.addItems(self.get_subject_list(clear))
        else:
            combo.addItems(self.get_subject_list(clear, first_word))
        self.subjects_combo_days_table[index].append(QHBoxLayout())
        self.subjects_combo_days_table[index][len(self.subjects_combo_days_table[index]) - 1].addWidget(combo)
        self.day_table[index].setCellWidget(row, column, combo)
        self.subjects_days_table_list_names[index].append(combo.currentText())
        combo.activated[str].connect(
            lambda: self.on_activated_days_tables(combo.currentText(), row, self.subjects_days_table_list_names[index],
                                                  index))

    # Создание таблицы с преподавателями
    def create_teachers_table(self):
        self.day_table.append(QTableWidget())
        self.day_table[13].setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.day_table[13].setHorizontalHeaderLabels(["Teachers", "Subjects"])
        self.dvbox.append(QVBoxLayout())
        self.dvbox[13].addWidget(self.day_table[13])
        self.days_par_gbox[6].setLayout(self.dvbox[len(self.dvbox) - 1])

        self.update_teachers_table(True)

    # Заполнение таблицы с преподами
    def update_teachers_table(self, start):
        if start:
            self.cursor.execute(f"SELECT * FROM {self.tables_names[6]};")
            self.teachers_records = list(self.cursor.fetchall())
            self.day_table[13].setRowCount(len(self.teachers_records) + 1)
            self.day_table[13].setColumnCount(2)
        else:
            self.day_table[13].setRowCount(len(self.teachers_records) + 1)
        # print(self.teachers_records)
        # print(len(self.teachers_records))

        for i in range(len(self.teachers_records)):
            # joinButton = buttons[i]
            self.day_table[13].setItem(i, 0, QTableWidgetItem(str(self.teachers_records[i][0])))
            self.create_subjects_list(self.teachers_records[i][1], start, i)

        self.add_table_button = QPushButton("+")
        self.day_table[13].setCellWidget(len(self.teachers_records), 0, self.add_table_button)
        self.add_table_button.clicked.connect(lambda: self.add_teachers_table())

        self.delete_table_button = QPushButton("-")
        self.day_table[13].setCellWidget(len(self.teachers_records), 1, self.delete_table_button)
        self.delete_table_button.clicked.connect(lambda: self.delete_teachers_table())

        self.day_table[13].resizeRowsToContents()
        self.day_table[13].resizeColumnsToContents()

    def delete_teachers_table(self):
        for i in range(self.day_table[13].rowCount() - 2):
            self.teachers_records[i] = tuple(
                list((str(self.day_table[13].item(i, 0).text()), self.subjects_teachers_table_list_names[i])))
        self.day_table[13].clearContents()
        # self.update_subsidiary_tabel(6,1)
        self.cursor.execute("DELETE FROM teachers WHERE id = (SELECT id FROM teachers ORDER BY id DESC LIMIT 1)")
        self.conn.commit()
        self.update_teachers_table(True)

    # Заполнение и создание выподающего списка в таблице с преподами
    def create_subjects_list(self, first_word, start, i):
        combo = QComboBox(self)
        combo.addItems(self.get_subject_list(False, first_word))
        self.subjects_combo_teachers_table.append(QHBoxLayout())
        self.subjects_combo_teachers_table[len(self.subjects_combo_teachers_table) - 1].addWidget(combo)
        self.day_table[13].setCellWidget(i, 1, combo)
        self.subjects_teachers_table_list_names.append(combo.currentText())
        combo.activated[str].connect(
            lambda: self.on_activated(combo.currentText(), i, self.subjects_teachers_table_list_names))
        # print(len(self.subjects_combo_teachers_table))

    def on_activated_days_tables(self, text, row, var, index):
        print(text)
        records = []
        print(records)
        for i in range(5):
            records.append([])
            for j in range(4):
                records[i].append('')
            records[i].append(self.subjects_days_table_list_names[index][i])
            records[i].append(self.day_table[index].item(i, 1).text())
            records[i].append(self.day_table[index].item(i, 2).text())
            records[i].append('')
        records[row][4] = text
        print(records)
        self.upload_tables(index, records)

    # Сохранение выбраной переменной из выпадающего списка
    def on_activated(self, text, index, var):
        print(text)
        var[index] = text

    # Добавление строки в таблицу с учителями или обновление этой таблицы
    def add_teachers_table(self, flag=True):
        for i in range(self.day_table[13].rowCount() - 1):
            self.teachers_records[i] = tuple(
                list((str(self.day_table[13].item(i, 0).text()), self.subjects_teachers_table_list_names[i])))
        self.day_table[13].clearContents()
        if flag:
            self.teachers_records.append(tuple(list(('', ''))))
        self.update_teachers_table(False)

    # инициализация таблицы с предметами
    def create_subject_tabel(self):
        self.day_table.append(QTableWidget())
        self.day_table[12].setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.day_table[12].setHorizontalHeaderLabels(["Subjects"])
        self.dvbox.append(QVBoxLayout())
        self.dvbox[12].addWidget(self.day_table[12])
        self.days_par_gbox[7].setLayout(self.dvbox[len(self.dvbox) - 1])

        self.update_subjects_table(True)

    # Заполнение таблицы с предметами
    def update_subjects_table(self, start):
        if start:
            self.cursor.execute(f"SELECT * FROM {self.tables_names[7]};")
            self.subjects_records = list(self.cursor.fetchall())
            self.day_table[12].setRowCount(len(self.subjects_records) + 2)
            self.day_table[12].setColumnCount(1)
        else:
            self.day_table[12].setRowCount(len(self.subjects_records) + 2)
        # print(self.subjects_records)
        # print(len(self.subjects_records))

        for i in range(len(self.subjects_records)):
            # joinButton = buttons[i]
            self.day_table[12].setItem(i, 0, QTableWidgetItem(str(self.subjects_records[i][0])))
        self.add_subjects_button = QPushButton("+")
        self.day_table[12].setCellWidget(len(self.subjects_records), 0, self.add_subjects_button)
        self.add_subjects_button.clicked.connect(lambda: self.add_button_subjects())

        self.delete_subjects_button = QPushButton("-")
        self.day_table[12].setCellWidget(len(self.subjects_records) + 1, 0, self.delete_subjects_button)
        self.delete_subjects_button.clicked.connect(lambda: self.delete_button_subjects())

        self.day_table[12].resizeRowsToContents()
        self.day_table[12].resizeColumnsToContents()

    def delete_button_subjects(self):
        for i in range(self.day_table[12].rowCount() - 3):
            self.subjects_records[i] = tuple(list((str(self.day_table[12].item(i, 0).text()), '')))
        self.day_table[12].clearContents()
        self.cursor.execute("DELETE FROM subjects WHERE id = (SELECT id FROM subjects ORDER BY id DESC LIMIT 1)")
        self.conn.commit()
        self.update_subjects_table(True)

    # Добавление новой строки в таблицу с предметами
    def add_button_subjects(self):
        for i in range(self.day_table[12].rowCount() - 2):
            self.subjects_records[i] = tuple(list((str(self.day_table[12].item(i, 0).text()), '')))
        self.day_table[12].clearContents()
        self.subjects_records.append(tuple(list(('', ''))))
        self.update_subjects_table(False)

    # Инициализация кнопок обновления для каждой вкладки
    def create_update_buttons(self):
        self.update_all = []
        # self.update_button = []
        for i in range(8):
            self.update_all.append(QHBoxLayout())
            self.tabs_vbox[i].addLayout(self.update_all[i])
            self.create_button(i)

    # Добаление и реализация работы кнопок обновления
    def create_button(self, i):
        self.update_button = QPushButton("Update")
        self.update_all[i].addWidget(self.update_button)
        if i < 6:
            self.update_button.clicked.connect(lambda: self.update_days_tabel(i))
        else:
            self.update_button.clicked.connect(lambda: self.update_subsidiary_tabel(i))

    # Обновление доп таблиц
    def update_subsidiary_tabel(self, tab_id, count=0):
        self.cursor.execute(f"DELETE FROM {self.tables_names[tab_id]}")
        self.conn.commit()
        if tab_id == 7:
            for i in range(self.day_table[12].rowCount() - 1 - count):
                with contextlib.suppress(Exception):
                    self.cursor.execute(
                        f"INSERT INTO {self.tables_names[tab_id]}  (subjects) VALUES (%s);",
                        (str(self.day_table[12].item(i, 0).text()),))
                    self.conn.commit()
                # except Exception:
                #     pass
                    # self.cursor.execute(
                    #     f"INSERT INTO {self.tables_names[tab_id]}  (subjects) VALUES (%s);",
                    #     (str(''),))
        else:
            for i in range(self.day_table[13].rowCount() - 1 - count):
                # print(self.self.subjects_combo_teachers_table[i])
                # print(self.day_table[13].item(i, 0))
                print(i)
                self.cursor.execute(
                    f"INSERT INTO {self.tables_names[tab_id]}  (teachers, subjects) VALUES (%s,%s);",
                    (str(self.day_table[13].item(i, 0).text()),
                     str(self.subjects_teachers_table_list_names[i])))
                self.conn.commit()
        for i in range(6):
            self.update_subjects_table(i)
        self.create_subject_tabel()
        self.create_teachers_table()
        self.find_data_for_tabels()

    # Обновление таблиц дней недели
    def update_days_tabel(self, index):
        self.cursor.execute(f"DELETE FROM {self.tables_names[index]}")
        self.conn.commit()
        for k in range(2):
            '''print(index + 6 * k)'''
            for i in range(self.day_table[index * 2 + k].rowCount()):
                row = []
                for j in range(self.day_table[index * 2 + k].columnCount()):

                    if j == 1 or j == 2:
                        row.append(self.day_table[index * 2 + k].item(i, j).text())
                    elif j == 0:
                        row.append(self.subjects_days_table_list_names[index * 2 + k][i])
                    else:
                        row.append(self.teachers_days_table_list_names[index * 2 + k][i])
                # print(self.subjects_days_table_list_names[0])
                # print(row)
                self.cursor.execute(
                    f"""INSERT INTO {self.tables_names[index]} 
                    (subject, time, audience, teacher, parity, week_day, number) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s);""",
                    ((str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(True if k % 2 == 0 else False),
                      self.tabs_names[index], str(i))))
                self.conn.commit()

    # Получение значений из выпадающего списка
    def get_subject_list(self, start, first_word=None):
        self.cursor.execute("SELECT * FROM subjects")
        r = list(self.cursor.fetchall())
        records = []
        for i in r:
            records.append(str(i[0]))
        if not start:
            for i in range(len(records)):
                if records[i] == first_word:
                    records[i] = records[0]
                    records[0] = first_word
        # print(records)
        return records


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
