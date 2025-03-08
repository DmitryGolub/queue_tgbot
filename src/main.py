import asyncio
from datetime import datetime

from aiogram import Dispatcher, Bot, F
from aiogram.types.message import Message
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from utils import validation_on_admin
from database import add_user, get_user_by_telegram_id, add_queue, \
    get_queue_by_chat_message_id, delete_queues_by_chat_message_id, add_user_in_queue, get_users_in_queue, \
    delete_user_from_queue, get_user_in_queue, set_admin_user
from config import BOT_TOKEN, SECRET_ADMIN_KEY


dp = Dispatcher()
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Что я умею\n/register - регистрация пользователя\n/admin - стать админом\nКоманды для админа\n/new_queue - создать новую очередь\n/delete_queue - удалить очередь")


@dp.message(Command("admin"))
async def set_admin_command(message: Message):
    telegram_id = message.from_user.id

    if await get_user_by_telegram_id(telegram_id=telegram_id): # проверка на регистрацию

        # получаем текст сообщения
        message_text = message.text

        if len(message_text.split()) > 1: # если есть какой-то текст помимо команды
            text = message_text.split(maxsplit=1)[1]
            if text == SECRET_ADMIN_KEY:
                await set_admin_user(telegram_id=telegram_id)
                await message.answer("Теперь вы админ")
            else:
                await message.answer("Хорошая попытка")

        else:
            await message.answer("Нужно указать секретный ключ\nПример: \n/admin secret_key")

    else:
        await message.answer("Для начала нужно зарегистрироваться")


@dp.message(Command("register"))
async def register_user_command(message: Message):
    # получаем telegram_id
    telegram_id = message.from_user.id

    # получаем текст сообщения
    message_text = message.text

    if len(message_text.split()) > 1: # если есть какой-то текст помимо команды
        name = message_text.split(maxsplit=1)[1]
        
        # проверяем, есть ли такой пользователь в users
        if await get_user_by_telegram_id(telegram_id=telegram_id): # если есть, выводим сообщение
            await message.answer("Вы уже зарегистрировались")

        else: # если нет, добавляем
            await add_user(telegram_id, name)
            await message.answer("Вы успешно авторизовались")

    else: # если текста нет, возвращаем сообщение об ошибки
        await message.reply("Укажите Имя и Фамилию.\nПример:\n/register Иван Иванов")
    

@dp.message(Command("new_queue"))
async def new_queue_command(message: Message):
    telegram_id = message.from_user.id

    if await get_user_by_telegram_id(telegram_id=telegram_id) and await validation_on_admin(telegram_id):
        # получаем текст сообщения
        message_text = message.text

        if len(message_text.split()) > 1: # если есть какой-то текст помимо команды, создаем очередь
            title = message_text.split(maxsplit=1)[1]

            # Отправляем сообщение с очередью
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="join_to_queue"))
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="quit_from_queue"))
            builder.adjust(1)
            sent_message = await message.answer(f"<b>{title}</b>", reply_markup=builder.as_markup())
            # Получаем все необходимы данные из отправленного сообщения
            message_id = sent_message.message_id
            chat_id = sent_message.chat.id

            print("Создана очередь", title, message_id, chat_id)
            # Добавляем очередь в таблицу
            await add_queue(title, chat_id, message_id)

        else: # если текста нет, возвращаем сообщение об ошибки
            await message.reply("Добавье название очереди.\nПример:\n/new_queue Очередь на лабораторную")
    else:
        await message.answer("Эту команду могут использовать только админы")


@dp.message(Command("delete_queue"))
async def delete_queue_command(message: Message):
    telegram_id = message.from_user.id

    if await get_user_by_telegram_id(telegram_id=telegram_id) and await validation_on_admin(telegram_id): # Валидация на админа
        if message.reply_to_message: # Проверяем, что это был ответ на сообщение
            # Берем нужные данне из сообщения, на которое ответили
            reply_message_id = message.reply_to_message.message_id
            reply_chat_id = message.reply_to_message.chat.id

            # Проверка, что админ ответил на сообщение с очередью
            if await get_queue_by_chat_message_id(message_id=reply_message_id, chat_id=reply_chat_id):
                # Удаляем сообщение с очередью
                await bot.delete_message(chat_id=reply_chat_id, message_id=reply_message_id)
                # Удаляем запись из таблицы очередей
                await delete_queues_by_chat_message_id(chat_id=reply_chat_id, message_id=reply_message_id)

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
    
    
    if await get_user_by_telegram_id(telegram_id=telegram_id): # Проверяем, что пользователь авторизован
        
        time_addition = datetime.now()

        if await get_user_in_queue(telegram_id=telegram_id, message_id=message_id, chat_id=chat_id):
            await callback.answer("Вы уже в очереди")
        else:
            await add_user_in_queue(telegram_id=telegram_id, message_id=message_id, chat_id=chat_id, time_addition=time_addition)

            users_in_queue = await get_users_in_queue(message_id=message_id, chat_id=chat_id)
            queue = await get_queue_by_chat_message_id(message_id=message_id, chat_id=chat_id)
            
            # Обновляем сообщение с очередью
            new_text = f"<b>{queue['title']}</b>\n"

            for index, user in enumerate(users_in_queue):
                new_text += f"{index + 1}. {user['name']}\n"
            
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="join_to_queue"))
            builder.add(InlineKeyboardButton(text="Выйти из очереди", callback_data="quit_from_queue"))
            builder.adjust(1)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text, reply_markup=builder.as_markup())

            await callback.answer("Вы добавлены в очередь")
    else:
        await callback.answer("Вы не зарегистрированы")


@dp.callback_query(F.data == "quit_from_queue")
async def quit_to_queue_callback(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id

    if await get_user_by_telegram_id(telegram_id=telegram_id): # Проверяем, что пользователь авторизован

        if await get_user_in_queue(telegram_id=telegram_id, message_id=message_id, chat_id=chat_id):

            await delete_user_from_queue(telegram_id=telegram_id, chat_id=chat_id, message_id=message_id)

            users_in_queue = await get_users_in_queue(message_id=message_id, chat_id=chat_id)
            queue = await get_queue_by_chat_message_id(message_id=message_id, chat_id=chat_id)
            
            # Обновляем сообщение с очередью
            new_text = f"<b>{queue['title']}\n</b>"

            for index, user in enumerate(users_in_queue):
                new_text += f"{index + 1}. {user['name']}\n"
            
            builder = InlineKeyboardBuilder()
            builder.add(InlineKeyboardButton(text="Добавиться в очередь", callback_data="join_to_queue"))
            builder.add(InlineKeyboardButton(text="Выйти из очереди", callback_data="quit_from_queue"))
            builder.adjust(1)

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
