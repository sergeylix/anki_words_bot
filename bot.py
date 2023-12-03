import time
from pytz import utc
import logging
import os

import pandas as pd
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.types.input_file import InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import message_texts
from sqlite import db_start, get_files, add_file_row, update_file_row, get_auth_access, add_access, get_users_w_access,\
    create_profile, update_user_language, words_exists, update_last_activity, add_basic_words, del_basic_words, insert_words, select_words,\
    delete_word, delete_all_words, actual_user_group, all_user_groups, change_cards_group, cards,\
    update_remind_date, words_num, select_duplicate, upload_csv, download_csv, update_group, actual_user_notification_interval,\
    update_notification_interval, user_list_to_send_notifications, user_list_to_send_message, event_recording, any_query

# All timestamp in UTC: -3 hour from msk

logging.basicConfig(level=logging.INFO)

load_dotenv()

storage = MemoryStorage()

# PROXY_URL = ""
TOKEN = os.getenv('TOKEN')

bot = Bot(token=TOKEN) #, proxy=PROXY_URL
dp = Dispatcher(bot=bot, storage=storage)


class FSMLanguage(StatesGroup):
    language = State()

class FSMDelete(StatesGroup):
    word_for_delete = State()

class FSMDeleteAll(StatesGroup):
    delete_all = State()

class FSMCard(StatesGroup):
    word_for_reminder = State()
    change_cards_group = State()

class FSMUpload(StatesGroup):
    upload_csv = State()

class FSMDownload(StatesGroup):
    download_csv = State()
    download_csv_group_selection = State()

class FSMChangeGroup(StatesGroup):
    change_group = State()

class FSMNotif(StatesGroup):
    notifications = State()

class FSMSendForAll(StatesGroup):
    send_for_all = State()

class FSMQuery(StatesGroup):
    execute_query = State()


users_info = [] # список пользователей с инфомрацией
users_w_access = [] # список пользователей с доступами
async def on_startup(_):
    await db_start()
    await setup_bot_commands()
    await upload_files()

    global users_w_access, users_info
    users_w_access, users_info = await get_users_w_access()



# Доступ для админа
def auth(func):

    async def wrapper(message, *args, **kwargs):
        if message['from']['id'] != 91523724:
            return await message.reply(message_texts.MSG_ACCESS_DENIED['EN'])
        return await func(message, *args, **kwargs)
    
    return wrapper


# Доступ для пользователей
def users_access(func):

    async def wrapper(message, user_language=None, *args, **kwargs):
        global users_w_access, users_info
        if message['from']['id'] not in users_w_access:
            return await message.reply(message_texts.MSG_ACCESS_DENIED_REQUEST['EN'])
        user_language = users_info[message['from']['id']]['language']
        if user_language == "None": user_language = 'EN'
        await update_last_activity(message['from']['id'])
        return await func(message, user_language=user_language, *args, **kwargs)
    
    return wrapper


# Инлайновые клавиатуры
# Выбор языка
inline_buttons_language = types.InlineKeyboardMarkup(row_width=2)
b1 = types.InlineKeyboardButton(text='🇬🇧 English', callback_data='language_set EN')
b2 = types.InlineKeyboardButton(text='🇷🇺 Русский', callback_data='language_set RU')
b3 = types.InlineKeyboardButton(text='Cancel', callback_data='cancel')

inline_buttons_language.add(b1, b2)
inline_buttons_language.row(b3)


# Показать перевод
def inline_buttons_translation(user_language: str):
    ib_translation = types.InlineKeyboardMarkup(row_width=1)
    b1 = types.InlineKeyboardButton(text=message_texts.KB_CARDS_SHOW_TRANSLATION[user_language], callback_data='translation')
    b2 = types.InlineKeyboardButton(text=message_texts.KB_CARDS_SHOW_CANCEL[user_language], callback_data='cancel')

    ib_translation.add(b1)
    ib_translation.row(b2)
    return ib_translation

# Через сколько дней напомнить
def inline_buttons_reminder(user_language: str):
    ib_reminder = types.InlineKeyboardMarkup(row_width=4)
    b2 = types.InlineKeyboardButton(text=message_texts.KB_CARDS_SHOW_CANCEL[user_language], callback_data='cancel')
    b3 = types.InlineKeyboardButton(text='1', callback_data='remind in 1 day')
    b4 = types.InlineKeyboardButton(text='7', callback_data='remind in 7 day')
    b5 = types.InlineKeyboardButton(text='30', callback_data='remind in 30 day')
    b6 = types.InlineKeyboardButton(text='90', callback_data='remind in 90 day')

    ib_reminder.add(b3, b4, b5, b6)
    ib_reminder.row(b2)
    return ib_reminder

# Загружаем слова из CSV
def inline_buttons_upload(user_language: str):
    ib_upload = types.InlineKeyboardMarkup(row_width=3)
    upload_b1 = types.InlineKeyboardButton(text=message_texts.KB_UPLOAD_YES[user_language], callback_data='upload_yes')
    upload_b2 = types.InlineKeyboardButton(text=message_texts.KB_UPLOAD_NO[user_language], callback_data='upload_no')
    upload_b3 = types.InlineKeyboardButton(text=message_texts.KB_UPLOAD_CANCEL[user_language], callback_data='cancel')

    ib_upload.add(upload_b1)
    ib_upload.row(upload_b2)
    ib_upload.row(upload_b3)
    return ib_upload

# Что скачать
def inline_buttons_download(user_language: str):
    ib_download = types.InlineKeyboardMarkup(row_width=3)
    download_b1 = types.InlineKeyboardButton(text=message_texts.KB_DOWNLOAD_ALL[user_language], callback_data='download_all')
    download_b2 = types.InlineKeyboardButton(text=message_texts.KB_DOWNLOAD_GROUP[user_language], callback_data='download_group')
    download_b3 = types.InlineKeyboardButton(text=message_texts.KB_DOWNLOAD_CANCEL[user_language], callback_data='cancel')

    ib_download.add(download_b1)
    ib_download.row(download_b2)
    ib_download.row(download_b3)
    return ib_download

# Для каких слов изменить группу
def inline_buttons_chenge_type(user_language: str):
    ib_chenge_type = types.InlineKeyboardMarkup(row_width=4)
    chenge_type_b1 = types.InlineKeyboardButton(text=message_texts.KB_CHANGE_GR_ONE_WORD[user_language], callback_data='change_one')
    chenge_type_b2 = types.InlineKeyboardButton(text=message_texts.KB_CHANGE_GR_IN_GR[user_language], callback_data='change_group')
    chenge_type_b3 = types.InlineKeyboardButton(text=message_texts.KB_CHANGE_GR_ALL[user_language], callback_data='change_all')
    chenge_type_b4 = types.InlineKeyboardButton(text=message_texts.KB_CHANGE_GR_CANCEL[user_language], callback_data='cancel')

    ib_chenge_type.add(chenge_type_b1)
    ib_chenge_type.row(chenge_type_b2)
    ib_chenge_type.row(chenge_type_b3)
    ib_chenge_type.row(chenge_type_b4)
    return ib_chenge_type


# Настройка частоты уведомлений
def inline_buttons_notifications(user_language: str):
    ib_notifications = types.InlineKeyboardMarkup(row_width=4)
    notifications_b1 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_DAY[user_language], callback_data='notifications_set 1')
    notifications_b2 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_2DAYS[user_language], callback_data='notifications_set 2')
    notifications_b3 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_WEEK[user_language], callback_data='notifications_set 7')
    notifications_b4 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_MONTH[user_language], callback_data='notifications_set 30')
    notifications_b5 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_NEVER[user_language], callback_data='notifications_set never')
    notifications_b6 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_CONCEL[user_language], callback_data='cancel')

    ib_notifications.add(notifications_b1, notifications_b2)
    ib_notifications.row(notifications_b3, notifications_b4)
    ib_notifications.row(notifications_b5)
    ib_notifications.row(notifications_b6)
    return ib_notifications


# Обычные клавиатуры
# buttons_download = types.ReplyKeyboardMarkup(resize_keyboard=True)
# download_b1 = types.KeyboardButton(text=message_texts.KB_DOWNLOAD_ALL)
# download_b2 = types.KeyboardButton(text=message_texts.KB_DOWNLOAD_GROUP)
# download_b3 = types.KeyboardButton(text=message_texts.KB_DOWNLOAD_CANCEL)

# buttons_download.add(download_b1, download_b2)
# buttons_download.row(download_b3)


# Команды
async def setup_bot_commands():
    bot_commands = [
        types.BotCommand("cards", "Start cards mode"),
        types.BotCommand("words", "Show the last 15 saved words"),
        types.BotCommand("words_num", "Show the number of saved words"),
        types.BotCommand("duplicates", "Show duplicate words"),
        types.BotCommand("import_export", "Upload or download words"),
        types.BotCommand("delete", "Delete one word mode"),
        types.BotCommand("delete_all", "Delete all words mode"),
        types.BotCommand("cancel", "Turn off any mode"),
        types.BotCommand("help", "Help"),
        types.BotCommand("language", "Change interface language"),
        types.BotCommand("notifications", "Set up notifications"),
        types.BotCommand("donate", "Support the project")
    ]
    await bot.set_my_commands(bot_commands)


# Загрузка файлов в ТГ для дальнейшей отправки
async def upload_files():
    auth_id = '91523724'
    file_names_in_db = []
    files_in_db_list = []
    files_in_db_dict = {'file_id': str(),
                        'file_name': str()}
    file_list = [
                    {'file_name': 'template.csv',
                     'file_description': 'template for uploading csv',
                     'file_path': 'bot_files/csv/'
                    }
                ]
    file_rows_in_db = await get_files()
    for row in file_rows_in_db:
        file_names_in_db.append(row[1])
        files_in_db_dict['file_id'] = row[0]
        files_in_db_dict['file_name'] = row[1]
        files_in_db_list.append(files_in_db_dict.copy())
    
    for value in file_list:
        file_name = value['file_name']
        file_description = value['file_description']
        file_path = value['file_path'] + value['file_name']
        if file_name not in file_names_in_db:
            file = InputFile(file_path, filename=file_name)
            answer_message = f'Добавлен файл <b>{file_name}</b> на сервер ТГ'
            send_to_auth = await bot.send_document(chat_id=auth_id, document=file, caption=answer_message, parse_mode = 'HTML', disable_notification=True)
            file_id = str(send_to_auth.document.file_id)
            await add_file_row(file_id, file_name, file_description, file_path)
        else:
            for f in files_in_db_list:
                if file_name == f['file_name']:
                    file_id = f['file_id']
                else: 
                    file_id = None
            try:
                answer_message = f'Файл <b>{file_name}</b> существует на сервере ТГ'
                send_to_auth = await bot.send_document(chat_id=auth_id, document=file_id, caption=answer_message, parse_mode = 'HTML', disable_notification=True)
                await asyncio.sleep(.5)
                await bot.delete_message(auth_id, send_to_auth.message_id)
            except:
                answer_message = f'Файл <b>{file_name}</b> существует на сервере ТГ, обновлен <code>file_id</code>'
                file = InputFile(file_path, filename=file_name)
                send_to_auth = await bot.send_document(chat_id=auth_id, document=file, caption=answer_message, parse_mode = 'HTML', disable_notification=True)
                file_id_new = str(send_to_auth.document.file_id)
                await update_file_row(file_name, file_id_new)


# Удаление файла на VPS сервере
async def delete_file_on_server(user_id, fp: str):
    if os.path.isfile(fp):
        os.remove(fp)
        logging.info(f'{fp} deleted. | {user_id=}, {time.asctime()}')
    else:
        logging.info(f'{fp} not found. | {user_id=}, {time.asctime()}')


# Запрос доступа
@dp.message_handler(commands=['access_request'])
async def access_request(message: types.Message, *args, **kwargs):
    global users_w_access, users_info
    user_id = message.from_user.id
    username = message.from_user.username
    user_full_name = message.from_user.full_name

    if user_id in users_w_access:
        await message.reply('Доступ уже открыт.\n/help — чтобы посмотреть инструкцию и команды', reply=False)
    else:
        is_auth_access = await get_auth_access()
        # Автоматический
        if is_auth_access == 0:
            await add_access([user_id], 1)
            await message.reply(message_texts.MSG_ACCESS['EN'], reply=False)
            await bot.send_message('91523724', f"АВТОМАТИЧЕСКИ ОТКРЫТ ДОСТУПА ДЛЯ:\n{user_id} | @{username} | {user_full_name}\n\nЧтобы заблокировать — /block {user_id}")
            # events
            logging.info(f'АВТОМАТИЧЕСКИ ОТКРЫТ ДОСТУП ДЛЯ {user_id} ! | {user_id=}, {username=}, {user_full_name=} {time.asctime()}')
            await event_recording(user_id=user_id, event='access_request')
            await event_recording(user_id=user_id, event='granting_access')
        else:
            # По согласованию с автором
            await message.reply('🛎 Запрос отправлен. Ожидайте уведомления...', reply=False)
            await bot.send_message('91523724', f"ЗАПРОС ДОСТУПА ДЛЯ:\n{user_id} | @{username} | {user_full_name}\n\nЧтобы открыть доступ — /access {user_id}\nЧтобы заблокировать — /block {user_id}") 
            # events
            logging.info(f'ЗАПРОС ДОСТУПА ДЛЯ {user_id} ! | {user_id=}, {username=}, {user_full_name=} {time.asctime()}')
            await event_recording(user_id=user_id, event='granting_access')
    users_w_access, users_info = await get_users_w_access()

# Выдача доступа
@dp.message_handler(commands=['access'])
@auth
async def granting_access(message: types.Message, *args, **kwargs):
    global users_w_access, users_info
    user_id = message.from_user.id
    access_for_user_id = message.text.split(" ")
    del access_for_user_id[0]

    await add_access(access_for_user_id, 1)
    for user_id in access_for_user_id:
        if user_id.isnumeric():
            await bot.send_message(user_id, message_texts.MSG_ACCESS['EN'])
            await message.reply(f'Доступ для пользователя {user_id} открыт.', reply=False)
    users_w_access, users_info = await get_users_w_access()
    # events
    logging.info(f'Доступ открыт для пользователя {access_for_user_id}| {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='granting_access')


# Блокировка доступа
@dp.message_handler(commands=['block'])
@auth
async def block_access(message: types.Message, *args, **kwargs):
    global users_w_access, users_info
    user_id = message.from_user.id
    access_for_user_id = message.text.split(" ")
    del access_for_user_id[0]

    await add_access(access_for_user_id, 0)
    for user_id in access_for_user_id:
        if user_id.isnumeric():
            await message.reply(f'Доступ для пользователя {user_id} закрыт.', reply=False)
    users_w_access, users_info = await get_users_w_access()
    # events
    logging.info(f'Доступ заблокирован для пользователя {access_for_user_id}| {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='access_blocking')    


# Функция для выбора языка
async def language(message, state):
    user_id = message.from_user.id

    await FSMLanguage.language.set()
    async with state.proxy() as data:
        data['language'] = message
    
    answer_message = message_texts.MSG_LANGUAGE['EN']
    await message.reply(answer_message, reply=False, parse_mode = 'HTML', reply_markup=inline_buttons_language)
    # events
    logging.info(f'Настройка языка интерфейса | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='asking_language')


# Функция для приветския
@users_access
async def greetings(message, user_language: str):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    await message.reply(message_texts.MSG_HI[user_language].format(user_name=user_name), reply=False, parse_mode = 'HTML')
    await bot.send_message(user_id, message_texts.MSG_START[user_language], parse_mode = 'HTML')
    await bot.send_message(user_id, message_texts.MSG_ONBOARDING_START[user_language], parse_mode = 'HTML')


# Старт
@dp.message_handler(commands=['start'])
@users_access
async def start_hendler(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name

    # events
    logging.info(f'Старт | {user_id=}, {user_full_name=} {time.asctime()}')
    await event_recording(user_id=user_id, event='start') 

    await create_profile(user_id, user_full_name)
    await language(message, state)


# Выбор языка - отдельная команда
@dp.message_handler(commands=['language'], state=None)
@users_access
async def language_change(message: types.Message, state: FSMContext, *args, **kwargs):
    await language(message, state)


# Ответ на колбэк настройка языка - установка языка
@dp.callback_query_handler(filters.Text(contains=['language_set']), state=FSMLanguage.language) 
@users_access
async def set_language(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    global users_w_access, users_info
    user_id = callback_query.from_user.id
    new_language = str(callback_query.data.split(' ', 1)[1])
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк
    await update_user_language(user_id, new_language) # Изменяем язык в БД
    users_w_access, users_info = await get_users_w_access()

    answer_message = message_texts.MSG_LANGUAGE_SET[new_language]
    await callback_query.message.answer(answer_message, parse_mode = 'HTML')
    # events
    logging.info(f'Устанавливаем язык интерфейса | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='setting_up_language')

    async with state.proxy() as data:
        message = data['language']
        if message.text == '/start':
            await greetings(message, user_language)

    await state.finish()


# Ответ на колбэк настройка языка - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMLanguage.language) 
@users_access
async def cancel_set_language(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк
    answer_message = message_texts.MSG_CANCEL_LANGUAGE[user_language]

    await callback_query.message.answer(answer_message)

    async with state.proxy() as data:
        message = data['language']
        if message.text == '/start':
            await greetings(message, user_language)

    await state.finish()



# Хэлп
@dp.message_handler(commands=['help'])
@users_access
async def help_hendler(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    await bot.send_message(user_id, message_texts.MSG_HELP[user_language], parse_mode = 'HTML')
    # events
    logging.info(f'Хэлп | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='help')


# Вывести все команжы
@dp.message_handler(commands=['commands'])
@users_access
async def all_commands(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    await bot.send_message(user_id, message_texts.MSG_COMANDS[user_language], parse_mode = 'HTML')
    # events
    logging.info(f'Вывести все команды | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='sending_commands')


# Онбординг - инструкция
@dp.message_handler(commands=['onboarding'])
@users_access
async def onboarding_info(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    await bot.send_message(user_id, message_texts.MSG_ONBOARDING[user_language], parse_mode = 'HTML')
    # отправка видео инструкции
    # await message.answer_video(user_id, )
    # events
    logging.info(f'Онбординг - инстркция | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='onboarding')

# Онбординг - добавление базовых слов
@dp.message_handler(commands=['add_basic_words'])
@users_access
async def onboarding_add_basic_words(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    await create_profile(user_id, user_full_name)
    await add_basic_words(user_id, user_language)
    await bot.send_message(user_id, message_texts.MSG_ONBOARDING_ADD_BASIC_WORDS[user_language], parse_mode = 'HTML')
    # events
    logging.info(f'Онбординг - добавление базовых слов | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='add_basic_words')

# Онбординг - удаление базовых слов
@dp.message_handler(commands=['del_basic_words'])
@users_access
async def onboarding_del_basic_words(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    await del_basic_words(user_id)
    await bot.send_message(user_id, message_texts.MSG_ONBOARDING_DEL_BASIC_WORDS[user_language], parse_mode = 'HTML')
    # events
    logging.info(f'Онбординг - удаление базовых слов | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='del_basic_words')


# Просмотр команд для автора
@dp.message_handler(commands=['auth'])
@auth
async def help_auth_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    await bot.send_message(user_id, message_texts.MSG_AUTH_HELP, parse_mode = 'HTML')
    # events
    logging.info(f'Хэлп для автора | {user_id=} {time.asctime()}')


# Выход из состояний
@dp.message_handler(state="*", commands=['cancel'])
@users_access
async def cancel_handler(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    current_state = await state.get_state()
    if current_state is None:
        await message.reply(message_texts.MSG_CANCEL[user_language], reply=False)
        return
    elif current_state in ['FSMDelete:word_for_delete','FSMDeleteAll:delete_all']:
        answer_message = message_texts.MSG_CANCEL_DELETE[user_language]
    elif current_state == 'FSMCard:word_for_reminder':
        async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
            chat_id = data['word_for_reminder']['chat_id']
            message_id = data['word_for_reminder']['cards_send_message']['message_id']
        await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
        answer_message = message_texts.MSG_CANCEL_REMINDER[user_language]
    elif current_state == 'FSMCard:change_cards_group':
        answer_message = message_texts.MSG_CANCEL_CHANGE_GROUP[user_language]
    elif current_state == 'FSMUpload:upload_csv':
        try:
            async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
                chat_id = data['upload_csv']['chat_id']
                message_id = data['upload_csv']['message_id']
                fp = data['upload_csv']['fp']
                await delete_file_on_server(user_id, fp) # удаляем скаченный файл
            await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
        except:
            pass
        answer_message = message_texts.MSG_CANCEL_UPLOAD_CSV[user_language]
    elif current_state == 'FSMDownload:download_csv':
        async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
            chat_id = data['download_csv']['chat_id']
            message_id = data['download_csv']['message_id']
        await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
        answer_message = message_texts.MSG_CANCEL_CHANGE_DOWNLOAD[user_language]
    else:
        answer_message = message_texts.MSG_CANCEL_GENETAL[user_language]
    await state.finish()
    await message.reply(answer_message, reply=False)
    # events
    logging.info(f'Отмена | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='cancel')


# Обновление следующей даты уведомления
async def update_next_notification(user_id: str):
    notification_interval = await actual_user_notification_interval(user_id)
    if notification_interval.isnumeric():
        await update_notification_interval(user_id, notification_interval) # Изменяем частоту в БД


# Добавление слова
@dp.message_handler(state={None, FSMLanguage.language,
                           FSMDelete.word_for_delete, 
                           FSMDeleteAll.delete_all,
                           FSMUpload.upload_csv,
                           FSMDownload.download_csv, 
                           FSMDownload.download_csv_group_selection,
                           FSMCard.word_for_reminder, 
                           FSMCard.change_cards_group}, 
                    regexp='.=.')
@users_access
async def word_insert(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_message = message.text
    
    answer_message = message_texts.MSG_INSERT_WORD[user_language]
    await create_profile(user_id, user_full_name)
    await insert_words(user_id, user_message)
    await message.reply(answer_message)

    # выход из всех режимов, если они были включены
    current_state = await state.get_state()
    if current_state is not None:
        if current_state == 'FSMCard:word_for_reminder':
            async with state.proxy() as data: # достаем id часа и сообщения, чтобы скрыть инлайновую клавиатуру
                chat_id = data['word_for_reminder']['chat_id']
                message_id = data['word_for_reminder']['cards_send_message']["message_id"]
            await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
            answer_message = message_texts.MSG_CANCEL_REMINDER[user_language]
            logging.info(f'Вышел из режима карточек | {user_id=}, {time.asctime()}')
        elif current_state in ['FSMCard:change_cards_group','FSMDownload:download_csv_group_selection']:
            answer_message = message_texts.MSG_CANCEL_CHANGE_GROUP[user_language]
            logging.info(f'Вышел из режима изменения групп | {user_id=}, {time.asctime()}')
        elif current_state in ['FSMDelete:word_for_delete','FSMDeleteAll:delete_all']:
            answer_message = message_texts.MSG_CANCEL_DELETE[user_language]
            logging.info(f'Вышел из режима удаления | {user_id=}, {time.asctime()}')
        elif current_state == 'FSMUpload:upload_csv':
            try:
                async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
                    chat_id = data['upload_csv']['chat_id']
                    message_id = data['upload_csv']['message_id']
                    fp = data['upload_csv']['fp']
                    await delete_file_on_server(user_id, fp) # удаляем скаченный файл
                await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
            except:
                pass
            answer_message = message_texts.MSG_CANCEL_UPLOAD_CSV[user_language]
            logging.info(f'Вышел из загрузки csv | {user_id=}, {time.asctime()}')
        elif current_state == 'FSMDownload:download_csv':
            async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
                chat_id = data['download_csv']['chat_id']
                message_id = data['download_csv']['message_id']
            await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
            answer_message = message_texts.MSG_CANCEL_CHANGE_DOWNLOAD[user_language]
            logging.info(f'Вышел из режима скачивания | {user_id=}, {time.asctime()}')
        else:
            answer_message = message_texts.MSG_CANCEL_GENETAL[user_language]
        await state.finish()
        await message.reply(answer_message, reply=False)
    # Обновляем след. дату уведомления
    await update_next_notification(user_id)
    # events
    logging.info(f'Добавление слова | {user_id=}, {user_full_name=}, {user_message} {time.asctime()}')
    await event_recording(user_id=user_id, event='adding_word')


# Удаление слова
@dp.message_handler(commands=['delete'], state=None)
@users_access
async def word_delete(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    if not words_exists(user_id):
        answer_message = message_texts.MSG_NO_WORDS[user_language]
    else:
        await FSMDelete.word_for_delete.set()
        answer_message = message_texts.MSG_DELETE[user_language]
    await message.reply(answer_message, reply=False)
    # events
    logging.info(f'Удаление слова | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='asking_delete_word')

# Ловим слово для удаления
@dp.message_handler(state=FSMDelete.word_for_delete)
@users_access
async def load_word_for_delete(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    async with state.proxy() as data:
        data['word_for_delete'] = message.text
        
    answer_message = await delete_word(user_id, user_language, state)
    await state.finish()
    await message.reply(answer_message)
    # events
    logging.info(f'Ловим слово для удаления | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='deleting_word')


# Удаление всех слов
@dp.message_handler(commands=['delete_all'], state=None)
@users_access
async def delete_all(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    if not words_exists(user_id):
        answer_message = message_texts.MSG_NO_WORDS[user_language]
    else:
        await FSMDeleteAll.delete_all.set()
        answer_message = message_texts.MSG_DELETE_ALL[user_language]
    await message.reply(answer_message, reply=False)
    # events
    logging.info(f'Удаление всех слов | {user_id=}, {time.asctime()}')

# Ловим запуск процесса удаления всех слов
@dp.message_handler(commands=['delete_all'], state=FSMDeleteAll.delete_all)
@users_access
async def delete_all_again(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = message_texts.MSG_DELETE_ALL_X2[user_language]
    await message.reply(answer_message)
    # events
    logging.info(f'Запущен процесс удаления всех слов | {user_id=}, {time.asctime()}')

# Ловим подтверждение, что нужно удалить все слова
@dp.message_handler(commands=['yes'], state=FSMDeleteAll.delete_all)
@users_access
async def delete_all_again(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await delete_all_words(user_id, user_language)
    await state.finish()
    await message.reply(answer_message, reply=False)
    # events
    logging.info(f'Все слова удалены | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='deleting_all_words')


# Выводим список слов
@dp.message_handler(commands=['words'])
@users_access
async def print_my_words(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await select_words(user_id, user_language)
    await message.reply(answer_message, reply=False)
    # events
    logging.info(f'Выводим список сохраненных слов | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='sending_last_words')


# Выводим кол-во слов всего
@dp.message_handler(commands=['words_num'])
@users_access
async def print_my_words_num(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await words_num(user_id, user_language)
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    # events
    logging.info(f'Выводим кол-во сохраненных слов | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='sending_word_count')


# Импорт экспорт
@dp.message_handler(commands=['import_export'], state=None)
@users_access
async def import_export(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = message_texts.MSG_IMPORT_EXPORT[user_language]
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    # events
    logging.info(f'Импорт экспорт | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='import_export')


# Загрузка слов пользователя в бота через csv
@dp.message_handler(commands=['upload_csv'], state=None)
@users_access
async def upload(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Пользователь переходит в режим загрузки слов из csv | {user_id=}, {time.asctime()}')
    answer_message = message_texts.MSG_UPLOAD_CSV[user_language]
    await message.reply(answer_message, reply=False, parse_mode = 'HTML', disable_web_page_preview=True)
    try:
        file_id = await get_files(file_name='template.csv')
        if not file_id: 
            file_id = None
        else: 
            file_id = file_id[0]
        answer_message = message_texts.MSG_UPLOAD_CSV_TEMPLATE[user_language]
        await bot.send_document(chat_id=user_id, document=file_id, caption=answer_message, parse_mode = 'HTML')
    except:
        logging.info(f'Ошибка при отправке шаблона CSV файла | {user_id=}, {time.asctime()}')
    await FSMUpload.upload_csv.set()

# Загружаем слова пользователя в бота через csv - проверяем и готовим превью
@dp.message_handler(content_types=['document','text'], state=FSMUpload.upload_csv)
@users_access
async def file_processing(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Обрабатываем полученный файл | {user_id=}, {time.asctime()}')

    if document := message.document:
        if document.file_name[-4:] == '.csv':
            if document.file_size <= 20971520:
                answer_message = message_texts.MSG_UPLOAD_CSV_PROCESSING[user_language]
                await message.reply(answer_message, reply=False, parse_mode = 'HTML', disable_web_page_preview=True)
                
                try:
                    k = 1
                    file_path = f'tmp/documents/id_{user_id}_{time.strftime("%Y%m%d_%H%M%S")}.csv'
                    await document.download(destination_file=file_path)
                    df = pd.DataFrame()
                    df = pd.read_csv(file_path, header=None, sep=';')
                    df = df.astype(object).where(pd.notnull(df),None)
                    if str(df.iloc[0,1]) == 'translation':
                        k = k + 1
                        df = df.iloc[1:]
                        if df.shape[0] == 0:
                            logging.info(f'Не успешная загрузка ERR_6 | {user_id=}, {time.asctime()}')
                            answer_message = message_texts.MSG_UPLOAD_CSV_ERR_6[user_language]
                            await message.reply(answer_message, reply=False, parse_mode = 'HTML', disable_web_page_preview=True)
                            return
                    for i in range(df.shape[0]):
                        for j in range(df.shape[1]):
                            value = df.iloc[i, j]
                            if j in (0, 1) and not value:
                                answer_message = message_texts.MSG_UPLOAD_CSV_ERR_5[user_language].format(row=i+k)
                                await message.reply(answer_message, reply=False, parse_mode = 'HTML', disable_web_page_preview=True)
                                return
                    
                    # preview preparation
                    preview = str()
                    df_head = df.head(5)
                    for i in range(df_head.shape[0]):
                        for j in range(df_head.shape[1]):
                            value = df_head.iloc[i, j]
                            if not value:
                                value = ""
                            else:
                                value = str(value)
                            if j >= 2:
                                preview = preview + value
                            else:
                                preview = preview + value + " | "
                        if i == df_head.shape[0] - 1:
                            preview = preview
                        else:
                            preview = preview + "\n"
                    answer_message = message_texts.MSG_UPLOAD_CSV_PREVIEW[user_language].format(preview=preview)
                    upload_send_message = await message.reply(answer_message, reply=False, parse_mode = 'HTML', disable_web_page_preview=True, reply_markup = inline_buttons_upload(user_language))
                    upload_send_message
                    chat_id = message.chat.id
                    message_id = upload_send_message['message_id']
                    async with state.proxy() as data:
                        data['upload_csv'] = {'chat_id': chat_id,
                                                'message_id': message_id,
                                                'fp': file_path,
                                                }
                    return
                except:
                    logging.info(f'Не успешная загрузка ERR_4 | {user_id=}, {time.asctime()}')
                    answer_message = message_texts.MSG_UPLOAD_CSV_ERR_4[user_language]
            else:
                logging.info(f'Не успешная загрузка ERR_3 | {user_id=}, {time.asctime()}')
                answer_message = message_texts.MSG_UPLOAD_CSV_ERR_3[user_language]
        else:
            logging.info(f'Не успешная загрузка ERR_2 | {user_id=}, {time.asctime()}')
            answer_message = message_texts.MSG_UPLOAD_CSV_ERR_2[user_language]
    else:
        logging.info(f'Не успешная загрузка ERR_1 | {user_id=}, {time.asctime()}')
        answer_message = message_texts.MSG_UPLOAD_CSV_ERR_1[user_language]

    await message.reply(answer_message, reply=False, parse_mode = 'HTML', disable_web_page_preview=True)

# Ответ на колбэк загружкаем слова?
@dp.callback_query_handler(filters.Text(contains=['upload_']), state=FSMUpload.upload_csv) 
@users_access
async def upload_confirmation(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    download_type = callback_query.data

    if download_type == 'upload_yes':
        answer_message = message_texts.MSG_UPLOAD_CSV_YES[user_language]
        async with state.proxy() as data:
            fp = data['upload_csv']['fp']
            logging.info(f'Загружаем слова из CSV в БД | {user_id=}, {time.asctime()}')
            try:
                await upload_csv(user_id, fp)
                logging.info(f'Успешно загрузили слова в БД | {user_id=}, {time.asctime()}')
            except:
                answer_message = message_texts.MSG_UPLOAD_CSV_YES_ERR[user_language]
                logging.info(f'Ошибка в загрузке слов в БД | {user_id=}, {time.asctime()}')
            await delete_file_on_server(user_id, fp) # удаляем скаченный файл
        await state.finish()
    else:
        answer_message = message_texts.MSG_UPLOAD_CSV_NO[user_language]
        async with state.proxy() as data:
            fp = data['upload_csv']['fp']
            await delete_file_on_server(user_id, fp) # удаляем скаченный файл
    await callback_query.message.answer(answer_message, reply=False, parse_mode = 'HTML')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк


# Ответ на колбэк загружкаем слова? - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMUpload.upload_csv) 
@users_access
async def cancel_upload(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = message_texts.MSG_CANCEL_UPLOAD_CSV[user_language]
    await callback_query.message.answer(answer_message)
    async with state.proxy() as data:
        fp = data['upload_csv']['fp']
        await delete_file_on_server(user_id, fp) # удаляем скаченный файл
    await state.finish()


# Скачиваем слова из бота в csv
@dp.message_handler(commands=['download_csv'], state=None)
@users_access
async def download(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    if not words_exists(user_id):
        answer_message = message_texts.MSG_NO_WORDS[user_language]
        await message.reply(answer_message, reply=False)
    else:
        await FSMDownload.download_csv.set()
        answer_message = message_texts.MSG_DOWNLOAD_CSV[user_language]
        download_send_message = await message.reply(answer_message, reply=False, parse_mode = 'HTML', reply_markup = inline_buttons_download(user_language))
        download_send_message
        chat_id = message.chat.id
        message_id = download_send_message['message_id']
        async with state.proxy() as data:
            data['download_csv'] = {'chat_id': chat_id,
                                        'message_id': message_id}
    # events
    logging.info(f'Пользователь выбирает способ скачивания csv | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='asking_download_csv')


# Ответ на колбэк скачивания - что скачиваем?
@dp.callback_query_handler(filters.Text(contains=['download_']), state=FSMDownload.download_csv) 
@users_access
async def download(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    download_type = callback_query.data

    if download_type == 'download_all':
        # events
        logging.info(f'Скачиваем файл для пользователя в csv | {user_id=}, {time.asctime()}')
        await event_recording(user_id=user_id, event='sending_downloaded_csv')
        
        group = message_texts.MSG_ALL_WORDS
        answer_message = message_texts.MSG_DOWNLOAD_CSV_ALL[user_language]
        await callback_query.message.answer(answer_message, reply=False, parse_mode = 'HTML')

        fp = await download_csv(user_id, group)
        doc = open(fp, 'rb')
        await callback_query.message.answer_document(document=doc)
        await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
        await callback_query.answer() # завершаем коллбэк
        doc.close()
        if os.path.isfile(fp):
            os.remove(fp)
            logging.info(f'{fp} deleted. | {user_id=}, {time.asctime()}')
        else:
            logging.info(f'{fp} not found. | {user_id=}, {time.asctime()}')
        await state.finish()
    else:
        user_groups = await all_user_groups(user_id, state)
        answer_message = message_texts.MSG_DOWNLOAD_CSV_GROUPS[user_language].format(user_groups=user_groups['message_groups'])
        await callback_query.message.answer(answer_message, parse_mode = 'HTML')
        await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
        await callback_query.answer() # завершаем коллбэк
        await state.finish()
        await FSMDownload.download_csv_group_selection.set()
        async with state.proxy() as data:
            data['download_csv_group_selection'] = {'message_groups': user_groups['message_groups'],
                                        'groups': user_groups['groups'],
                                        'min_group_num': user_groups['min_group_num'],
                                        'max_group_num': user_groups['max_group_num'],
                                        'message': int()}

# Ловим группу для скачивания csv
@dp.message_handler(state=FSMDownload.download_csv_group_selection)
@users_access
async def download(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    user_message = message.text

    if user_message.isnumeric():
        user_message = int(user_message)
        async with state.proxy() as data:
            min_group_num = data['download_csv_group_selection']['min_group_num']
            max_group_num = data['download_csv_group_selection']['max_group_num'] + 1
        if user_message in range(min_group_num, max_group_num):
            # events
            logging.info(f'Скачиваем файл по группе в csv | {user_id=}, {time.asctime()}')
            await event_recording(user_id=user_id, event='sending_downloaded_csv')

            group_num = user_message
            group = data['download_csv_group_selection']['groups'][group_num]
            answer_message = message_texts.MSG_DOWNLOAD_CSV_GROUP[user_language].format(group=group)
            await message.reply(answer_message, reply=False, parse_mode = 'HTML')

            fp = await download_csv(user_id, group)
            doc = open(fp, 'rb')
            await message.answer_document(document=doc)
            doc.close()
            await delete_file_on_server(user_id, fp) # удаляем скаченный файл
            await state.finish()
        else:
            logging.info(f'Написан не существующий номер группы | {user_id=}, {time.asctime()}')
            answer_message = message_texts.MSG_CARDS_GET_GROUPS_WRONG1[user_language]
            await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    else:
        logging.info(f'Написан не номер группы | {user_id=}, {time.asctime()}')
        answer_message = message_texts.MSG_CARDS_GET_GROUPS_WRONG2[user_language]
        await message.reply(answer_message, reply=False, parse_mode = 'HTML')

# Ответ на колбэк скачивания - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMDownload.download_csv) 
@users_access
async def cancel_download(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = message_texts.MSG_DOWNLOAD_CSV_CONCEL[user_language]
    await state.finish()
    await callback_query.message.answer(answer_message)


# Карточки для напоминания слов
@dp.message_handler(commands=['cards'], state=None)
@users_access
async def load_cards(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    # events
    logging.info(f'Запущены карточки | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='launching_cards')

    chat_id = message.chat.id
    index_num = 0
    group = await actual_user_group(user_id)
    users_cards = cards(user_id, group)
    if not users_cards:
        answer_message = message_texts.MSG_CARDS_NO_WORDS[user_language].format(group=group)
        await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    else:
        total_num = len(users_cards)
        answer_message = message_texts.MSG_CARDS_INFO[user_language].format(group=group)
        await message.reply(answer_message, reply=False, parse_mode = 'HTML')

        word_for_reminder = users_cards[index_num][1]
        cards_send_message = await bot.send_message(user_id, word_for_reminder, reply_markup=inline_buttons_translation(user_language))
        cards_send_message
        await FSMCard.word_for_reminder.set()
        async with state.proxy() as data:
            data['word_for_reminder'] = {'users_cards': users_cards, 
                                         'total_num': total_num, 
                                         'index_num': index_num, 
                                         'chat_id': chat_id, 
                                         'cards_send_message': cards_send_message}
        # events
        logging.info(f'Показ слова в карточках | {user_id=}, {time.asctime()}')
        await event_recording(user_id=user_id, word_id=users_cards[index_num][0], event='sending_word')
    
    # Обновляем след. дату уведомления
    await update_next_notification(user_id)

# Ответ на колбэк показываем перевод
@dp.callback_query_handler(filters.Text(contains=['translation']), state=FSMCard.word_for_reminder) 
@users_access
async def translation(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    
    async with state.proxy() as data:
        users_cards = data['word_for_reminder']['users_cards']
        index_num = data['word_for_reminder']['index_num']
        chat_id = data['word_for_reminder']['chat_id']
        cards_send_message = data['word_for_reminder']['cards_send_message']
        user_id = callback_query.from_user.id
        await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
        cards_edited_message_id = cards_send_message['message_id']
        cards_edited_message_text = cards_send_message['text'] + " | " + users_cards[index_num][2]
        await bot.edit_message_text(text=cards_edited_message_text, chat_id=chat_id, message_id=cards_edited_message_id, reply_markup=inline_buttons_reminder(user_language))
        await callback_query.answer(users_cards[index_num][1]) # завершаем коллбэк
        # events
        logging.info(f'Показан перевод карточки | {user_id=}, {time.asctime()}')
        await event_recording(user_id=user_id, word_id=users_cards[index_num][0], event='showing_translation')

# Ответ на колбэк следующее слово
@dp.callback_query_handler(filters.Text(contains=['remind in']), state=FSMCard.word_for_reminder) 
@users_access
async def next_cards(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):

    async with state.proxy() as data:
        users_cards = data['word_for_reminder']['users_cards']
        total_num = data['word_for_reminder']['total_num']
        index_num = data['word_for_reminder']['index_num']
        cards_send_message = data['word_for_reminder']['cards_send_message']

        user_id = callback_query.from_user.id
        remind_in = callback_query.data
        await update_remind_date(user_id, word_id = users_cards[index_num][0], remind_in = remind_in, rev = users_cards[index_num][3])
        await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
        await callback_query.answer(users_cards[index_num][1]) # завершаем коллбэк
        # events
        logging.info(f'Обновлена дата карточки | {user_id=}, {time.asctime()}')
        await event_recording(user_id=user_id, word_id=users_cards[index_num][0], event='selecting_reminder_interval')

        index_num += 1
        if index_num > total_num - 1:
            answer_message = message_texts.MSG_CARDS_FINISH[user_language]
            await state.finish()
            await callback_query.message.answer(answer_message)
            # DONATE
            answer_message_donate = message_texts.MSG_DONATE[user_language]
            await callback_query.message.answer(answer_message_donate)
        else:
            word_for_reminder = users_cards[index_num][1]
            cards_send_message = await bot.send_message(user_id, word_for_reminder, reply_markup=inline_buttons_translation(user_language))
            cards_send_message
            async with state.proxy() as data:
                data['word_for_reminder']['index_num'] = index_num
                data['word_for_reminder']['cards_send_message'] = cards_send_message

# Ответ на колбэк - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMCard.word_for_reminder) 
@users_access
async def cancel_cards(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = message_texts.MSG_CARDS_CANCEL[user_language]
    await state.finish()
    await callback_query.message.answer(answer_message)
    # DONATE
    answer_message_donate = message_texts.MSG_DONATE[user_language]
    await callback_query.message.answer(answer_message_donate)
    # events
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='cancel - cards')



# Изменение группы слов для режима карточек - показываем все группы
@dp.message_handler(commands=['cards_group'], state='*')
@users_access
async def print_cards_group(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id

    # выход из режима карточек, если он был включены
    current_state = await state.get_state()
    if current_state == 'FSMCard:word_for_reminder':
        async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
            chat_id = data['word_for_reminder']['chat_id']
            message_id = data['word_for_reminder']['cards_send_message']["message_id"]
        await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
        await state.finish()
    else:
        await state.finish()

    # переход в режим изменения группы
    user_groups = await all_user_groups(user_id, state)  
    answer_message = message_texts.MSG_CARDS_USER_GROUPS[user_language].format(user_groups=user_groups['message_groups'])
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    await FSMCard.change_cards_group.set()
    async with state.proxy() as data:
        data['change_cards_group'] = {'message_groups': user_groups['message_groups'],
                                      'groups': user_groups['groups'],
                                      'min_group_num': user_groups['min_group_num'],
                                      'max_group_num': user_groups['max_group_num'],
                                      'message': int(),
                                      'current_state': current_state}
    # events
    logging.info(f'Показываем все группы слов для режима карточек | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='sending_group_of_words')

# Изменение группы слов для режима карточек - ловим группу и меняем
@dp.message_handler(state=FSMCard.change_cards_group)
@users_access
async def get_cards_group(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    user_message = message.text
    if user_message.isnumeric():
        user_message = int(user_message)
        async with state.proxy() as data:
            current_state = data['change_cards_group']['current_state']
            min_group_num = data['change_cards_group']['min_group_num']
            max_group_num = data['change_cards_group']['max_group_num'] + 1
        if user_message in range(min_group_num, max_group_num):
            logging.info(f'Изменена группа слов для режима карточек | {user_id=}, {time.asctime()}')
            async with state.proxy() as data:
                data['change_cards_group']['message'] = user_message
            group = await change_cards_group(user_id, state) # меняем группу в БД
            if current_state == 'FSMDownload:download_csv':
                answer_message = message_texts.MSG_DOWNLOAD_CSV_GROUPS[user_language].format(group=group)
            else:
                answer_message = message_texts.MSG_CARDS_GET_GROUPS[user_language].format(group=group)
            await state.finish()
        else:
            logging.info(f'Написан не существующий номер группы | {user_id=}, {time.asctime()}')
            answer_message = message_texts.MSG_CARDS_GET_GROUPS_WRONG1[user_language]
    else:
        logging.info(f'Написан не номер группы | {user_id=}, {time.asctime()}')
        answer_message = message_texts.MSG_CARDS_GET_GROUPS_WRONG2[user_language]
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')


# Вывести дублирующиеся слова
@dp.message_handler(commands=['duplicates'])
@users_access
async def duplicates(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await select_duplicate(user_id, user_language)
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    # events
    logging.info(f'Вывод дублирующихся слов | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='sending_duplicates')


# Изменение группы у слова
@dp.message_handler(commands=['change_group'], state=None)
@users_access
async def change_group_for_words(message: types.Message, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    if not words_exists(user_id):
        answer_message = message_texts.MSG_NO_WORDS[user_language]
        await message.reply(answer_message, reply=False)
    else:
        await FSMChangeGroup.change_group.set()
        logging.info(f'Режим изменения группы у слов | {user_id=}, {time.asctime()}')
        answer_message = message_texts.CHANGE_GROUP_FOR_WORDS[user_language]
        await message.reply(answer_message, reply=False, parse_mode = 'HTML', reply_markup=inline_buttons_chenge_type(user_language))
        # update_group

# ТУТ ДОБАВИТЬ ЛОГИКУ!!

# Ответ на колбэк изменения группы у слова - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMChangeGroup.change_group) 
@users_access
async def cancel_change_grpup(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = message_texts.CHANGE_GROUP_FOR_WORDS_CONCEL[user_language]
    await state.finish()
    await callback_query.message.answer(answer_message)


# Настройка уведомления
@dp.message_handler(commands=['notifications'], state=None)
@users_access
async def notifications(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    await FSMNotif.notifications.set()
    notification_interval = await actual_user_notification_interval(user_id)
    if notification_interval.isnumeric():
        notification_interval = int(notification_interval)
        if notification_interval == 1: notification_freq = message_texts.KB_NOTIFICATIONS_DAY[user_language]
        elif notification_interval == 2: notification_freq = message_texts.KB_NOTIFICATIONS_2DAYS[user_language]
        elif notification_interval == 7: notification_freq = message_texts.KB_NOTIFICATIONS_WEEK[user_language]
        elif notification_interval == 30: notification_freq = message_texts.KB_NOTIFICATIONS_MONTH[user_language]
        else: notification_freq = ''
        add_info = message_texts.MSG_NOTIFICATIONS_ADD_INFO[user_language]
    else: 
        notification_freq = message_texts.KB_NOTIFICATIONS_NEVER[user_language]
        add_info = ""
    answer_message = message_texts.MSG_NOTIFICATIONS_INFO[user_language].format(notification_freq=notification_freq, add_info=add_info)
    await message.reply(answer_message, reply=False, parse_mode = 'HTML', reply_markup=inline_buttons_notifications(user_language))
    # events
    logging.info(f'Настройка частоты уведомлений | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='asking_notifications')

# Ответ на колбэк настройка уведомлений - установка новой частоты
@dp.callback_query_handler(filters.Text(contains=['notifications_set']), state=FSMNotif.notifications) 
@users_access
async def set_notifications(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    new_notification_interval = str(callback_query.data.split(' ', 1)[1])
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк
    await update_notification_interval(user_id, new_notification_interval) # Изменяем частоту в БД

    if new_notification_interval.isnumeric():
        new_notification_interval = int(new_notification_interval)
        if new_notification_interval == 1: notification_freq = message_texts.KB_NOTIFICATIONS_DAY[user_language]
        elif new_notification_interval == 2: notification_freq = message_texts.KB_NOTIFICATIONS_2DAYS[user_language]
        elif new_notification_interval == 7: notification_freq = message_texts.KB_NOTIFICATIONS_WEEK[user_language]
        elif new_notification_interval == 30: notification_freq = message_texts.KB_NOTIFICATIONS_MONTH[user_language]
        else: notification_freq = ''
        add_info = message_texts.MSG_NOTIFICATIONS_ADD_INFO[user_language]
        answer_message = message_texts.MSG_NOTIFICATIONS_SET[user_language].format(notification_freq=notification_freq, add_info=add_info)
    else: 
        notification_freq = message_texts.KB_NOTIFICATIONS_NEVER[user_language]
        add_info = ""
        answer_message = message_texts.MSG_NOTIFICATIONS_SET_NEVER[user_language].format(notification_freq=notification_freq, add_info=add_info)
    await state.finish()
    await callback_query.message.answer(answer_message, parse_mode = 'HTML')
    # events
    logging.info(f'Устанавливаем новую частоту уведомлений | {user_id=}, {time.asctime()}')
    await event_recording(user_id=user_id, event='setting_up_notifications')


# Ответ на колбэк настройка уведомлений - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMNotif.notifications) 
@users_access
async def cancel_set_notifications(callback_query: types.CallbackQuery, user_language: str, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = message_texts.MSG_CANCEL_NOTIFICATIONS[user_language]
    await state.finish()
    await callback_query.message.answer(answer_message)


# Отправка сообщения всем пользователям
@dp.message_handler(commands=['send_for_all'], state=None)
@auth
async def send_for_all(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Переход в режим отправки сообщений всем пользователям | {user_id=}, {time.asctime()}')
    await FSMSendForAll.send_for_all.set()
    answer_message = message_texts.MSG_SEND_FOR_ALL
    await message.reply(answer_message, reply=False)

# Ловим сообщеине, которое нужно отправить всем и отправляем его
@dp.message_handler(state=FSMSendForAll.send_for_all)
@auth
async def execute_send_for_all(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Отправляем сообщение | {user_id=}, {time.asctime()}')
    message_for_all = message.text
    user_list = await user_list_to_send_message()
    list_not_delivered = []
    count = 0
    for user_id in user_list:
        try:
            if await bot.send_message(user_id, message_for_all, parse_mode = 'HTML'):
                count += 1
            # 20 messages per second (Limit: 30 messages per second)
            await asyncio.sleep(.05)
        except:
            list_not_delivered.append(user_id)
    answer_message = message_texts.MSG_SEND_FOR_ALL_SUCCESS.format(count=count,not_delivered=list_not_delivered)
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    await state.finish()


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
    await message.reply(answer_message, reply=False)


# Донат
@dp.message_handler(commands=['donate'])
@users_access
async def donate_hendler(message: types.Message, user_language: str, *args, **kwargs):
    user_id = message.from_user.id
    await bot.send_message(user_id, message_texts.MSG_DONATE_INFO[user_language], disable_web_page_preview = True)
    # events
    logging.info(f'Донат | {user_id=} {time.asctime()}')
    await event_recording(user_id=user_id, event='donate')

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
async def echo(message: types.Message, user_language: str, *args, **kwargs):
    answer_message = message_texts.MSG_COMMAND_NOT_DEFINED[user_language]
    await message.answer(answer_message)




# расписание подготовка списка
async def sched():
    try:
        count = 0
        user_list = await user_list_to_send_notifications() # прод
        # user_list = [{'user_id': '91523724', 'notifications_interval': str(1), 'user_language': 'EN'}] # тест, заглушка для уведомлений только себе
        for user in user_list:
            if user['user_id'].isnumeric():
                try:
                    answer_message = message_texts.MSG_NOTIFICATIONS[user['user_language']]
                    if await bot.send_message(user['user_id'], answer_message):
                        count += 1
                    await update_notification_interval(user['user_id'], user['notifications_interval'])
                    # 20 messages per second (Limit: 30 messages per second)
                    await asyncio.sleep(.05)
                except:
                    pass
    except: 
        await bot.send_message('91523724', "Автор, ошибка в уведомлениях, почини!")


scheduler = AsyncIOScheduler(timezone=utc)
# scheduler.add_job(sched, trigger='cron', hour='17', minute='47') # тест
scheduler.add_job(sched, trigger='cron', hour='16', minute='45') # прод
scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)