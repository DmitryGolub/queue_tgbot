import asyncio
import asyncpg

from config import DB_HOST, DB_PORT, DB_USER, DB_NAME, DB_PASSWORD


# Декоратор для соединения с БД
def connection_to_db(func):
    async def wrapper(*args, **kwargs):
        try:
            connection = await asyncpg.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )

            return await func(connection, *args, **kwargs)
        except Exception as ex:
            print(ex)
        finally:
            await connection.close()
    
    return wrapper


# Создание таблиц
@connection_to_db
async def create_tabels(cursor):
    await cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users (
                   telegram_id BIGINT PRIMARY KEY,
                   name VARCHAR(100) NOT NULL UNIQUE,
                   admin BOOL DEFAULT false
                   );
                   """)
    
    await cursor.execute("""
                   CREATE TABLE IF NOT EXISTS queues (
                   queue_id SERIAL PRIMARY KEY,
                   title VARCHAR(255) NOT NULL,
                   chat_id BIGINT NOT NULL,
                   message_id BIGINT NOT NULL
                   );
                   """)
    
    await cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users_queues (
                   queue_id BIGINT REFERENCES queues(queue_id) ON DELETE CASCADE,
                   telegram_id BIGINT REFERENCES users(telegram_id) ON DELETE CASCADE,
                   time_addition TIMESTAMP
                   );
                   """)


# Запросы к таблице users
@connection_to_db
async def add_user(cursor, telegram_id: int, name: str):
    await cursor.execute(f"""
                   INSERT INTO users (telegram_id, name)
                   VALUES ({telegram_id}, '{name}');
                   """)


@connection_to_db
async def get_user_by_telegram_id(cursor, telegram_id: int) -> dict:
    user = await cursor.fetchrow(f"""
                   SELECT telegram_id, name, admin FROM users
                   WHERE telegram_id = {telegram_id};
                   """)
    if user:
        user = {
            'telegram_id': user['telegram_id'],
            'name': user['name'],
            'admin': user['admin'],
        }

        return user
    else:
        return {}


@connection_to_db
async def set_admin_user(cursor, telegram_id: int):
    await cursor.execute(f"""
                   UPDATE users
                   SET admin = true 
                   WHERE telegram_id = {telegram_id}         
;""")


# Запросы к таблице queue
@connection_to_db
async def add_queue(cursor, title: str, chat_id: int, message_id: int):
    await cursor.execute(f"""
                   INSERT INTO queues (title, chat_id, message_id)
                   VALUES ('{title}', {chat_id}, {message_id});
                   """)


@connection_to_db
async def get_queue_by_chat_message_id(cursor, chat_id: int, message_id: int) -> list[dict]:
    # Отправляем запрос
    queue = await cursor.fetchrow(f"""
                   SELECT queue_id, title, chat_id, message_id FROM queues
                   WHERE chat_id = {chat_id} AND message_id = {message_id}
                   ;
                   """)

    if not queue:
        return []
    else:
        # Формируем результат
        res = {
                'queue_id': queue['queue_id'],
                'title': queue['title'],
                'chat_id': queue['chat_id'],
                'message_id': queue['message_id']
            }
        
        return res
    

@connection_to_db
async def delete_queues_by_chat_message_id(cursor, chat_id: int, message_id: int):
    # Удаляем очереди
    await cursor.execute(f"""
                   DELETE FROM queues
                   WHERE chat_id = {chat_id} AND message_id = {message_id}
                   ;
                   """)


# Запросы к таблице users_queues
@connection_to_db
async def add_user_in_queue(cursor, telegram_id: int, chat_id: int, message_id: int, time_addition: str):
    # Получаем очередь по message_id и chat_id
    
    queue = await cursor.fetchrow(f"""
                   SELECT queue_id FROM queues
                   WHERE chat_id = {chat_id} AND message_id = {message_id}
                   ;
                   """)
    
    # Получем id очереди
    queue_id = queue['queue_id']

    # Добавляем пользователя в очередь
    await cursor.execute(f"""
                   INSERT INTO users_queues (telegram_id, queue_id, time_addition)
                   VALUES ({telegram_id}, {queue_id}, '{time_addition}'
                   );
                   """)


@connection_to_db
async def get_user_in_queue(cursor, telegram_id: int, message_id: int, chat_id: int):
    # Получаем очередь по message_id и chat_id
    queue = await cursor.fetchrow(f"""
                   SELECT queue_id FROM queues
                   WHERE chat_id = {chat_id} AND message_id = {message_id}
                   ;
                   """)
    
    # Получем id очереди
    queue_id = queue['queue_id']

    # Получаем telegram_id и name пользователей
    user = await cursor.fetchrow(f"""
                   SELECT users.telegram_id, users.name FROM users_queues
                   JOIN users ON users.telegram_id = users_queues.telegram_id
                   JOIN queues ON queues.queue_id = users_queues.queue_id
                   WHERE users_queues.queue_id = {queue_id} AND users_queues.telegram_id = {telegram_id}
                   ORDER BY time_addition
                   ;""")
    if user:
        
        # Формируем результат
        res = {
            'telegram_id': user['telegram_id'],
            'name': user['name']
        }
        
        return res
    
    return {}



@connection_to_db
async def get_users_in_queue(cursor, message_id: int, chat_id: int):
    # Получаем очередь по message_id и chat_id
    queue = await cursor.fetchrow(f"""
                   SELECT queue_id FROM queues
                   WHERE chat_id = {chat_id} AND message_id = {message_id}
                   ;
                   """)
    
    # Получем id очереди
    queue_id = queue['queue_id']

    # Получаем telegram_id и name пользователей
    users = await cursor.fetch(f"""
                   SELECT users.telegram_id, users.name FROM users_queues
                   JOIN users ON users.telegram_id = users_queues.telegram_id
                   JOIN queues ON queues.queue_id = users_queues.queue_id
                   WHERE users_queues.queue_id = {queue_id}
                   ORDER BY time_addition
                   ;""")

    # Формируем результат
    res = []

    for user in users:
        res.append({
            'telegram_id': user['telegram_id'],
            'name': user['name'],
        })
    
    return res


@connection_to_db
async def delete_user_from_queue(cursor, telegram_id: int, chat_id: int, message_id: int):
    # Получаем очередь по message_id и chat_id
    queue = await cursor.fetchrow(f"""
                   SELECT queue_id FROM queues
                   WHERE chat_id = {chat_id} AND message_id = {message_id}
                   ;
                   """)
    # Получем id очереди
    queue_id = queue['queue_id']

    await cursor.execute(f"""
                   DELETE FROM users_queues
                   WHERE telegram_id = {telegram_id} AND queue_id = {queue_id}
                   ;
                   """)


if __name__ == "__main__":
    print('OK')
