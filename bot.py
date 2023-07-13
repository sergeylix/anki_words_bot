import time
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher.filters import Text
from sqlite import db_start, add_access, get_users_w_access, create_profile, insert_words, select_words, delete_word, cards, update_remind_date, words_num

logging.basicConfig(level=logging.INFO)

# Для работы с переменными окружения
load_dotenv()
TOKEN = os.getenv('TOKEN')

MSG = """Давай запоминать перевод слов.\n
Напиши слово, потом знак равно '=', и затем перевод. И я сохраню слово в твоей базе слов.
Например: hello = привет"""
MSG_HELP = """Коменды:
/help - вывести список команд
/my_words - вывести последние 15 сохраненных слов
/my_words_num - вывести количество сохраненных слов
/delete - включить режим удаления слово
/cards - включить режим карточек (режим напоминания слов)
/cancel - выход из любого режима"""
MSG_START = MSG + "\n\n" + MSG_HELP

class FSMDelete(StatesGroup):
    word_for_delete = State()

class FSMCard(StatesGroup):
    word_for_reminder = State()


storage = MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)

users_w_access = [] # список пользователей с доступами
async def on_startup(_):
    await db_start()

    global users_w_access
    users_w_access = await get_users_w_access()
    # await bot.send_message('91523724', f"{users_w_access}")
    



# Доступ для админа
def auth(func):

    async def wrapper(message, *args, **kwargs):
        if message['from']['id'] != 91523724:
            return await message.reply("Access Denied -_-")
        return await func(message, *args, **kwargs)
    
    return wrapper


# Доступ для пользователей
def users_access(func):

    async def wrapper(message, *args, **kwargs):
        global users_w_access
        if message['from']['id'] not in users_w_access:
            return await message.reply("Access Denied.\nTo get access run - /access_request")
        return await func(message, *args, **kwargs)
    
    return wrapper


# Инлайновые клавиатуры
# Показать перевод
inline_buttons_translation = types.InlineKeyboardMarkup(row_width=1)
b1 = types.InlineKeyboardButton(text='Показать перевод', callback_data='translation')
b2 = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')

inline_buttons_translation.add(b1)
inline_buttons_translation.row(b2)

# Через сколько дней напомнить
inline_buttons_reminder = types.InlineKeyboardMarkup(row_width=4)
b3 = types.InlineKeyboardButton(text='1', callback_data='remind in 1 day')
b4 = types.InlineKeyboardButton(text='7', callback_data='remind in 7 day')
b5 = types.InlineKeyboardButton(text='30', callback_data='remind in 30 day')
b6 = types.InlineKeyboardButton(text='90', callback_data='remind in 90 day')

inline_buttons_reminder.add(b3, b4, b5, b6)
inline_buttons_reminder.row(b2)


# Запрос доступа
@dp.message_handler(commands=['access_request'])
async def access_request(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    username = message.from_user.username
    user_full_name = message.from_user.full_name

    logging.info(f'ЗАПРОС ДОСТУПА ДЛЯ {user_id} ! | {user_id=}, {username=}, {user_full_name=} {time.asctime()}')
    await message.reply('Запрос отправлен. Ожидайте уведомление...', reply=False)
    await bot.send_message('91523724', f"ЗАПРОС ДОСТУПА ДЛЯ:\n{user_id} | @{username} | {user_full_name}\n\nЧтоб открыть доступ - /access {user_id}\nЧтобы заблокировать - /block {user_id}") 


# Выдача доступа
@dp.message_handler(commands=['access'])
@auth
async def granting_access(message: types.Message, *args, **kwargs):
    global users_w_access
    user_id = message.from_user.id
    access_for_user_id = message.text.split(" ")
    del access_for_user_id[0]
    logging.info(f'Доступ открыт для пользователя {access_for_user_id}| {user_id=} {time.asctime()}')

    await add_access(access_for_user_id, 1)
    for user_id in access_for_user_id:
        if user_id.isnumeric():
            await bot.send_message(user_id, "Доступ открыт! Чтобы начать - /start")
            await message.reply(f'Доступ для пользователя {user_id} открыт.', reply=False)
    users_w_access = await get_users_w_access()


# Блокировка доступа
@dp.message_handler(commands=['block'])
@auth
async def block_access(message: types.Message, *args, **kwargs):
    global users_w_access
    user_id = message.from_user.id
    access_for_user_id = message.text.split(" ")
    del access_for_user_id[0]
    logging.info(f'Доступ заблокирован для пользователя {access_for_user_id}| {user_id=} {time.asctime()}')

    await add_access(access_for_user_id, 0)
    for user_id in access_for_user_id:
        if user_id.isnumeric():
            await message.reply(f'Доступ для пользователя {user_id} закрыт.', reply=False)
    users_w_access = await get_users_w_access()


# Старт
@dp.message_handler(commands=['start'])
@users_access
async def start_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_full_name = message.from_user.full_name

    logging.info(f'Старт | {user_id=}, {user_full_name=} {time.asctime()}')

    await create_profile(user_id, user_full_name)
    await message.reply(f'Привет, {user_name}!', reply=False)
    await bot.send_message(user_id, MSG_START)


# Хэлп
@dp.message_handler(commands=['help'])
@users_access
async def start_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Хэлп | {user_id=} {time.asctime()}')

    await bot.send_message(user_id, MSG_HELP)


# Выход из состояний
@dp.message_handler(state="*", commands=['cancel'])
@users_access
async def cancel_handler(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Отмена | {user_id=} {time.asctime()}')

    current_state = await state.get_state()
    if current_state is None:
        await message.reply("Что отменить? Ничего и не происходит :)", reply=False)
        return
    elif current_state == 'FSMDelete:word_for_delete':
        answer_message = "Хорошо, не будем удалять слова"
    elif current_state == 'FSMCard:word_for_reminder':
        answer_message = "Вышел из режима карточек"
    else:
        answer_message = "Отменил"
    await state.finish()
    await message.reply(answer_message, reply=False)


# Добавление слова
@dp.message_handler(regexp='.=.')
@users_access
async def word_insert(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_message = message.text
    answer_message = 'Записал.\nПосмотреть последние 15 слов - /my_words\nРежим карточек - /cards\nУдалить слово - /delete'

    logging.info(f'Добавление слова | {user_id=}, {user_full_name=}, {user_message} {time.asctime()}')
    
    await create_profile(user_id, user_full_name)
    await insert_words(user_id, user_message)
    await message.reply(answer_message, reply=False)


# Удаление слова
@dp.message_handler(commands=['delete'], state=None)
@users_access
async def word_delete(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Удаление слова | {user_id=}, {time.asctime()}')
    await FSMDelete.word_for_delete.set()
    answer_message = "Напиши слово, которое нужно удалить\n\nДля отмены - /cancel"
    await message.reply(answer_message, reply=False)

# Ловим слово для удаления
@dp.message_handler(state=FSMDelete.word_for_delete)
@users_access
async def load_word_for_delete(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Ловим слово для удаления | {user_id=}, {time.asctime()}')
    async with state.proxy() as data:
        data['word_for_delete'] = message.text
        
    answer_message = await delete_word(user_id, state)
    await state.finish()
    await message.reply(answer_message)


# Выводим список слов
@dp.message_handler(commands=['my_words'])
@users_access
async def print_my_words(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = select_words(user_id)

    logging.info(f'Выводим список сохраненных слов | {user_id=}, {time.asctime()}')
    
    await message.reply(answer_message, reply=False)


# Выводим кол-во слов
@dp.message_handler(commands=['my_words_num'])
@users_access
async def print_my_words_num(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = words_num(user_id)

    logging.info(f'Выводим кол-во сохраненных слов | {user_id=}, {time.asctime()}')
    
    await message.reply(answer_message, reply=False)


# Карточки для напоминания слов
@dp.message_handler(commands=['cards'], state=None)
@users_access
async def load_cards(message: types.Message, state: FSMContext, *args, **kwargs):

    user_id = message.from_user.id
    chat_id = message.chat.id
    logging.info(f'Запущены карточки | {user_id=}, {time.asctime()}')
    index_num = 0
    users_cards = cards(user_id)
    if not users_cards:
        answer_message = "На сегодня нет слов для повторения. Так держать!"
        await message.reply(answer_message, reply=False)
    else:
        total_num = len(users_cards)
        answer_message = "Режим карточек включен.\nТебе будут показываться слово и кнопка для просмотра перевода.\nА затем выбери через сколько дней напомнить слово еще раз:\n1 - через 1 день\n7 - через 7 дней\n30 - через 30 дней\n90 - через 90 дней\n\nДля отмены - /cancel"
        await message.reply(answer_message, reply=False)

        word_for_reminder = users_cards[index_num][1]
        cards_send_message = await bot.send_message(user_id, word_for_reminder, reply_markup=inline_buttons_translation)
        cards_send_message
        await FSMCard.word_for_reminder.set()
        async with state.proxy() as data:
            data['word_for_reminder'] = {'users_cards': users_cards, 
                                         'total_num': total_num, 
                                         'index_num': index_num, 
                                         'chat_id': chat_id, 
                                         'cards_send_message': cards_send_message}

# Ответ на колбэк показываем перевод
@dp.callback_query_handler(filters.Text(contains=['translation']), state=FSMCard.word_for_reminder) 
@users_access
async def translation(callback_query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    
    async with state.proxy() as data:
        users_cards = data['word_for_reminder']['users_cards']
        index_num = data['word_for_reminder']['index_num']
        chat_id = data['word_for_reminder']['chat_id']
        cards_send_message = data['word_for_reminder']['cards_send_message']
        user_id = callback_query.from_user.id
        logging.info(f'Показан перевод карточки | {user_id=}, {time.asctime()}')
        await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
        cards_edited_message_id = cards_send_message['message_id']
        cards_edited_message_text = cards_send_message['text'] + " | " + users_cards[index_num][2]
        await bot.edit_message_text(text=cards_edited_message_text, chat_id=chat_id, message_id=cards_edited_message_id, reply_markup=inline_buttons_reminder)
        await callback_query.answer(users_cards[index_num][1]) # завершаем коллбэк

# Ответ на колбэк следующее слово
@dp.callback_query_handler(filters.Text(contains=['remind in']), state=FSMCard.word_for_reminder) 
@users_access
async def next_cards(callback_query: types.CallbackQuery, state: FSMContext, *args, **kwargs):

    async with state.proxy() as data:
        users_cards = data['word_for_reminder']['users_cards']
        total_num = data['word_for_reminder']['total_num']
        index_num = data['word_for_reminder']['index_num']
        cards_send_message = data['word_for_reminder']['cards_send_message']

        user_id = callback_query.from_user.id
        remind_in = callback_query.data
        logging.info(f'Обновлена дата карточки | {user_id=}, {time.asctime()}')
        await update_remind_date(user_id, word_id = users_cards[index_num][0], remind_in = remind_in)
        await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
        await callback_query.answer(users_cards[index_num][1]) # завершаем коллбэк

        index_num += 1
        if index_num > total_num - 1:
            answer_message = "На сегодня больше нет слов. Так держать!\nВышел из режима карточек."
            await state.finish()
            await callback_query.message.answer(answer_message)
        else:
            word_for_reminder = users_cards[index_num][1]
            cards_send_message = await bot.send_message(user_id, word_for_reminder, reply_markup=inline_buttons_translation)
            cards_send_message
            async with state.proxy() as data:
                data['word_for_reminder']['index_num'] = index_num
                data['word_for_reminder']['cards_send_message'] = cards_send_message

# Ответ на колбэк - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMCard.word_for_reminder) 
@users_access
async def cancel_cards(callback_query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = "Вышел из режима карточек"
    await state.finish()
    await callback_query.message.answer(answer_message)




# В остальных случаях базовй ответ
@dp.message_handler()
@users_access
async def echo(message: types.Message, *args, **kwargs):
    answer_message = "Не пониманю. Может не хватает знака '='?"
    await message.answer(answer_message)
    # await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)