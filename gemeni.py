import requests
import ssl
import json


def get_available_models(api_key):
    """
    Получает список доступных моделей (синхронная версия)
    """
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

    try:
        # Отключаем проверку SSL для избежания ошибок сертификатов
        response = requests.get(url, verify=False)

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

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def gemini_query_smart(api_key, query):
    """
    Умный запрос, который сначала проверяет доступные модели (синхронная версия)
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

    url = f"https://generativelanguage.googleapis.com/v1/models/{model_to_use}:generateContent?key={api_key}"

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": query}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)

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
        return "❌ Таймаут запроса"
    except Exception as e:
        return f"❌ Ошибка: {e}"


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

    # Затем тестируем запрос
    test_response = gemini_query_smart(api_key, "Привет! Ответь одним словом: 'работает'")
    print(f"📝 Тестовый ответ: {test_response}")

    return "работает" in test_response.lower()


# Использование
if __name__ == "__main__":
    API_KEY = "AIzaSyCPMMiv61hM9VDlfdPQJ2tHduJsPi_8tS4"  # Замените на ваш ключ

    # Отключаем SSL предупреждения
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    print("🚀 Запуск синхронной версии Gemini API")
    print("=" * 50)

    # Тестируем подключение
    if test_gemini_connection(API_KEY):
        print("\n🎉 Подключение успешно!")

        # Основной запрос
        while True:
            user_query = input("\n💬 Введите ваш вопрос (или 'выход' для завершения): ")
            if user_query.lower() in ['выход', 'exit', 'quit']:
                break

            if user_query.strip():
                response = gemini_query_smart(API_KEY, user_query)
                print(f"\n🤖 Ответ: {response}")
    else:
        print("\n❌ Не удалось установить соединение с Gemini API")
        print("Проверьте:")
        print("  - Корректность API ключа")
        print("  - Интернет-соединение")
        print("  - Доступ к Google APIs")