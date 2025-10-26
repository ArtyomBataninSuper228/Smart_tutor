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
Classes = {}
subjects = [
    "Математика",
    "Алгебра",
    "Геометрия",
    "Вероятность и статистика",
    "Русский язык",
    "Литература",
    "История",
    "Обществознание",
    "ОБЖ",
    "Труды",
    "Технология",
    "География",
    "Английский язык",
    "Немецкий язык",
    "Физика",
    "Химия",
    "Музыка",
    "Химия",
    "ОДНКНР",
    "Биология",
]

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
            time.sleep(1)

def open_teachers_data(filename= "students.json"):
        file = open(filename, "rb")
        data = loads(file.read().decode("utf-8"))
        for i in data.keys():
            teacher = Teacher(i)
            teacher.fromJSON(data[i])
        file.close()

class Class():
    def __init__(self, form):
        self.Themes = themes[str(form)]
        self.teachers = []
        self.form = form
        self.students_ids = []
    def toJSON(self):
            return dumps(self.__dict__)

    def fromJSON(self, json_data):
            self.__dict__.update(loads(json_data))

def save_classes_data(filename="classes.json"):
        global is_run
        while is_run:
            file = open(filename, "wb")
            data = {}
            for i in Classes.keys():
                data[i] = Classes[i].toJSON()
            file.write(bytes(dumps(data), "utf-8"))
            file.close()
            time.sleep(1)


def open_classes_data(filename="classes.json"):
    file = open(filename, "rb")
    data = loads(file.read().decode("utf-8"))
    for i in data.keys():
        cls = Class(i)
        cls.from_json(data[i])
    file.close()

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
        self.test = ""
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
            time.sleep(1)

def open_students_data(filename= "students.json"):
        file = open(filename, "rb")
        data = loads(file.read().decode("utf-8"))
        for i in data.keys():
            student = Student(i)
            student.fromJSON(data[i])
        file.close()

#Загрузка данных
file = open('themes.json', 'r')
themes = load(file)
file.close()
open_classes_data()
open_teachers_data()
open_students_data()
t1 = Thread(target=save_teachers_data)
t2 = Thread(target=save_students_data)
t3 = Thread(target=save_classes_data)
t1.start()
t2.start()
t3.start()

#Настройка  нейросети

import re
from telegram import Update
from telegram.ext import ContextTypes


class MessageSplitter:
    MAX_LENGTH = 4096  # Максимальная длина сообщения в Telegram

    @staticmethod
    def split_message(text, parse_mode='HTML'):
        """
        Разбивает длинное сообщение на части с сохранением форматирования
        """
        if len(text) <= MessageSplitter.MAX_LENGTH:
            return [text]

        if parse_mode == 'HTML':
            return MessageSplitter._split_html(text)
        elif parse_mode == 'MarkdownV2':
            return MessageSplitter._split_markdown(text)
        else:
            return MessageSplitter._split_plain(text)

    @staticmethod
    def _split_plain(text):
        """Разбивка простого текста"""
        parts = []
        while text:
            if len(text) <= MessageSplitter.MAX_LENGTH:
                parts.append(text)
                break

            # Ищем место для разрыва (последний перенос строки или пробел)
            split_index = text.rfind('\n', 0, MessageSplitter.MAX_LENGTH)
            if split_index == -1:
                split_index = text.rfind(' ', 0, MessageSplitter.MAX_LENGTH)
            if split_index == -1:
                split_index = MessageSplitter.MAX_LENGTH

            parts.append(text[:split_index])
            text = text[split_index:].lstrip()

        return parts

    @staticmethod
    def _split_html(text):
        """Разбивка HTML текста с сохранением тегов"""
        parts = []

        # Регулярное выражение для поиска HTML тегов
        tag_pattern = re.compile(r'<(/?)([a-zA-Z][^>]*)>')
        tags_stack = []

        current_part = ""
        pos = 0

        while pos < len(text):
            # Определяем, сколько символов можно добавить
            remaining_chars = MessageSplitter.MAX_LENGTH - len(current_part)

            if remaining_chars <= 0:
                # Закрываем все открытые теги в текущей части
                closing_tags = ''.join(f'</{tag}>' for tag in reversed(tags_stack))
                current_part += closing_tags
                parts.append(current_part)

                # Открываем теги для следующей части
                opening_tags = ''.join(f'<{tag}>' for tag in tags_stack)
                current_part = opening_tags
                remaining_chars = MessageSplitter.MAX_LENGTH - len(current_part)

            # Ищем следующий тег
            match = tag_pattern.search(text, pos)
            if match and match.start() - pos <= remaining_chars:
                # Добавляем текст до тега
                if match.start() > pos:
                    chunk = text[pos:match.start()]
                    if len(chunk) > remaining_chars:
                        chunk = chunk[:remaining_chars]
                    current_part += chunk
                    pos += len(chunk)
                    remaining_chars -= len(chunk)
                    continue

                # Обрабатываем тег
                tag = match.group(0)
                is_closing = match.group(1) == '/'
                tag_name = match.group(2).split()[0]  # Берем только имя тега без атрибутов

                if is_closing:
                    # Закрывающий тег - удаляем из стека
                    if tags_stack and tags_stack[-1] == tag_name:
                        tags_stack.pop()
                else:
                    # Открывающий тег - добавляем в стек
                    tags_stack.append(tag_name)

                current_part += tag
                pos = match.end()
            else:
                # Добавляем обычный текст
                end_pos = min(pos + remaining_chars, len(text))
                chunk = text[pos:end_pos]

                # Ищем хорошее место для разрыва
                if end_pos < len(text):
                    # Ищем последний перенос строки или пробел
                    break_pos = chunk.rfind('\n')
                    if break_pos == -1:
                        break_pos = chunk.rfind(' ')
                    if break_pos != -1:
                        chunk = chunk[:break_pos + 1]
                        end_pos = pos + break_pos + 1

                current_part += chunk
                pos = end_pos

        # Добавляем последнюю часть
        if current_part:
            # Закрываем все открытые теги
            closing_tags = ''.join(f'</{tag}>' for tag in reversed(tags_stack))
            current_part += closing_tags
            parts.append(current_part)

        return parts

    @staticmethod
    def _split_markdown(text):
        """Разбивка Markdown текста"""
        # Упрощенная версия для Markdown
        return MessageSplitter._split_plain(text)


# Использование в боте
async def send_long_message(update: Update, context: ContextTypes.DEFAULT_TYPE, long_text, parse_mode='HTML'):
    """
    Отправляет длинное сообщение частями
    """
    splitter = MessageSplitter()
    parts = splitter.split_message(long_text, parse_mode)

    for i, part in enumerate(parts):
        try:
            if i == 0:
                # Первая часть
                await update.message.reply_text(part, parse_mode=parse_mode)
            else:
                # Последующие части
                await update.message.reply_text(part, parse_mode=parse_mode)

            # Небольшая задержка между сообщениями
            import asyncio
            await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Ошибка при отправке части {i}: {e}")
            # Пробуем отправить как простой текст
            await update.message.reply_text(f"Часть {i + 1}:\n{part}")

# Отключаем SSL предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TUTOR_INSTRUCTION = (
    "Ты — интеллектуальный тьютор и репетитор для школьников 12–17 лет. "
    "Твоя задача — помогать ученикам понимать школьные предметы, готовиться к проектам, объяснять материал простыми словами. "
    "Будь дружелюбным, терпеливым и доброжелательным. "
    "Говори по-русски, как настоящий наставник, адаптируй объяснения под возраст ученика, "
    "мотивируй к обучению и помогай логически рассуждать. "
    "Не используй слишком сложные формулировки — твой стиль должен быть понятным, живым и увлекательным. "
    "Помогай ему шаг за шагом, поясняй идеи, исправляй ошибки и предлагай улучшения."
)

def get_available_models(api_key, TUTOR_INSTRUCTION):
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
models = get_available_models(api_key, TUTOR_INSTRUCTION)
def gemini_query_smart(api_key, query, system_instruction, timeout=120):
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
    url = f"https://generativelanguage.googleapis.com/v1/models/{model_to_use}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    # 💬 Псевдо system instruction — как первая подсказка модели
    contents = []
    if system_instruction:
        contents.append({
            "role": "user",
            "parts": [{"text": f"[ИНСТРУКЦИЯ ДЛЯ МОДЕЛИ]\n{system_instruction}"}]
        })

    contents.append({
        "role": "user",
        "parts": [{"text": query}]
    })

    data = {"contents": contents}

    try:
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=timeout)
        end_time = time.time()
        print(f"⏱️  Время выполнения запроса: {end_time - start_time:.2f} секунд")

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


def gemini_query_with_retry(api_key, query, system_instruction, max_retries=3, initial_timeout=60,  max_timeout=300):
    """
    Запрос с повторными попытками и прогрессивным увеличением таймаута
    """
    for attempt in range(max_retries):
        timeout = min(initial_timeout * (2 ** attempt), max_timeout)  # Экспоненциальный backoff

        #print(f"🔄 Попытка {attempt + 1}/{max_retries}, таймаут: {timeout} секунд")

        result = gemini_query_smart(api_key, query, system_instruction, timeout )

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
    if message.from_user.id not in Students.keys() and message.from_user.id not in Teachers.keys():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Регистрация как Ученик")
        btn2 = types.KeyboardButton("Регистрация как Учитель")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, text="Здравствуйте, вы ещё не зарегестрированы в системе".format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):

    if(message.text == "Регистрация как Ученик"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if message.from_user.id  in Students or message.from_user.id in Teachers.keys():
            bot.send_message(message.chat.id, text="Вы  уже зарагестрированы")
            return
        student = Student(message.from_user.id)

        for i in range(5, 12):
            btn1 = types.KeyboardButton(f"{i} класс")
            markup.add(btn1)
        bot.send_message(message.chat.id, text="Укажите ваш класс", reply_markup=markup)
        #bot.send_message(message.chat.id, text="Вы зарегестрированы")

    elif(message.text == "Регистрация как Учитель"):
        if message.from_user.id in Students or message.from_user.id in Teachers.keys():
            bot.send_message(message.chat.id, text="Вы  уже зарагестрированы")
            return
        markup = types.ReplyKeyboardMarkup(resize_keyboard=False)
        teacher = Teacher(message.from_user.id)
        for i in subjects:
            btn1 = types.KeyboardButton(f"{i}")
            markup.add(btn1)
        bot.send_message(message.chat.id, "Напишите, какие предметы вы преподаёте", reply_markup=markup)

    elif  len(message.text.split()) > 1 and message.text.split()[1] == "класс":
        try:
            if int(message.text.split()[0]) > 4 and int(message.text.split()[0]) < 12:
                Students[message.from_user.id].form = int(message.text.split()[0])
                student = Students[message.from_user.id]
                print(student.form)
                INSTRUCTION = (
                    f"Ты — интеллектуальный тьютор и репетитор для школьника {student.form} класса. "
                    "Твоя задача — помогать ученикам понимать школьные предметы, готовиться к проектам, объяснять материал простыми словами. "
                    "Будь дружелюбным, терпеливым и доброжелательным. "
                    "Говори по-русски, как настоящий наставник, адаптируй объяснения под возраст ученика, "
                    "мотивируй к обучению и помогай логически рассуждать. "
                    "Не используй слишком сложные формулировки — твой стиль должен быть понятным, живым и увлекательным. "
                    "Помогай ему шаг за шагом, поясняй идеи, исправляй ошибки и предлагай улучшения."
                )
                message_text = """Создай тест для оценки способностей и знаний ученика
                Нужно что бы ученик оформил ответ следующим образом:
                Тестирование: (Ответы на вопросы)
                Важно что бы его ответ начинался с последовательности "Тестирование:" что бы система распознала ответ
                """
                response = gemini_query_with_retry(
                    api_key,
                    message_text,
                    max_retries=3,
                    system_instruction=INSTRUCTION,
                    initial_timeout=300,
                    max_timeout=3000  # 50 минут максимальный таймаут
                )
                student.test = response
                bot.send_message(message.chat.id, text=response)


            else:
                bot.send_message(message.chat.id, text="Неверный класс")
        except ZeroDivisionError:
            bot.send_message(message.chat.id, text="Неверный класс")
    elif message.text in subjects:
        if message.from_user.id in Teachers.keys():
            teacher = Teacher(message.from_user.id)
            teacher.subjects.append(message.text)
        else:
            bot.send_message(message.chat.id, text="Вы не зарегистрированы как учитель")

    elif "Тестирование:" in message.text:
        student = Students[message.from_user.id]
        INSTRUCTION = (
            f"Ты — интеллектуальный тьютор и репетитор для школьника {student.form} класса. "
            "Твоя задача — помогать ученикам понимать школьные предметы, готовиться к проектам, объяснять материал простыми словами. "
            "Будь дружелюбным, терпеливым и доброжелательным. "
            "Говори по-русски, как настоящий наставник, адаптируй объяснения под возраст ученика, "
            "мотивируй к обучению и помогай логически рассуждать. "
            "Не используй слишком сложные формулировки — твой стиль должен быть понятным, живым и увлекательным. "
            "Помогай ему шаг за шагом, поясняй идеи, исправляй ошибки и предлагай улучшения."
        )
        message_text = f"""
        Ученик написал тест для оценки его способностей. Напиши для учителя и родителей ученика  краткий вывод о его знаниях и способностях ученика, перспективах его обучения и направленностях. Текст теста: "{student.test}"
        ответ ученика: "{message.text}"
                        """
        response = gemini_query_with_retry(
            api_key,
            message_text,
            max_retries=3,
            system_instruction=INSTRUCTION,
            initial_timeout=600,
            max_timeout=3000  # 50 минут максимальный таймаут
        )
        student.test = response
        print(response)

        message_text = f"""
                Ученик написал тест для оценки его способностей. Напиши ответ ученику, что бы поддержать его. Текст теста: "{student.test}"
                ответ ученика: "{message.text}"
                                """
        response = gemini_query_with_retry(
            api_key,
            message_text,
            max_retries=3,
            system_instruction=INSTRUCTION,
            initial_timeout=600,
            max_timeout=3000  # 50 минут максимальный таймаут
        )
        splitter = MessageSplitter()
        parts = splitter.split_message(response, "HTML")
        for i in parts:
            bot.send_message(message.chat.id, i)
    elif message.text == "delete":
        Students.pop(message.from_user.id)





    else:
        if message.from_user.id in Students.keys():
            student = Students[message.from_user.id]

            INSTRUCTION = (

            f"Ты — интеллектуальный тьютор и репетитор для школьника {student.form} класса. "
            "Твоя задача — помогать ученикам понимать школьные предметы, готовиться к проектам, объяснять материал простыми словами. "
            "Будь дружелюбным, терпеливым и доброжелательным. "
            "Говори по-русски, как настоящий наставник, адаптируй объяснения под возраст ученика, "
            "мотивируй к обучению и помогай логически рассуждать. "
            "Не используй слишком сложные формулировки — твой стиль должен быть понятным, живым и увлекательным. "
            "Помогай ему шаг за шагом, поясняй идеи, исправляй ошибки и предлагай улучшения."
            f"Результат прохождения тестирования учеником: {student.test}"

            )
        elif message.from_user.id in Teachers.keys():
            teacher = Teachers[message.from_user.id]
            st = ""
            for i in teacher.subjects:
                st += i
            INSTRUCTION = f"""
            Ты - интеллектуальный помошник для учителя, твоя задача разгрузить учителя, помочь с составлением домашнего задания,
            с анализом статистики по успеваемости учеников.
            Учитель преподаёт следующие предметы: {st}
            Задания для контрольных и домашних работ необходимо брать из источников, одобренных ФГОС.
            Задания необходимо оформлять понятным для детей языком в удобном формате
            """
        else:
            bot.send_message(message.chat.id, " Вы не зарегестрированы", parse_mode='HTML')
            return


        response = gemini_query_with_retry(
            api_key,
            message.text,
            max_retries=3,
            system_instruction=INSTRUCTION,
            initial_timeout=300,
            max_timeout=3000  # 5 минут максимальный таймаут
            )
        splitter = MessageSplitter()
        parts = splitter.split_message(response, "HTML")
        for i in parts:
            bot.send_message(message.chat.id, i)
        sm = 0









    """
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Ссылка на наш сайт', url='https://habr.com/ru/all/')
    bot.send_photo(message.from_user.id, photo=open('2025-10-25 12.50.58.jpg', 'rb'))
    markup.add(btn1)
    print(message.from_user.id)
    bot.send_message(message.from_user.id, "Ну что двоешники, наркоманы, вэйперы? Работать Будем????!", reply_markup = markup)
    """
print("start_polling")
while 1:
    try:
        bot.polling(none_stop=True, interval=1) #обязательная для работы бота часть
    except Exception as e:
        pass