from json import *

import math
import telebot
from telebot import types
from threading import Thread
import requests
import urllib3
import json
import time
import textwrap

from gemeni import api_key

Students = {}
Teachers = {}

is_run = True


api_key = "AIzaSyCPMMiv61hM9VDlfdPQJ2tHduJsPi_8tS4"






#Обьявление классов
class event():
    def __init__(self, time, type):
        pass
class Teacher():
    def __init__(self, nickname):
        self.classes = []
        self.subjects = []
        self. nickname = nickname
        self.name = ""
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
        self.name = ""
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

#Настройка  нейросети



# Отключаем SSL предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_available_models(api_key):
    """
    Получает список доступных моделей (синхронная версия)
    """
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

    try:
        # Увеличиваем таймаут для получения моделей
        response = requests.get(url, verify=False, timeout=60)

        if response.status_code == 200:
            models_data = response.json()
            #print("📋 Доступные модели:")
            for model in models_data.get('models', []):
                model_name = model['name'].split('/')[-1]
                display_name = model.get('displayName', 'N/A')
                methods = model.get('supportedGenerationMethods', [])
                #print(f"  - {model_name} ({display_name})")
                #print(f"    Supported methods: {methods}")
            return models_data
        else:
            print(f"❌ Ошибка получения моделей: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("❌ Таймаут при получении списка моделей (60 секунд)")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None
models = get_available_models(api_key)
def gemini_query_smart(api_key, query, timeout=120):
    """
    Умный запрос с увеличенным таймаутом
    """
    #print("🔍 Получаю список доступных моделей...")
    #models = get_available_models(api_key)

    if not models:
        raise "❌ Не удалось получить список моделей"

    # Ищем модели, поддерживающие generateContent
    available_models = []
    for model in models.get('models', []):
        if 'generateContent' in model.get('supportedGenerationMethods', []):
            model_name = model['name'].split('/')[-1]  # Извлекаем короткое имя
            available_models.append(model_name)
            #print(f"✅ Найдена подходящая модель: {model_name}")

    if not available_models:
        raise "❌ Нет моделей, поддерживающих generateContent"

    # Пробуем первую доступную модель
    model_to_use = available_models[1]
    print(f"🔄 Использую модель: {model_to_use}")
    #print(f"⏱️  Таймаут запроса: {timeout} секунд")

    url = f"https://generativelanguage.googleapis.com/v1/models/{model_to_use}:generateContent?key={api_key}"

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": query}]
        }]
    }

    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=timeout)
        end_time = time.time()

        #print(f"⏱️  Время выполнения запроса: {end_time - start_time:.2f} секунд")

        if response.status_code == 200:
            result = response.json()
            if result.get('candidates'):
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                return "❌ Пустой ответ от модели"
        else:
            error_text = response.text
            return f"❌ Ошибка API ({response.status_code}): {error_text}"

    except requests.exceptions.Timeout:
        return f"❌ Таймаут запроса ({timeout} секунд)"
    except requests.exceptions.ConnectionError:
        return "❌ Ошибка соединения"
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка запроса: {e}"
    except Exception as e:
        return f"❌ Неожиданная ошибка: {e}"


def gemini_query_with_retry(api_key, query, max_retries=3, initial_timeout=60, max_timeout=300):
    """
    Запрос с повторными попытками и прогрессивным увеличением таймаута
    """
    for attempt in range(max_retries):
        timeout = min(initial_timeout * (2 ** attempt), max_timeout)  # Экспоненциальный backoff

        #print(f"🔄 Попытка {attempt + 1}/{max_retries}, таймаут: {timeout} секунд")

        result = gemini_query_smart(api_key, query, timeout)

        if not result.startswith("❌ Таймаут запроса"):
            return result

        if attempt < max_retries - 1:
            wait_time = 5 * (attempt + 1)
            #print(f"⏳ Жду {wait_time} секунд перед повторной попыткой...")
            time.sleep(wait_time)

    raise "❌ Все попытки завершились таймаутом"


def test_gemini_connection(api_key):
    """
    Тестирование подключения к Gemini API
    """
    print("🧪 Тестируем подключение к Gemini API...")

    # Сначала получаем список моделей
    #models = get_available_models(api_key)
    if not models:
        print("❌ Не удалось подключиться к API")
        return False

    # Затем тестируем запрос с увеличенным таймаутом
    test_response = gemini_query_smart(api_key, "Привет! Ответь одним словом: 'работает'", timeout=60)
    print(f"📝 Тестовый ответ: {test_response}")

    return "работает" in test_response.lower()

'''
# Использование
if __name__ == "__main__":
    API_KEY = api_key # Замените на ваш ключ

    print("🚀 Запуск синхронной версии Gemini API с увеличенным таймаутом")
    print("=" * 60)

    # Тестируем подключение
    if test_gemini_connection(API_KEY):
        print("\n🎉 Подключение успешно!")

        # Основной запрос
        while True:
            user_query = input("\n💬 Введите ваш вопрос (или 'выход' для завершения): ")
            if user_query.lower() in ['выход', 'exit', 'quit']:
                break

            if user_query.strip():
                print("⏳ Обрабатываю запрос...")
                # Используем версию с повторными попытками
                response = gemini_query_with_retry(
                    API_KEY,
                    user_query,
                    max_retries=3,
                    initial_timeout=300,
                    max_timeout=3000  # 5 минут максимальный таймаут
                )
                print(f"\n🤖 Ответ: {response}")
    #else:
    #    print("\n❌ Не удалось установить соединение с Gemini API")
    #    print("Проверьте:")
    #    print("  - Корректность API ключа")
    #    print("  - Интернет-соединение")
    #    print("  - Доступ к Google APIs")
'''


#Настройка бота
bot = telebot.TeleBot('8215300847:AAHGW-KR6aJhm2uJgBtzdNJAYm093KwjVH0')
print("started")
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Регистрация как Ученик")
    btn2 = types.KeyboardButton("Регистрация как Учитель")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text="Здравствуйте, вы ещё не зарегестрированы в системе".format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):
    print(message.text)
    if(message.text == "Регистрация как Ученик"):
        if message.from_user.id  in Students or message.from_user.id in Teachers.keys():
            bot.send_message(message.chat.id, text="Вы  уже зарагестрированы")
            return
        student = Student(message.from_user.id)
        bot.send_message(message.chat.id, text="Вы зарегестрированы")

    elif(message.text == "Регистрация как Учитель"):
        if message.from_user.id in Students or message.from_user.id in Teachers.keys():
            bot.send_message(message.chat.id, text="Вы  уже зарагестрированы")
            return
        teacher = Teacher(message.from_user.id)
        bot.send_message(message.chat.id, text="Вы зарегестрированы")

    else:
            response = gemini_query_with_retry(
            api_key,
            message.text,
            max_retries=3,
            initial_timeout=300,
            max_timeout=3000  # 5 минут максимальный таймаут
            )

            for i in textwrap.wrap(response, 10000):
                bot.send_message(message.chat.id, i)








    """
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Ссылка на наш сайт', url='https://habr.com/ru/all/')
    bot.send_photo(message.from_user.id, photo=open('2025-10-25 12.50.58.jpg', 'rb'))
    markup.add(btn1)
    print(message.from_user.id)
    bot.send_message(message.from_user.id, "Ну что двоешники, наркоманы, вэйперы? Работать Будем????!", reply_markup = markup)
    """
print("start_polling")
bot.polling(none_stop=True, interval=1) #обязательная для работы бота часть