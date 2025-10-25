from json import *
import telebot
from telebot import types
from threading import Thread

Students = {}
Teachers = {}

is_run = True



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
    def toJSON(self):
            return dumps(self.__dict__)

    def fromJSON(self, json_data):
            self.__dict__.update(loads(json_data))


def save_teachers_data(filename = "teachers.json"):
        global is_run
        while is_run:
            file = open(filename, "wb")
            data = {}
            for i in Teachers.keys():
                data[i] = Teachers[i].toJSON()
            file.write(bytes(dumps(data), "utf-8"))
            file.close()

def open_teachers_data(filename= "students.json"):
        file = open(filename, "rb")
        data = loads(file.read().decode("utf-8"))
        for i in data:
            teacher = Teacher()
            teacher.fromJSON(i)
        file.close()

class Class():
    def __init__(self, form):
        self.Themes = themes[str(form)]
        self.teachers = []
        self.form = form
        self.students = []



class Student():
    def __init__(self, nickname):
        self.subjects = []
        self.themes = []
        self.statistics = {}
        self.form = 1
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
            data = {}
            for i in Students.keys():
                data[i] = Students[i].toJSON()
            file.write(bytes(dumps(data), "utf-8"))
            file.close()

def open_students_data(filename= "students.json"):
        file = open(filename, "rb")
        data = loads(file.read().decode("utf-8"))
        for i in data.keys():
            student = Student(i)
            student.from_json(data[i])
        file.close()

#Загрузка данных
file = open('themes.json', 'r')
themes = load(file)
file.close()
t1 = Thread(target=save_teachers_data)
t2 = Thread(target=save_students_data)
t1.start()
t2.start()

bot = telebot.TeleBot('8215300847:AAHGW-KR6aJhm2uJgBtzdNJAYm093KwjVH0')
print("started")
@bot.message_handler(commands = ['start'])
def url(message):
    save_teachers_data


    """
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Ссылка на наш сайт', url='https://habr.com/ru/all/')
    bot.send_photo(message.from_user.id, photo=open('2025-10-25 12.50.58.jpg', 'rb'))
    markup.add(btn1)
    print(message.from_user.id)
    bot.send_message(message.from_user.id, "Ну что двоешники, наркоманы, вэйперы? Работать Будем????!", reply_markup = markup)
    """

bot.polling(none_stop=False, interval=0) #обязательная для работы бота часть