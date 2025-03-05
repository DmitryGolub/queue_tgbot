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
                           CREATE TABLE IF NOT EXISTS users (
                           telegram_id BIGINT PRIMARY KEY,
                           name VARCHAR(255) NOT NULL
                           );
                           """)
            
            cursor.execute("""CREATE TABLE IF NOT EXISTS notices (
                           telegram_id BIGINT PRIMARY KEY,
                           message_id INTEGER NOT NULL
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
def add_user(cursor, telegram_id, name) -> None:
    cursor.execute(f"""SELECT * FROM users WHERE telegram_id = {telegram_id};""")
    if not cursor.fetchall():
        cursor.execute(f"""
                    INSERT INTO users (telegram_id, name)
                    VALUES ({telegram_id}, '{name}');
                    """)
        return f"Вы успешно авторизовались, {name}"
    
    else:
        return "Пользователь уже существует"


@connection_to_db
def get_users(cursor) -> list:
    cursor.execute(f"""SELECT telegram_id, name FROM users;""")

    data = cursor.fetchall()

    res = []

    for item in data:
        res.append({
            'telegram_id': item[0],
            'name': item[1]
        })


    return res


@connection_to_db
def add_notice(cursor, telegram_id, message_id) -> None:
    cursor.execute(f"""SELECT * FROM notices WHERE telegram_id = {telegram_id}""")
    if not cursor.fetchall():
        cursor.execute(f"""INSERT INTO notices (telegram_id, message_id)
                    VALUES ({telegram_id}, '{message_id}');""")
        return "Вы добавлены в очередь"
    else:
        return "Вы уже в очереди"


@connection_to_db
def get_notices(cursor) -> None:
    cursor.execute("""SELECT telegram_id, message_id FROM notices;""")
    data = cursor.fetchall()

    res = []

    for item in data:
        res.append({
            'telegram_id': item[0],
            'message_id': item[1]
        })


    return str(res)


@connection_to_db
def delete_notices(cursor) -> None:
    cursor.execute("""DELETE FROM notices;""")
