import asyncio
import psycopg2

from config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASSWORD


def connection_to_db(func):
    def wrapper(*args, **kwargs):
        try:
            connection = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )

            cursor = connection.cursor()

            return func(cursor, *args, **kwargs)
        except Exception as ex:
            print(ex)
        finally:
            cursor.close()
            connection.commit()
            connection.close()
    
    return wrapper


# Создание таблиц
@connection_to_db
def create_tabels(cursor):
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                   telegram_id BIGINT PRIMARY KEY,
                   name VARCHAR(100) NOT NULL UNIQUE,
                   admin BOOL DEFAULT false
                   );
                   """)
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS queues (
                   queue_id SERIAL PRIMARY KEY,
                   title VARCHAR(255) NOT NULL,
                   chat_id BIGINT NOT NULL,
                   message_id BIGINT NOT NULL
                   );
                   """)
    
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users_queues (
                   queue_id BIGINT REFERENCES queues(queue_id) ON DELETE CASCADE,
                   telegram_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
                   time_addition TIMESTAMP
                   );
                   """)


# Запросы к таблице users
@connection_to_db
def add_user(cursor, telegram_id: int, name: str):
    cursor.execute(f"""
                   INSERT INTO users (telegram_id, name)
                   VALUES ({telegram_id}, '{name}');
                   """)


@connection_to_db
def get_user_by_telegram_id(cursor, telegram_id: int) -> tuple:
    cursor.execute(f"""
                   SELECT * FROM users
                   WHERE telegram_id = {telegram_id};
                   """)
    
    user = cursor.fetchone()

    return user


# Запросы к таблице queue
@connection_to_db
def add_queue(cursor, title: str, chat_id: int, message_id: int):
    cursor.execute(f"""
                   INSERT INTO queues (title, chat_id, message_id)
                   VALUES ('{title}', {chat_id}, {message_id});
                   """)


@connection_to_db
def get_queues_by_chat_message_id(cursor, chat_id: int, message_id: int) -> list[dict]:
    # Отправляем запрос
    cursor.execute(f"""
                   SELECT queue_id, title, chat_id, message_id FROM queues
                   WHERE chat_id = {chat_id} AND message_id = {message_id}
                   ;
                   """)
    
    queues = cursor.fetchall()

    # Формируем результат
    res = []

    for queue in queues:
        res.append({
            'queue_id': queue[0],
            'title': queue[1],
            'chat_id': queue[2],
            'message_id': queue[3]
        })
    
    return res
    

@connection_to_db
def delete_queues_by_chat_message_id(cursor, chat_id: int, message_id: int):
    # Удаляем очереди
    cursor.execute(f"""
                   DELETE FROM queues
                   WHERE chat_id = {chat_id} AND message_id = {message_id}
                   ;
                   """)


if __name__ == "__main__":
    print('OK')
