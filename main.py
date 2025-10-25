
import telebot
from telebot import types

bot = telebot.TeleBot('8490068257:AAHHp3X_UCTr0N7J7mANk9wDNXcFcttqA38')
class
class Teacher():
    def __init__(self, nickname):
        self.classes = []
        self.subjects = []
        self. nickname = nickname

class Class():
    def __init__(self, form):
        self.Themes = []
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




@bot.message_handler(commands = ['start'])
def url(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Ссылка на наш сайт', url='https://habr.com/ru/all/')
    bot.send_photo(message.from_user.id, photo=open('2025-10-25 12.50.58.jpg', 'rb'))
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Ну что двоешники, наркоманы, вэйперы? Работать Будем????!", reply_markup = markup)
bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть