import requests
import json

# Конфигурация
API_KEY = "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"  # Замените на ваш реальный API ключ
MODEL = "deepseek/deepseek-chat-v3.1:free"

def chat_with_deepseek():
    print("=== DeepSeek Chat ===")
    print("Введите ваш вопрос (или 'выход' для завершения)")

    while True:
        prompt = input("\nВы: ").strip()

        if prompt.lower() in ['выход', 'exit', 'quit']:
            break

        if not prompt:
            continue

        # Отправка запроса
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        if response.status_code == 200:
            answer = response.json()['choices'][0]['message']['content']
            print(f"\nDeepSeek: {answer}")
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")


if __name__ == "__main__":
    chat_with_deepseek()