import time
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import message_texts
from sqlite import db_start, add_access, get_users_w_access, create_profile,\
    insert_words, select_words, delete_word, delete_all_words, cards, update_remind_date,\
    words_num, words_in_group_num, select_duplicate, download_csv, any_query

logging.basicConfig(level=logging.INFO)

load_dotenv()

storage = MemoryStorage()

# PROXY_URL = ""
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN) #, proxy=PROXY_URL
dp = Dispatcher(bot=bot, storage=storage)


class FSMDelete(StatesGroup):
    word_for_delete = State()

class FSMDeleteAll(StatesGroup):
    delete_all = State()

class FSMCard(StatesGroup):
    word_for_reminder = State()

class FSMQuery(StatesGroup):
    execute_query = State()


users_w_access = [] # список пользователей с доступами
async def on_startup(_):
    await db_start()
    await setup_bot_commands()

    global users_w_access
    users_w_access = await get_users_w_access()



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

# Команды
async def setup_bot_commands():
    bot_commands = [
        types.BotCommand("cards", "Режим карточек"),
        types.BotCommand("my_words", "Последние 15 слов"),
        types.BotCommand("my_words_num", "Количество слов"),
        types.BotCommand("my_words_in_groups_num", "Количество слов в группах"),
        types.BotCommand("duplicates", "Вывести дублирующиеся слова"),
        types.BotCommand("download_csv", "Скачать все слова в csv"),
        types.BotCommand("delete", "Режим удаления одного слова"),
        types.BotCommand("delete_all", "Режим удаления всех слов"),
        types.BotCommand("cancel", "Отмена"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("donate", "Поддержать проект")
    ]
    await bot.set_my_commands(bot_commands)


# Запрос доступа
@dp.message_handler(commands=['access_request'])
async def access_request(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    username = message.from_user.username
    user_full_name = message.from_user.full_name

    logging.info(f'ЗАПРОС ДОСТУПА ДЛЯ {user_id} ! | {user_id=}, {username=}, {user_full_name=} {time.asctime()}')
    await message.reply('Запрос отправлен. Ожидайте уведомления...', reply=False)
    await bot.send_message('91523724', f"ЗАПРОС ДОСТУПА ДЛЯ:\n{user_id} | @{username} | {user_full_name}\n\nЧтобы открыть доступ - /access {user_id}\nЧтобы заблокировать - /block {user_id}") 


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
    await bot.send_message(user_id, message_texts.MSG_START)


# Хэлп
@dp.message_handler(commands=['help'])
@users_access
async def help_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Хэлп | {user_id=} {time.asctime()}')

    await bot.send_message(user_id, message_texts.MSG_HELP)


# Просмотр команд для автора
@dp.message_handler(commands=['auth'])
@auth
async def help_auth_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Хэлп для автора | {user_id=} {time.asctime()}')

    await bot.send_message(user_id, message_texts.MSG_AUTH_HELP)


# Выход из состояний
@dp.message_handler(state="*", commands=['cancel'])
@users_access
async def cancel_handler(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Отмена | {user_id=} {time.asctime()}')

    current_state = await state.get_state()
    if current_state is None:
        await message.reply(message_texts.MSG_CANCEL, reply=False)
        return
    elif current_state in ['FSMDelete:word_for_delete','FSMDeleteAll:delete_all']:
        answer_message = message_texts.MSG_CANCEL_DELETE
    elif current_state == 'FSMCard:word_for_reminder':
        async with state.proxy() as data: # достаем id часа и сообщения, чтобы скрыть инлайновую клавиатуру
            chat_id = data['word_for_reminder']['chat_id']
            message_id = data['word_for_reminder']['cards_send_message']["message_id"]
        await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
        answer_message = message_texts.MSG_CANCEL_REMINDER
    else:
        answer_message = message_texts.MSG_CANCEL_GENETAL
    await state.finish()
    await message.reply(answer_message, reply=False)


# Добавление слова
@dp.message_handler(state="*", regexp='.=.')
@users_access
async def word_insert(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_message = message.text
    logging.info(f'Добавление слова | {user_id=}, {user_full_name=}, {user_message} {time.asctime()}')
    
    answer_message = message_texts.MSG_INSERT_WORD
    await create_profile(user_id, user_full_name)
    await insert_words(user_id, user_message)
    await message.reply(answer_message, reply=False)

    # выход из всех режимов, если они был включены
    current_state = await state.get_state()
    if current_state is not None:
        if current_state == 'FSMCard:word_for_reminder':
            async with state.proxy() as data: # достаем id часа и сообщения, чтобы скрыть инлайновую клавиатуру
                chat_id = data['word_for_reminder']['chat_id']
                message_id = data['word_for_reminder']['cards_send_message']["message_id"]
            await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
            answer_message = message_texts.MSG_CANCEL_REMINDER
            logging.info(f'Вышел из режима карточек | {user_id=}, {time.asctime()}')
        elif current_state in ['FSMDelete:word_for_delete','FSMDeleteAll:delete_all']:
            answer_message = message_texts.MSG_CANCEL_DELETE
            logging.info(f'Вышел из режима удаления | {user_id=}, {time.asctime()}')
        await state.finish()
        await message.reply(answer_message, reply=False)


# Удаление слова
@dp.message_handler(commands=['delete'], state=None)
@users_access
async def word_delete(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Удаление слова | {user_id=}, {time.asctime()}')
    await FSMDelete.word_for_delete.set()
    answer_message = message_texts.MSG_DELETE
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


# Удаление всех слов
@dp.message_handler(commands=['delete_all'], state=None)
@users_access
async def delete_all(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Удаление всех слов | {user_id=}, {time.asctime()}')
    await FSMDeleteAll.delete_all.set()
    answer_message = message_texts.MSG_DELETE_ALL
    await message.reply(answer_message, reply=False)

# Ловим подтверждение, что нужно удалить все слова
@dp.message_handler(commands=['delete_all'], state=FSMDeleteAll.delete_all)
@users_access
async def delete_all_again(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Все слова удалены | {user_id=}, {time.asctime()}')
        
    answer_message = await delete_all_words(user_id)
    await state.finish()
    await message.reply(answer_message)


# Выводим список слов
@dp.message_handler(commands=['my_words'])
@users_access
async def print_my_words(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await select_words(user_id)

    logging.info(f'Выводим список сохраненных слов | {user_id=}, {time.asctime()}')
    
    await message.reply(answer_message, reply=False)


# Выводим кол-во слов всего
@dp.message_handler(commands=['my_words_num'])
@users_access
async def print_my_words_num(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await words_num(user_id)

    logging.info(f'Выводим кол-во сохраненных слов | {user_id=}, {time.asctime()}')
    
    await message.reply(answer_message, reply=False)

# Выводим кол-во слов в группах
@dp.message_handler(commands=['my_words_in_groups_num'])
@users_access
async def print_my_words_in_groups_num(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await words_in_group_num(user_id)

    logging.info(f'Выводим кол-во сохраненных слов в группах | {user_id=}, {time.asctime()}')
    
    await message.reply(answer_message, reply=False)


# Скачиваем все слова в csv
@dp.message_handler(commands=['download_csv'])
@users_access
async def download(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Скачиваем файлы для пользователя в csv | {user_id=}, {time.asctime()}')

    fp = await download_csv(user_id)
    doc = open(fp, 'rb')
    await message.reply_document(doc)
    doc.close()
    if os.path.isfile(fp):
        os.remove(fp)
        logging.info(f'{fp} deleted. | {user_id=}, {time.asctime()}')
    else:
        logging.info(f'{fp} not found. | {user_id=}, {time.asctime()}')


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
        answer_message = message_texts.MSG_CARDS_NO_WORDS
        await message.reply(answer_message, reply=False)
    else:
        total_num = len(users_cards)
        answer_message = message_texts.MSG_CARDS_INFO
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
            answer_message = message_texts.MSG_CARDS_FINISH
            await state.finish()
            await callback_query.message.answer(answer_message)
            # DONATE
            answer_message_donate = message_texts.MSG_DONATE
            await callback_query.message.answer(answer_message_donate)
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

    answer_message = message_texts.MSG_CARDS_CANCEL
    await state.finish()
    await callback_query.message.answer(answer_message)
    # DONATE
    answer_message_donate = message_texts.MSG_DONATE
    await callback_query.message.answer(answer_message_donate)


# Вывести дублирующиеся слова
@dp.message_handler(commands=['duplicates'])
@users_access
async def duplicates(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await select_duplicate(user_id)
    logging.info(f'Вывод дублирующихся слов | {user_id=}, {time.asctime()}')
    await message.reply(answer_message, reply=False)


# Выполнить любой SQL запрос
@dp.message_handler(commands=['query'], state=None)
@auth
async def execute_query(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Переход в режим выполнения SQL запросов | {user_id=}, {time.asctime()}')
    await FSMQuery.execute_query.set()
    answer_message = message_texts.MSG_SQL_QUERY
    await message.reply(answer_message, reply=False)

# Ловим SQL запрос
@dp.message_handler(state=FSMQuery.execute_query)
@auth
async def execute_query(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Выполнение запроса | {user_id=}, {time.asctime()}')
    query = message.text
    answer_message = await any_query(query)
    await state.finish()
    await message.reply(answer_message)


# Донат
@dp.message_handler(commands=['donate'])
@users_access
async def donate_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Донат | {user_id=} {time.asctime()}')
    await bot.send_message(user_id, message_texts.MSG_DONATE_INFO)

# Донат Georgian_iban
@dp.message_handler(commands=['Georgian_iban'])
@users_access
async def donate_Georgian_iban_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Донат Georgian_iban | {user_id=} {time.asctime()}')
    await bot.send_message(user_id, message_texts.MSG_DONATE_Georgian_iban)

# Донат BUSD_BEP20
@dp.message_handler(commands=['BUSD_BEP20'])
@users_access
async def donate_BUSD_BEP20_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Донат BUSD_BEP20 | {user_id=} {time.asctime()}')
    await bot.send_message(user_id, message_texts.MSG_DONATE_BUSD_BEP20)

# Донат USDT_TRC20
@dp.message_handler(commands=['USDT_TRC20'])
@users_access
async def donate_USDT_TRC20_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Донат USDT_TRC20 | {user_id=} {time.asctime()}')
    await bot.send_message(user_id, message_texts.MSG_DONATE_USDT_TRC20)

# Донат MSG_DONATE_USDC_ERC20
@dp.message_handler(commands=['USDC_ERC20'])
@users_access
async def donate_MSG_DONATE_USDC_ERC20_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Донат MSG_DONATE_USDC_ERC20 | {user_id=} {time.asctime()}')
    await bot.send_message(user_id, message_texts.MSG_DONATE_USDC_ERC20)




# В остальных случаях базовй ответ
@dp.message_handler()
@users_access
async def echo(message: types.Message, *args, **kwargs):
    answer_message = message_texts.MSG_COMMAND_NOT_DEFINED
    await message.answer(answer_message)
    # await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)