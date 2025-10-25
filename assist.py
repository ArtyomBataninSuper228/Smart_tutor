# Простой тест OpenAI API (новая версия SDK, >=1.0)
# Установка: pip install openai

from openai import OpenAI

# ======= ВСТАВЬ СВОЙ КЛЮЧ СЮДА (только для теста!) =======
API_KEY = "KEY"
# ==========================================================

client = OpenAI(api_key=API_KEY)

def main():
    print("Тестовый чат с OpenAI. Введи 'exit' или 'выход' для завершения.")

    while True:
        user_input = input("Ты: ").strip()
        if user_input.lower() in ["exit", "выход", "quit"]:
            print("Выход.")
            break

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # можно заменить на gpt-4o или gpt-3.5-turbo
                messages=[{"role": "user", "content": user_input}],
            )

            answer = response.choices[0].message.content
            print("\nБот:", answer, "\n")

        except Exception as e:
            print(f"Ошибка: {e}\n")

if __name__ == "__main__":
    main()