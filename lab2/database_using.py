import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

try:
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORT")
    )
    cursor = conn.cursor()
    print("Соединение с базой данных успешно установлено!")

except psycopg2.OperationalError as e:
    print("Не удалось подключиться к базе данных!")
    print("Ошибка:", e)



def save_user(user_id, username, is_toxic):
    cursor.execute("SELECT toxic_count FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    if result:
        if is_toxic:
            new_count = int(result[0] + 1)
            cursor.execute("UPDATE users SET toxic_count = %s WHERE user_id = %s", (new_count, user_id,))
    else:
        toxic_count = 1 if is_toxic else 0
        cursor.execute(
            "INSERT INTO users (user_id, username, toxic_count) VALUES (%s, %s, %s)", (user_id, username, toxic_count,)
        )

    conn.commit()

def log_message(user_id, username, message, is_toxic):
    # Проверяем, существует ли user_id в таблице users
    cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
    user_exists = cursor.fetchone()

    if not user_exists:
        print("Пользователь не найден в таблице users. Сообщение не записано.")
        return

    # Текущая дата и время
    timestamp = datetime.now()

    # Добавляем лог в таблицу message_logs
    cursor.execute(
        "INSERT INTO save_messages(timestamp, user_id, username, message, is_toxic) VALUES (%s, %s, %s, %s, %s)",
        (timestamp, user_id, username, message, is_toxic,)
    )

    # Сохраняем изменения
    conn.commit()
    print("Сообщение успешно добавлено в базу данных.")

def num_toxcom(user_id):
    cursor.execute("SELECT toxic_count FROM users WHERE user_id = %s", (user_id,))
    num_toxic = cursor.fetchone()
    return num_toxic


# Закрытие соединения
def close_connection():
    cursor.close()
    conn.close()