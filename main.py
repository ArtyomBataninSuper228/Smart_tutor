from json import *
import telebot
from telebot import types

Students = {}
Teachers = {}





#Обьявление классов
class event():
    def __init__(self, time, type):
        pass
class Teacher():
    def __init__(self, nickname):
        self.classes = []
        self.subjects = []
        self. nickname = nickname
        Teachers[self.nickname] = self

class Class():
    def __init__(self, form):
        self.Themes = themes[str(form)]
        self.teachers = []
        self.form = form



class Student():
    def __init__(self, nickname, form):
        self.subjects = []
        self.themes = []
        self.statistics = {}
        self.form = form
        self.Class = None
        self.nickname = nickname
        self.studing_plan = {}
        Students[self.nickname] = self

        def toJSON(self):
            return dumps(self.__dict__)

        def fromJSON(self, json_data):
            self.__dict__.update(loads(json_data))


    def save_students_data(filename = "students.json"):
        global is_run
        while is_run:
            file = open(filename, "wb")
            data = []
            for i in Students:
                data.append(i.toJSON())
            file.write(bytes(dumps(data), "utf-8"))
            file.close()

    def open_users_data(filename= "students.json"):
        file = open(filename, "rb")
        data = loads(file.read().decode("utf-8"))
        for i in data:
            student = Student()
            student.fromJSON(i)
        file.close()


#Загрузка данных
file = open('themes.json', 'r')
themes = load(file)
file.close()

bot = telebot.TeleBot('8215300847:AAHGW-KR6aJhm2uJgBtzdNJAYm093KwjVH0')
print("started")
@bot.message_handler(commands = ['start'])
def url(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Ссылка на наш сайт', url='https://habr.com/ru/all/')
    bot.send_photo(message.from_user.id, photo=open('2025-10-25 12.50.58.jpg', 'rb'))
    markup.add(btn1)
    #print(message.from_user.id)
    bot.send_message(message.from_user.id, "Ну что двоешники, наркоманы, вэйперы? Работать Будем????!", reply_markup = markup)

bot.polling(none_stop=False, interval=0) #обязательная для работы бота часть