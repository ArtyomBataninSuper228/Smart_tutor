import aiohttp
import asyncio
import ssl
import json


async def get_available_models(api_key: str):
    """
    Получает список доступных моделей
    """
    url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    models_data = await response.json()
                    print("📋 Доступные модели:")
                    for model in models_data.get('models', []):
                        print(f"  - {model['name']} ({model['displayName']})")
                        print(f"    Supported methods: {model.get('supportedGenerationMethods', [])}")
                    return models_data
                else:
                    error = await response.text()
                    print(f"❌ Ошибка получения моделей: {error}")
                    return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


async def gemini_query_smart(api_key: str, query: str):
    """
    Умный запрос, который сначала проверяет доступные модели
    """
    print("🔍 Получаю список доступных моделей...")
    models = await get_available_models(api_key)

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

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('candidates'):
                        return result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return "❌ Пустой ответ"
                else:
                    error = await response.text()
                    return f"❌ Ошибка API: {error}"
    except Exception as e:
        return f"❌ Ошибка: {e}"


# Использование
async def main():
    API_KEY = "my_api_key"

    # Сначала посмотрим доступные модели
    response = await gemini_query_smart(API_KEY, "Привет! Ответь очень коротко.")
    print(f"\n🤖 Ответ: {response}")


if __name__ == "__main__":
    asyncio.run(main())