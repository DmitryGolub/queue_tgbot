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


            cursor.execute("""
                           CREATE TABLE users (
                           telegram_id INTEGER PRIMARY KEY,
                           username VARCHAR(255) NOT NULL,
                           name VARCHAR(255) NOT NULL
                           );
                           """)
            
            cursor.execute("""CREATE TABLE notice (
                           telegram_id INTEGER NOT NULL,
                           message_id INTEGER NOT NULL,
                           FOREIGN KEY (telegram_id) REFERENCES users(telegram_id),
                           PRIMARY KEY (telegram_id, message_id)
                           );
                           """)

            return func(cursor, *args, **kwargs)
        except Exception as ex:
            print(ex)
        finally:
            cursor.close()
            connection.commit()
            connection.close()
    
    return wrapper


@connection_to_db
def test():
    print("OK")
    