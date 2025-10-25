import requests
import urllib3
import json
import time

# Отключаем SSL предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
api_key = "AIzaSyCPMMiv61hM9VDlfdPQJ2tHduJsPi_8tS4"

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
            print("📋 Доступные модели:")
            for model in models_data.get('models', []):
                model_name = model['name'].split('/')[-1]
                display_name = model.get('displayName', 'N/A')
                methods = model.get('supportedGenerationMethods', [])
                print(f"  - {model_name} ({display_name})")
                print(f"    Supported methods: {methods}")
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


def gemini_query_smart(api_key, query, timeout=120):
    """
    Умный запрос с увеличенным таймаутом
    """
    print("🔍 Получаю список доступных моделей...")
    models = get_available_models(api_key)

    if not models:
        return "❌ Не удалось получить список моделей"

    # Ищем модели, поддерживающие generateContent
    available_models = []
    for model in models.get('models', []):
        if 'generateContent' in model.get('supportedGenerationMethods', []):
            model_name = model['name'].split('/')[-1]  # Извлекаем короткое имя
            available_models.append(model_name)
            print(f"✅ Найдена подходящая модель: {model_name}")

    if not available_models:
        return "❌ Нет моделей, поддерживающих generateContent"

    # Пробуем первую доступную модель
    model_to_use = available_models[0]
    print(f"🔄 Использую модель: {model_to_use}")
    print(f"⏱️  Таймаут запроса: {timeout} секунд")

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

models = get_available_models(api_key)

def gemini_query_with_retry(api_key, query, max_retries=3, initial_timeout=60, max_timeout=300):
    """
    Запрос с повторными попытками и прогрессивным увеличением таймаута
    """
    for attempt in range(max_retries):
        timeout = min(initial_timeout * (2 ** attempt), max_timeout)  # Экспоненциальный backoff

        print(f"🔄 Попытка {attempt + 1}/{max_retries}, таймаут: {timeout} секунд")

        result = gemini_query_smart(api_key, query, timeout)

        if not result.startswith("❌ Таймаут запроса"):
            return result

        if attempt < max_retries - 1:
            wait_time = 5 * (attempt + 1)
            print(f"⏳ Жду {wait_time} секунд перед повторной попыткой...")
            time.sleep(wait_time)

    return "❌ Все попытки завершились таймаутом"


def test_gemini_connection(api_key):
    """
    Тестирование подключения к Gemini API
    """
    print("🧪 Тестируем подключение к Gemini API...")

    # Сначала получаем список моделей
    models = get_available_models(api_key)
    if not models:
        print("❌ Не удалось подключиться к API")
        return False

    # Затем тестируем запрос с увеличенным таймаутом
    test_response = gemini_query_smart(api_key, "Привет! Ответь одним словом: 'работает'", timeout=60)
    print(f"📝 Тестовый ответ: {test_response}")

    return "работает" in test_response.lower()


# Использование
if __name__ == "__main__":
    API_KEY = api_key  # Замените на ваш ключ

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
    else:
        print("\n❌ Не удалось установить соединение с Gemini API")
        print("Проверьте:")
        print("  - Корректность API ключа")
        print("  - Интернет-соединение")
        print("  - Доступ к Google APIs")