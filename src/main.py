import asyncio
from datetime import datetime

from aiogram import Dispatcher, Bot, F
from aiogram.types.message import Message
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from utils import validation_on_admin
from database import add_user, get_user_by_telegram_id, add_queue, \
    get_queue_by_chat_message_id, delete_queues_by_chat_message_id, add_user_in_queue, get_users_in_queue, \
    delete_user_from_queue, get_user_in_queue
from config import BOT_TOKEN


dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("""
                         Что я умею
                         /register - регистрация пользователя
                         /admin - стать админом
                         Команды для админа
                         /new_queue - создать новую очередь
                         /delete_queue - удалить очередь""")


@dp.message(Command("set_admin"))
async def set_admin_command(message: Message):
    ...


@dp.message(Command("register"))
async def register_user_command(message: Message):
    # получаем telegram_id
    telegram_id = message.from_user.id

    # получаем текст сообщения
    message_text = message.text

    if len(message_text.split()) > 1: # если есть какой-то текст помимо команды
        name = message_text.split(maxsplit=1)[1]
        
        # проверяем, есть ли такой пользователь в users
        if get_user_by_telegram_id(telegram_id=telegram_id): # если есть, выводим сообщение
            await message.answer("Вы уже зарегистрировались")

        else: # если нет, добавляем
            add_user(telegram_id, name)
            await message.answer("Вы успешно авторизовались")

    else: # если текста нет, возвращаем сообщение об ошибки
        await message.reply("Укажите Имя и Фамилию.\nПример:\n/register Иван Иванов")
    

@dp.message(Command("new_queue"))
async def new_queue_command(message: Message):
    telegram_id = message.from_user.id

    if validation_on_admin(telegram_id):
        # получаем текст сообщения
        message_text = message.text

        if len(message_text.split()) > 1: # если есть какой-то текст помимо команды, создаем очередь
            title = message_text.split(maxsplit=1)[1]

            # Отправляем сообщение с очередью
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="join_to_queue"))
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="quit_from_queue"))
            sent_message = await message.answer(f"{title}", reply_markup=builder.as_markup())

            # Получаем все необходимы данные из отправленного сообщения
            message_id = sent_message.message_id
            chat_id = sent_message.chat.id

            print("Создана очередь", title, message_id, chat_id)
            # Добавляем очередь в таблицу
            add_queue(title, chat_id, message_id)

        else: # если текста нет, возвращаем сообщение об ошибки
            await message.reply("Добавье название очереди.\nПример:\n/new_queue Очередь на лабораторную")
    else:
        await message.answer("Вы не можете использовать эту команду")


@dp.message(Command("delete_queue"))
async def delete_queue_command(message: Message):
    telegram_id = message.from_user.id

    if validation_on_admin(telegram_id): # Проверяем, что это был ответ на сообщение
        if message.reply_to_message:
            # Берем нужные данне из сообщения, на которое ответили
            reply_message_id = message.reply_to_message.message_id
            reply_chat_id = message.reply_to_message.chat.id

            # Проверка, что админ ответил на сообщение с очередью
            if get_queue_by_chat_message_id(message_id=reply_message_id, chat_id=reply_chat_id):
                # Удаляем сообщение с очередью
                await bot.delete_message(chat_id=reply_chat_id, message_id=reply_message_id)
                # Удаляем запись из таблицы очередей
                delete_queues_by_chat_message_id(chat_id=reply_chat_id, message_id=reply_message_id)

            else: # Ответил не на сообщение с очередью
                await message.answer("Нужно ответить на сообщение с очередью")
        else:
            await message.answer("Нужно ответить на сообщение с очередью")
    else:
        await message.answer("Эту команду могут использовать только админы")


@dp.callback_query(F.data == "join_to_queue")
async def join_to_queue_callback(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    
    
    if get_user_by_telegram_id(telegram_id=telegram_id): # Проверяем, что пользователь авторизован
        
        time_addition = datetime.now()

        if get_user_in_queue(telegram_id=telegram_id, message_id=message_id, chat_id=chat_id):
            await callback.answer("Вы уже в очереди")
        else:
            add_user_in_queue(telegram_id=telegram_id, message_id=message_id, chat_id=chat_id, time_addition=time_addition)

            users_in_queue = get_users_in_queue(message_id=message_id, chat_id=chat_id)
            queue = get_queue_by_chat_message_id(message_id=message_id, chat_id=chat_id)
            
            # Обновляем сообщение с очередью
            new_text = f"{queue['title']}\n"

            for user in users_in_queue:
                new_text += f"{user['name']}\n"
            
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="join_to_queue"))
            builder.add(InlineKeyboardButton(text="Выйти из очереди", callback_data="quit_from_queue"))
            
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, reply_markup=builder.as_markup())

            await callback.answer("Вы добавлены в очередь")
    else:
        await callback.answer("Вы не зарегистрированы")


@dp.callback_query(F.data == "quit_from_queue")
async def quit_to_queue_callback(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    if get_user_by_telegram_id(telegram_id=telegram_id): # Проверяем, что пользователь авторизован

        if get_user_in_queue(telegram_id=telegram_id, message_id=message_id, chat_id=chat_id):

            delete_user_from_queue(telegram_id=telegram_id, chat_id=chat_id, message_id=message_id)

            users_in_queue = get_users_in_queue(message_id=message_id, chat_id=chat_id)
            queue = get_queue_by_chat_message_id(message_id=message_id, chat_id=chat_id)
            
            # Обновляем сообщение с очередью
            new_text = f"{queue['title']}\n"

            for user in users_in_queue:
                new_text += f"{user['name']}\n"
            
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="join_to_queue"))
            builder.add(InlineKeyboardButton(text="Выйти из очереди", callback_data="quit_from_queue"))
            
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, reply_markup=builder.as_markup())

            await callback.answer("Вы вышли из очереди")
        
        else:
            await callback.answer("Вас нет в очереди")
    else:
        await callback.answer("Вы не зарегистрированы") 


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
