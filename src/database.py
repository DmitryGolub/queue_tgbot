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


if __name__ == "__main__":
    create_tabels()
    print('OK')
