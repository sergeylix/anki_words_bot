import time
from pytz import utc
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import message_texts
from sqlite import db_start, add_access, get_users_w_access, create_profile, words_exists,\
    insert_words, select_words, delete_word, delete_all_words, actual_user_group, all_user_groups, change_cards_group, cards,\
    update_remind_date, words_num, select_duplicate, download_csv, update_group, actual_user_notification_interval,\
        update_notification_interval, user_list_to_send_notifications, any_query

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
    change_cards_group = State()

class FSMDownload(StatesGroup):
    download_csv = State()
    download_csv_group_selection = State()

class FSMChangeGroup(StatesGroup):
    change_group = State()

class FSMNotif(StatesGroup):
    notifications = State()

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

# Что скачать
inline_buttons_download = types.InlineKeyboardMarkup(row_width=3)
download_b1 = types.InlineKeyboardButton(text=message_texts.KB_DOWNLOAD_ALL, callback_data='download_all')
download_b2 = types.InlineKeyboardButton(text=message_texts.KB_DOWNLOAD_GROUP, callback_data='download_group')
download_b3 = types.InlineKeyboardButton(text=message_texts.KB_DOWNLOAD_CANCEL, callback_data='cancel')

inline_buttons_download.add(download_b1)
inline_buttons_download.row(download_b2)
inline_buttons_download.row(download_b3)

# Для каких слов изменить группу
inline_buttons_chenge_type = types.InlineKeyboardMarkup(row_width=4)
chenge_type_b1 = types.InlineKeyboardButton(text=message_texts.KB_CHANGE_GR_ONE_WORD, callback_data='change_one')
chenge_type_b2 = types.InlineKeyboardButton(text=message_texts.KB_CHANGE_GR_IN_GR, callback_data='change_group')
chenge_type_b3 = types.InlineKeyboardButton(text=message_texts.KB_CHANGE_GR_ALL, callback_data='change_all')
chenge_type_b4 = types.InlineKeyboardButton(text=message_texts.KB_CHANGE_GR_CANCEL, callback_data='cancel')

inline_buttons_chenge_type.add(chenge_type_b1)
inline_buttons_chenge_type.row(chenge_type_b2)
inline_buttons_chenge_type.row(chenge_type_b3)
inline_buttons_chenge_type.row(chenge_type_b4)


# Настройка частоты уведомлений
inline_buttons_notifications = types.InlineKeyboardMarkup(row_width=4)
notifications_b1 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_DAY, callback_data='notifications_set 1')
notifications_b2 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_2DAYS, callback_data='notifications_set 2')
notifications_b3 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_WEEK, callback_data='notifications_set 7')
notifications_b4 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_MONTH, callback_data='notifications_set 30')
notifications_b5 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_NEVER, callback_data='notifications_set never')
notifications_b6 = types.InlineKeyboardButton(text=message_texts.KB_NOTIFICATIONS_CONCEL, callback_data='cancel')

inline_buttons_notifications.add(notifications_b1, notifications_b2)
inline_buttons_notifications.row(notifications_b3, notifications_b4)
inline_buttons_notifications.row(notifications_b5)
inline_buttons_notifications.row(notifications_b6)


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
        types.BotCommand("cards", "Режим карточек"),
        types.BotCommand("words", "Последние 15 слов"),
        types.BotCommand("words_num", "Количество слов"),
        types.BotCommand("duplicates", "Дублирующиеся слова"),
        types.BotCommand("download_csv", "Скачать все слова в csv"),
        types.BotCommand("delete", "Режим удаления одного слова"),
        types.BotCommand("delete_all", "Режим удаления всех слов"),
        types.BotCommand("cancel", "Отмена"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("notifications", "Настройка уведомлений"),
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
    await bot.send_message(user_id, message_texts.MSG_START, parse_mode = 'HTML')


# Хэлп
@dp.message_handler(commands=['help'])
@users_access
async def help_hendler(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Хэлп | {user_id=} {time.asctime()}')

    await bot.send_message(user_id, message_texts.MSG_HELP, parse_mode = 'HTML')


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
        async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
            chat_id = data['word_for_reminder']['chat_id']
            message_id = data['word_for_reminder']['cards_send_message']['message_id']
        await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
        answer_message = message_texts.MSG_CANCEL_REMINDER
    elif current_state == 'FSMCard:change_cards_group':
        answer_message = message_texts.MSG_CANCEL_CHANGE_GROUP
    elif current_state == 'FSMDownload:download_csv':
        async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
            chat_id = data['download_csv']['chat_id']
            message_id = data['download_csv']['message_id']
        await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
        answer_message = message_texts.MSG_CANCEL_CHANGE_DOWNLOAD
    else:
        answer_message = message_texts.MSG_CANCEL_GENETAL
    await state.finish()
    await message.reply(answer_message, reply=False)


# Добавление слова
@dp.message_handler(state={None, FSMDelete.word_for_delete, 
                           FSMDeleteAll.delete_all, 
                           FSMDownload.download_csv, 
                           FSMDownload.download_csv_group_selection,
                           FSMCard.word_for_reminder, 
                           FSMCard.change_cards_group}, 
                    regexp='.=.')
@users_access
async def word_insert(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    user_message = message.text
    logging.info(f'Добавление слова | {user_id=}, {user_full_name=}, {user_message} {time.asctime()}')
    
    answer_message = message_texts.MSG_INSERT_WORD
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
            answer_message = message_texts.MSG_CANCEL_REMINDER
            logging.info(f'Вышел из режима карточек | {user_id=}, {time.asctime()}')
        elif current_state in ['FSMCard:change_cards_group','FSMDownload:download_csv_group_selection']:
            answer_message = message_texts.MSG_CANCEL_CHANGE_GROUP
            logging.info(f'Вышел из режима изменения групп | {user_id=}, {time.asctime()}')
        elif current_state in ['FSMDelete:word_for_delete','FSMDeleteAll:delete_all']:
            answer_message = message_texts.MSG_CANCEL_DELETE
            logging.info(f'Вышел из режима удаления | {user_id=}, {time.asctime()}')
        elif current_state == 'FSMDownload:download_csv':
            async with state.proxy() as data: # достаем id чата и сообщения, чтобы скрыть инлайновую клавиатуру
                chat_id = data['download_csv']['chat_id']
                message_id = data['download_csv']['message_id']
            await bot.edit_message_reply_markup(chat_id = chat_id, message_id = message_id, reply_markup = None) # удаляем инлайновую клавиатуру
            answer_message = message_texts.MSG_CANCEL_CHANGE_DOWNLOAD
            logging.info(f'Вышел из режима скачивания | {user_id=}, {time.asctime()}')
        else:
            answer_message = message_texts.MSG_CANCEL_GENETAL
        await state.finish()
        await message.reply(answer_message, reply=False)


# Удаление слова
@dp.message_handler(commands=['delete'], state=None)
@users_access
async def word_delete(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Удаление слова | {user_id=}, {time.asctime()}')
    if not words_exists(user_id):
        answer_message = message_texts.MSG_NO_WORDS
    else:
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
    if not words_exists(user_id):
        answer_message = message_texts.MSG_NO_WORDS
    else:
        await FSMDeleteAll.delete_all.set()
        answer_message = message_texts.MSG_DELETE_ALL
    await message.reply(answer_message, reply=False)

# Ловим запуск процесса удаления всех слов
@dp.message_handler(commands=['delete_all'], state=FSMDeleteAll.delete_all)
@users_access
async def delete_all_again(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Запущен процесс удаления всех слов | {user_id=}, {time.asctime()}')
    answer_message = message_texts.MSG_DELETE_ALL_X2
    await message.reply(answer_message)

# Ловим подтверждение, что нужно удалить все слова
@dp.message_handler(commands=['yes'], state=FSMDeleteAll.delete_all)
@users_access
async def delete_all_again(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Все слова удалены | {user_id=}, {time.asctime()}')
    answer_message = await delete_all_words(user_id)
    await state.finish()
    await message.reply(answer_message, reply=False)


# Выводим список слов
@dp.message_handler(commands=['words'])
@users_access
async def print_my_words(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await select_words(user_id)

    logging.info(f'Выводим список сохраненных слов | {user_id=}, {time.asctime()}')
    
    await message.reply(answer_message, reply=False)


# Выводим кол-во слов всего
@dp.message_handler(commands=['words_num'])
@users_access
async def print_my_words_num(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await words_num(user_id)
    logging.info(f'Выводим кол-во сохраненных слов | {user_id=}, {time.asctime()}')
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')


# Скачиваем слова в csv
@dp.message_handler(commands=['download_csv'], state=None)
@users_access
async def download(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Пользователь выбирает способ скачивания csv | {user_id=}, {time.asctime()}')
    if not words_exists(user_id):
        answer_message = message_texts.MSG_NO_WORDS
        await message.reply(answer_message, reply=False)
    else:
        await FSMDownload.download_csv.set()
        answer_message = message_texts.MSG_DOWNLOAD_CSV
        download_send_message = await message.reply(answer_message, reply=False, parse_mode = 'HTML', reply_markup = inline_buttons_download)
        download_send_message
        chat_id = message.chat.id
        message_id = download_send_message['message_id']
        async with state.proxy() as data:
            data['download_csv'] = {'chat_id': chat_id,
                                        'message_id': message_id}


# Ответ на колбэк скачивания - что скачиваем?
@dp.callback_query_handler(filters.Text(contains=['download_']), state=FSMDownload.download_csv) 
@users_access
async def download(callback_query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    download_type = callback_query.data

    if download_type == 'download_all':
        logging.info(f'Скачиваем файл для пользователя в csv | {user_id=}, {time.asctime()}')
        group = message_texts.MSG_ALL_WORDS
        answer_message = message_texts.MSG_DOWNLOAD_CSV_ALL
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
        answer_message = message_texts.MSG_DOWNLOAD_CSV_GROUPS.format(user_groups=user_groups['message_groups'])
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
async def download(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    user_message = message.text

    if user_message.isnumeric():
        user_message = int(user_message)
        async with state.proxy() as data:
            min_group_num = data['download_csv_group_selection']['min_group_num']
            max_group_num = data['download_csv_group_selection']['max_group_num'] + 1
        if user_message in range(min_group_num, max_group_num):
            logging.info(f'Скачиваем файл по группе в csv | {user_id=}, {time.asctime()}')
            group_num = user_message
            group = data['download_csv_group_selection']['groups'][group_num]
            answer_message = message_texts.MSG_DOWNLOAD_CSV_GROUP.format(group=group)
            await message.reply(answer_message, reply=False, parse_mode = 'HTML')

            fp = await download_csv(user_id, group)
            doc = open(fp, 'rb')
            await message.answer_document(document=doc)
            doc.close()
            if os.path.isfile(fp):
                os.remove(fp)
                logging.info(f'{fp} deleted. | {user_id=}, {time.asctime()}')
            else:
                logging.info(f'{fp} not found. | {user_id=}, {time.asctime()}')
            await state.finish()
        else:
            logging.info(f'Написан не существующий номер группы | {user_id=}, {time.asctime()}')
            answer_message = message_texts.MSG_CARDS_GET_GROUPS_WRONG1
            await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    else:
        logging.info(f'Написан не номер группы | {user_id=}, {time.asctime()}')
        answer_message = message_texts.MSG_CARDS_GET_GROUPS_WRONG2
        await message.reply(answer_message, reply=False, parse_mode = 'HTML')

# Ответ на колбэк скачивания - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMDownload.download_csv) 
@users_access
async def cancel_download(callback_query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = message_texts.MSG_DOWNLOAD_CSV_CONCEL
    await state.finish()
    await callback_query.message.answer(answer_message)


# Карточки для напоминания слов
@dp.message_handler(commands=['cards'], state=None)
@users_access
async def load_cards(message: types.Message, state: FSMContext, *args, **kwargs):

    user_id = message.from_user.id
    chat_id = message.chat.id
    logging.info(f'Запущены карточки | {user_id=}, {time.asctime()}')
    index_num = 0
    group = await actual_user_group(user_id)
    users_cards = cards(user_id, group)
    if not users_cards:
        answer_message = message_texts.MSG_CARDS_NO_WORDS.format(group=group)
        await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    else:
        total_num = len(users_cards)
        answer_message = message_texts.MSG_CARDS_INFO.format(group=group)
        await message.reply(answer_message, reply=False, parse_mode = 'HTML')

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


# Изменение группы слов для режима карточек - показываем все группы
@dp.message_handler(commands=['cards_group'], state='*')
@users_access
async def print_cards_group(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Показываем все группы слов для режима карточек | {user_id=}, {time.asctime()}')

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
    answer_message = message_texts.MSG_CARDS_USER_GROUPS.format(user_groups=user_groups['message_groups'])
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')
    await FSMCard.change_cards_group.set()
    async with state.proxy() as data:
        data['change_cards_group'] = {'message_groups': user_groups['message_groups'],
                                      'groups': user_groups['groups'],
                                      'min_group_num': user_groups['min_group_num'],
                                      'max_group_num': user_groups['max_group_num'],
                                      'message': int(),
                                      'current_state':current_state}

# Изменение группы слов для режима карточек - ловим группу и меняем
@dp.message_handler(state=FSMCard.change_cards_group)
@users_access
async def get_cards_group(message: types.Message, state: FSMContext, *args, **kwargs):
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
                answer_message = message_texts.MSG_DOWNLOAD_CSV_GROUPS.format(group=group)
            else:
                answer_message = message_texts.MSG_CARDS_GET_GROUPS.format(group=group)
            await state.finish()
        else:
            logging.info(f'Написан не существующий номер группы | {user_id=}, {time.asctime()}')
            answer_message = message_texts.MSG_CARDS_GET_GROUPS_WRONG1
    else:
        logging.info(f'Написан не номер группы | {user_id=}, {time.asctime()}')
        answer_message = message_texts.MSG_CARDS_GET_GROUPS_WRONG2
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')


# Вывести дублирующиеся слова
@dp.message_handler(commands=['duplicates'])
@users_access
async def duplicates(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    answer_message = await select_duplicate(user_id)
    logging.info(f'Вывод дублирующихся слов | {user_id=}, {time.asctime()}')
    await message.reply(answer_message, reply=False, parse_mode = 'HTML')


# Изменение группы у слова
@dp.message_handler(commands=['change_group'], state=None)
@users_access
async def change_group_for_words(message: types.Message, state: FSMContext, *args, **kwargs):
    user_id = message.from_user.id
    if not words_exists(user_id):
        answer_message = message_texts.MSG_NO_WORDS
        await message.reply(answer_message, reply=False)
    else:
        await FSMChangeGroup.change_group.set()
        logging.info(f'Режим изменения группы у слов | {user_id=}, {time.asctime()}')
        answer_message = message_texts.CHANGE_GROUP_FOR_WORDS
        await message.reply(answer_message, reply=False, parse_mode = 'HTML', reply_markup=inline_buttons_chenge_type)
        # update_group

# ТУТ ДОБАВИТЬ ЛОГИКУ!!

# Ответ на колбэк изменения группы у слова - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMChangeGroup.change_group) 
@users_access
async def cancel_change_grpup(callback_query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = message_texts.CHANGE_GROUP_FOR_WORDS_CONCEL
    await state.finish()
    await callback_query.message.answer(answer_message)


# Уведомления
@dp.message_handler(commands=['notifications'], state=None)
@users_access
async def notifications(message: types.Message, *args, **kwargs):
    user_id = message.from_user.id
    logging.info(f'Настройка частоты уведомлений | {user_id=} {time.asctime()}')
    await FSMNotif.notifications.set()
    notification_interval = await actual_user_notification_interval(user_id)
    if notification_interval.isnumeric():
        notification_interval = int(notification_interval)
        if notification_interval == 1: notification_freq = message_texts.KB_NOTIFICATIONS_DAY
        elif notification_interval == 2: notification_freq = message_texts.KB_NOTIFICATIONS_2DAYS
        elif notification_interval == 7: notification_freq = message_texts.KB_NOTIFICATIONS_WEEK
        elif notification_interval == 30: notification_freq = message_texts.KB_NOTIFICATIONS_MONTH
        else: notification_freq = ''
    else: notification_freq = message_texts.KB_NOTIFICATIONS_NEVER
    answer_message = message_texts.MSG_NOTIFICATIONS_INFO.format(notification_freq=notification_freq)
    await message.reply(answer_message, reply=False, parse_mode = 'HTML', reply_markup=inline_buttons_notifications)

# Ответ на колбэк настройка уведомлений - установка новой частоты
@dp.callback_query_handler(filters.Text(contains=['notifications_set']), state=FSMNotif.notifications) 
@users_access
async def cancel_set_notifications(callback_query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    new_notification_interval = str(callback_query.data.split(' ', 1)[1])
    logging.info(f'Устанавливаем новую частоту уведомлений | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк
    await update_notification_interval(user_id, new_notification_interval) # Изменяем частоту в БД

    if new_notification_interval.isnumeric():
        new_notification_interval = int(new_notification_interval)
        if new_notification_interval == 1: notification_freq = message_texts.KB_NOTIFICATIONS_DAY
        elif new_notification_interval == 2: notification_freq = message_texts.KB_NOTIFICATIONS_2DAYS
        elif new_notification_interval == 7: notification_freq = message_texts.KB_NOTIFICATIONS_WEEK
        elif new_notification_interval == 30: notification_freq = message_texts.KB_NOTIFICATIONS_MONTH
        else: notification_freq = ''
        answer_message = message_texts.MSG_NOTIFICATIONS_SET.format(notification_freq=notification_freq)
    else: 
        notification_freq = message_texts.KB_NOTIFICATIONS_NEVER
        answer_message = message_texts.MSG_NOTIFICATIONS_SET_NEVER.format(notification_freq=notification_freq)
        
    await state.finish()
    await callback_query.message.answer(answer_message, parse_mode = 'HTML')


# Ответ на колбэк настройка уведомлений - отмена
@dp.callback_query_handler(filters.Text(contains=['cancel']), state=FSMNotif.notifications) 
@users_access
async def cancel_set_notifications(callback_query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_id = callback_query.from_user.id
    logging.info(f'Отмена | {user_id=}, {time.asctime()}')
    await callback_query.message.delete_reply_markup() # удаляем инлайновую клавиатуру
    await callback_query.answer() # завершаем коллбэк

    answer_message = message_texts.MSG_CANCEL_NOTIFICATIONS
    await state.finish()
    await callback_query.message.answer(answer_message)


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




# расписание
async def sched():
    try:
        answer_message = message_texts.MSG_NOTIFICATIONS
        # user_list = await user_list_to_send_notifications()
        user_list = [{'user_id': '91523724', 'notifications_interval': str(1)}] # заглушка для уведомлений только себе
        for user in user_list:
            if user['user_id'].isnumeric():
                try:
                    await bot.send_message(user['user_id'], answer_message)
                    await update_notification_interval(user['user_id'], user['notifications_interval'])
                except:
                    pass
    except: 
        await bot.send_message('91523724', "Автор, ошибка в уведомлениях, почини!")


scheduler = AsyncIOScheduler(timezone=utc)
# scheduler.add_job(sched, trigger='cron', hour='10', minute='46') # тест
scheduler.add_job(sched, trigger='cron', hour='16', minute='45') # прод
scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)