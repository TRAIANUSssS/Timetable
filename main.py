import telebot
from telebot import types
import time
import psycopg2

bot = telebot.TeleBot('5050419657:AAEVrwvvdC1UCF-1eK0hU7ftKVoCeGsBjKQ')
parity = -1

all_buttons = ["Понедельник", 'Вториник', "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье",
               "Расписание на текущуюю неделю", "Расписание на следующую неделю", '/help']

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


@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text in all_buttons:
        if parity == -1:
            calc_parity()
        index = all_buttons.index(message.text)
        if index <= 5:
            printTimetabel(message)
        if index == 6:
            bot.send_message(message.chat.id,'Этот день создан для отдыха')
        if index == 7 or index == 8:
            printTimetabel(message, True, int((index + 1) % 2))


def printTimetabel(message, all_days=False, reverse_parity=0):
    if reverse_parity == 1:
        par = True if parity == 0 else False
    else:
        par = False if parity == 0 else True
    print('четность ' + str(par))

    cursor.execute("SELECT * FROM timetabel")
    records = list(cursor.fetchall())

    line = ''
    if all_days == False:
        for row in records:
            if str(row[1]) == str(par) and row[2] == message.text:
                line += row[3] + ' ' + row[4] + ' ' + row[5] + ' ' + row[6] + '\n'
    else:
        for i in range(7):
            for row in records:
                if str(row[1]) == str(par) and row[2] == all_buttons[i]:
                    line += row[3] + ' ' + row[4] + ' ' + row[5] + ' ' + row[6] + '\n'
    bot.send_message(message.chat.id, line)


def calc_parity():
    global parity
    start_time = int(time.time())
    today = int(time.time())

    while time.strftime('%Y', time.gmtime(start_time)) != '2021' or time.strftime('%B', time.gmtime(
            start_time)) != 'September' or time.strftime('%d', time.gmtime(start_time)) != '01':
        start_time -= 86400
    start_time = calc_monday(start_time)
    today = calc_monday(today)
    weeks_count = (today - start_time) / 604800 + 1
    print(weeks_count)
    parity = int(weeks_count % 2)


def calc_monday(data):
    while time.strftime('%A', time.gmtime(data)) != 'Monday':
        data -= 86400
    return data


def add_keybord():
    keyboard = types.ReplyKeyboardMarkup(True)
    for item in all_buttons:
        keyboard.row(item)
    return keyboard


if __name__ == '__main__':
    bot.polling(none_stop=True)
    '''while True:
        try:
            
        except Exception as e:
            print(e)'''
