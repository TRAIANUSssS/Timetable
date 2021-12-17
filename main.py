import telebot
from telebot import types
import time
import psycopg2

bot = telebot.TeleBot('5050419657:AAEVrwvvdC1UCF-1eK0hU7ftKVoCeGsBjKQ')
parity = -1
week = 0

all_buttons = ["Понедельник", 'Вториник', "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье",
               "Расписание на текущуюю неделю", "Расписание на следующую неделю", '/help']

tabels_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

conn = psycopg2.connect(database="timetabel_db",
                        user="postgres",
                        password="123",
                        host="localhost",
                        port="5432")
cursor = conn.cursor()


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = add_keybord()
    bot.send_message(message.chat.id,
                     'Здравствуйте, это мой телеграм бот, который может показывать расписание, выбирайте день',
                     reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def iNeedHelp(message):
    keyboard = types.ReplyKeyboardMarkup(True)
    keyboard.add("/start")
    bot.send_message(message.chat.id,
                     'Здравствуйте, это мой телеграм бот, который может показывать расписание, выбирайте день',
                     reply_markup=keyboard)


@bot.message_handler(commands=['week'])
def tooday_week(message):
    bot.send_message(message.chat.id, f'Текущая неделя: {week}')


@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text in all_buttons:
        if parity == -1:
            calc_parity()
        index = all_buttons.index(message.text)
        if index <= 5:
            printTimetabel(message, index)
        if index == 6:
            bot.send_message(message.chat.id, 'Этот день создан для отдыха')
        if index == 7 or index == 8:
            printTimetabel(message, index, True, int((index + 1) % 2))


@bot.message_handler()
def wrong(message: types.Message):
    bot.send_message(message.chat.id, 'Неверная команда!')


def printTimetabel(message, index, all_days=False, reverse_parity=0):
    if reverse_parity == 0:
        par = True if parity == 0 else False
    else:
        par = False if parity == 0 else True
    # print('четность ' + str(par))

    if all_days == False:
        cursor.execute(f"SELECT * FROM {tabels_names[index]}")
        records = list(cursor.fetchall())

        line = get_line_with_timetable(records, par, index)
    else:
        for i in range(6):
            cursor.execute(f"SELECT * FROM {tabels_names[i]}")
            records = list(cursor.fetchall())
            line = ' '
            line += get_line_with_timetable(records, par, index)
    bot.send_message(message.chat.id, line)


@bot.message_handler()
def wrong(message: types.Message):
    bot.send_message(message.chat.id, 'Неверная команда!')


def get_line_with_timetable(records, par, index):
    line = ' '
    iteartion = 0
    line += '-----=====' + all_buttons[index] + '=====-----' + '\n'
    for i in range(len(records)):
        if str(records[i][2]) == str(par) and records[i][4] != 'Нет пары':
            audience = ', Аудитория: ' + records[i][6] if records[i][6] != '-' else ', Дистанционно'
            line += records[i][4] + audience + ', ' + records[i][5] + ', ' + records[i][7] + '\n'
            iteartion += 1
    if iteartion == 0:
        line += "День отдыха" + '\n'
    return line


def calc_parity():
    global parity, week
    start_time = int(time.time())
    today = int(time.time())

    start_time = calc_monday(start_time, True)
    today = calc_monday(today)
    weeks_count = (today - start_time) / 604800 + 1
    # print(weeks_count)
    week = int(weeks_count)
    parity = int(weeks_count % 2)


def calc_monday(data, sep=False):
    if sep == False:
        while time.strftime('%A', time.gmtime(data)) != 'Monday':
            data -= 86400
    else:
        while time.strftime('%Y', time.gmtime(data)) != '2021' or time.strftime('%B', time.gmtime(
                data)) != 'September' or time.strftime('%d', time.gmtime(data)) != '01':
            data -= 86400
    return data


def add_keybord():
    keyboard = types.ReplyKeyboardMarkup(True)
    for item in all_buttons:
        keyboard.row(item)
    return keyboard


if __name__ == '__main__':
    calc_parity()
    bot.polling(none_stop=True)
    '''while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)'''
