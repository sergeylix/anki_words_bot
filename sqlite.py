from datetime import datetime, timedelta
from random import shuffle
import time
import os
import pandas as pd
import sqlite3 as sq

from fasttext.FastText import _FastText
import message_texts


# Определяем язык текста
def define_language(string: str) -> str:
    model = _FastText(model_path='lid.176.ftz')
    leng = model.predict(string, k=1)[0][0]
    return leng



async def db_start():
    global db, cur

    db = sq.connect('anki_words')
    cur = db.cursor()

    # Создание таблицы с доступами
    query = """CREATE TABLE IF NOT EXISTS access(
	                user_id TEXT PRIMARY KEY,
	                access INTEGER DEFAULT "1" NOT NULL,
	                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)"""
    cur.execute(query)
    db.commit()

    # Создание таблицы с типом доступа: автоматический или нет
    query = """CREATE TABLE IF NOT EXISTS auth_access(
                    is_auth_access INTEGER DEFAULT "1" NOT NULL)"""
    cur.execute(query)
    db.commit()

    # Добавляем в таблицу с доступами флаг 0 - т.е. автоматическое открытие доступа
    query = """SELECT is_auth_access FROM auth_access LIMIT 1"""
    is_auth_access = cur.execute(query).fetchone()
    if not is_auth_access:
        query = """INSERT INTO auth_access(is_auth_access) VALUES(0)"""
        cur.execute(query)
        db.commit()

    # В доступы добавляем автора бота
    auth_id = '91523724'
    if not access_exists(auth_id):
        query = """INSERT INTO access(user_id) VALUES('{key}')"""
        cur.execute(query.format(key=auth_id))
        db.commit()

    # Создание таблицы с пользователями
    query = """CREATE TABLE IF NOT EXISTS profile(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_id TEXT, 
                    full_name TEXT,
                    last_activity TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)"""
    cur.execute(query)
    db.commit()

    # Создание таблицы со словами
    query = """CREATE TABLE IF NOT EXISTS words(
                    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    user_added_word TEXT,
                    word TEXT,
                    translation TEXT,
                    category TEXT,
                    is_uploaded_from_file INTEGER,
                    num_click_first_button INTEGER,
                    num_click_second_button INTEGER,
                    num_click_third_button INTEGER,
                    num_click_fourth_button INTEGER,
                    next_reminder_interval INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    reminder_date TIMESTAMP,
                    update_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES profile(user_id))"""
    cur.execute(query)
    db.commit()

    # Создание таблицы с группами
    query = """CREATE TABLE IF NOT EXISTS word_groups(
                    user_id TEXT PRIMARY KEY,
                    actual_category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    update_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES profile(user_id))"""
    cur.execute(query)
    db.commit()

    # Создание таблицы уведомлений
    query = """CREATE TABLE IF NOT EXISTS notifications(
					user_id TEXT PRIMARY KEY,
                    notifications_interval INTEGER,
                    next_notifications_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    update_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES profile(user_id))"""
    cur.execute(query)
    db.commit()

    # Получаем список пользователей, у которых нет записи в таблице уведомлений и добавляем им запись
    query = """SELECT a.user_id 
                    FROM profile a
                    LEFT JOIN notifications b ON a.user_id = b.user_id
                    WHERE b.user_id IS NULL"""
    for user in cur.execute(query).fetchall():
        user_id = user[0]
        notifications_interval = 7 # week
        next_notifications_date = (datetime.utcnow() + timedelta(days=notifications_interval))
        created_at = datetime.utcnow()
        update_date = created_at
        cur.execute("INSERT INTO notifications(user_id, notifications_interval, next_notifications_date, created_at, update_date) VALUES(?, ?, ?, ?, ?)", 
                    (user_id, notifications_interval, next_notifications_date, created_at, update_date))
        db.commit()

    # Создание таблицы с файлами бота
    query = """CREATE TABLE IF NOT EXISTS files(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT,
                    file_name TEXT,
                    file_description TEXT,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    update_date TIMESTAMP)"""
    cur.execute(query)
    db.commit()

    # Создание таблицы событий
    query = """CREATE TABLE IF NOT EXISTS events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_id TEXT,
                    word_id TEXT,
                    event TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES profile(user_id))"""
    cur.execute(query)
    db.commit()

    # Создание таблицы с языками интерфейса у пользователя
    query = """CREATE TABLE IF NOT EXISTS user_language(
                    user_id TEXT PRIMARY KEY,
                    language TEXT DEFAULT "EN" NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    update_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES profile(user_id))"""
    cur.execute(query)
    db.commit()


# Получаем список файлов из БД
async def get_files(file_name: str = None) -> list:
    if not file_name:
        file_rows = []
        query = """WITH t1 as (
                    SELECT file_id,
                        file_name,
                        ROW_NUMBER() OVER(PARTITION BY file_name ORDER BY created_at) AS rn
                    FROM files
                    )
                    SELECT file_id, file_name
                    FROM t1
                    WHERE rn = 1
                    ORDER BY file_name;
                    """
        file_rows = cur.execute(query).fetchall()
        return file_rows
    else:
        file_rows = []
        query = """SELECT file_id
                    FROM files
                    WHERE file_name = '{file_name}'
                    ORDER BY created_at
                    LIMIT 1
                    """
        file_rows = cur.execute(query.format(file_name=file_name)).fetchone()
        return file_rows


# Добавление строчки в БД с имеющимся файлом
async def add_file_row(file_id: str, file_name: str, file_description: str, file_path: str):
    created_at = datetime.utcnow()
    update_date = created_at
    cur.execute("INSERT INTO files(file_id, file_name, file_description, file_path, created_at, update_date) VALUES(?, ?, ?, ?, ?, ?)", 
                (file_id, file_name, file_description, file_path, created_at, update_date))
    db.commit()

# Обновление file_id в БД
async def update_file_row(file_name: str, file_id_new: str):
    update_date = datetime.utcnow()
    query = """UPDATE files SET file_id = ?, update_date = ? WHERE file_name == ?"""
    cur.execute(query, (file_id_new, update_date, file_name))
    db.commit()


# Получаем список пользователей с доступами
# async def get_users_w_access() -> list:
#         users_w_access = []
#         query = """SELECT user_id FROM access WHERE access = '{flg}'"""
#         for user in cur.execute(query.format(flg=1)).fetchall():
#             users_w_access.append(int(user[0]))
#         return users_w_access


async def get_users_w_access() -> list:
        users_w_access = []
        users_info = {}
        info = {}
        query = """SELECT a.user_id, b.language
                    FROM access a
                    LEFT JOIN user_language b on a.user_id = b.user_id
                    WHERE a.access = '{flg}'"""
        for user in cur.execute(query.format(flg=1)).fetchall():
            info = {'language': str(user[1])}
            users_info[int(user[0])] = info
            users_w_access.append(int(user[0]))
        return users_w_access, users_info






# Получаем тип пользователя
async def get_auth_access() -> int:
    query = """SELECT is_auth_access FROM auth_access LIMIT 1"""
    is_auth_access = cur.execute(query.format(flg=1)).fetchone()[0]
    return int(is_auth_access)


# Проверка, что существует доступ у пользователя
def access_exists(user_id: str) -> bool:
    user = cur.execute("SELECT 1 FROM access WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        access_exists=False
    else:
        access_exists=True
    return access_exists


# Проверка, что существует профиль у пользователя
def profile_exists(user_id: str) -> bool:
    user = cur.execute("SELECT 1 FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        profile_exists=False
    else:
        profile_exists=True
    return profile_exists

# Проверка, что есть строчка в таблице уведомлений
def notification_exists(user_id: str) -> bool:
    notif = cur.execute("SELECT 1 FROM notifications WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not notif:
        notification_exists=False
    else:
        notification_exists=True
    return notification_exists


# Проверка, что у пользователя есть слова
def words_exists(user_id: str) -> bool:
    word = cur.execute("SELECT 1 FROM words WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not word:
        words_exists=False
    else:
        words_exists=True
    return words_exists


# Проверка, что у пользователя есть язык интерфейса
def language_exists(user_id: str) -> bool:
    language = cur.execute("SELECT 1 FROM user_language WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not language:
        language_exists=False
    else:
        language_exists=True
    return language_exists


# Выдача прав пользователю
async def add_access(users:  list, flg: int):
    for user_id in users:
        user_id = str(user_id)
        if not access_exists(user_id) and user_id.isnumeric():
            query = """INSERT INTO access(user_id, access) VALUES('{key}', {flg})"""
            cur.execute(query.format(key=user_id, flg=flg))
            db.commit()
        else:
            query = """UPDATE access SET access = {flg}
            WHERE user_id == '{key}'"""
            cur.execute(query.format(flg=flg, key=user_id))
            db.commit()


# Создание профиля пользователя
async def create_profile(user_id: str, full_name: str):
    if not profile_exists(user_id):
        cur.execute("INSERT INTO profile(user_id, full_name) VALUES(?, ?)", (user_id, full_name))
        db.commit()
    
    if not language_exists(user_id):
        cur.execute("INSERT INTO user_language(user_id, language) VALUES(?, ?)", (user_id, 'EN'))
        db.commit()

    if not notification_exists(user_id):
        notifications_interval = 7 # week
        next_notifications_date = (datetime.utcnow() + timedelta(days=notifications_interval))
        created_at = datetime.utcnow()
        update_date = created_at
        cur.execute("INSERT INTO notifications(user_id, notifications_interval, next_notifications_date, created_at, update_date) VALUES(?, ?, ?, ?, ?)", 
                    (user_id, notifications_interval, next_notifications_date, created_at, update_date))
        db.commit()


# Обновляем последнюю дату активности пользователя
async def update_user_language(user_id: str, language: str):
    update_date = datetime.utcnow()
    cur.execute("UPDATE user_language SET update_date = '{update_date}', language = '{language}' WHERE user_id = '{key}'".format(update_date=update_date, language=language, key=user_id))
    db.commit()


# Обновляем язык интерфейса пользователя
async def update_last_activity(user_id: str):
    last_activity = datetime.utcnow()
    cur.execute("UPDATE profile SET last_activity = '{last_activity}' WHERE user_id = '{key}'".format(last_activity=last_activity, key=user_id))
    db.commit()


# Добавление базовых слов
async def add_basic_words(user_id: str, user_language: str):
    user_added_word = user_id
    basic_words = message_texts.MSG_ONBOARDING_BASIC_WORDS[user_language]
    for row in basic_words.split('\n'):
        words = [word.strip() for word in row.split('=', 2)]
        reminder_date = (datetime.utcnow() + timedelta(days=0))
        cur.execute("INSERT INTO words(user_id, user_added_word, word, translation, category, reminder_date) VALUES(?, ?, ?, ?, ?, ?)", (user_id, user_added_word, words[0], words[1], words[2], reminder_date))
        db.commit()

# Удаление базовых слов
async def del_basic_words(user_id: str):
        cur.execute("DELETE FROM words WHERE user_id = '{key}' AND category = 'onboarding'".format(key=user_id))
        db.commit()

# Добавление слова
async def insert_words(user_id: str, user_message: str):
    user_message = user_message.replace("\n"," ")
    words = [word.strip() for word in user_message.split('=', 2)]
    if len(words) == 2:
        words.append('')
    if define_language(words[0]) == '__label__en' and define_language(words[1]) == '__label__en':
        pass
    elif define_language(words[0]) != '__label__en' and define_language(words[1]) == '__label__en':
        words = [words[1], words[0], words[2]]
    reminder_date = (datetime.utcnow() + timedelta(days=0))
    user_added_word = user_id
    if not words[2]:
        cur.execute("INSERT INTO words(user_id, user_added_word, word, translation, reminder_date) VALUES(?, ?, ?, ?, ?)", (user_id, user_added_word, words[0], words[1], reminder_date))
    else:
        cur.execute("INSERT INTO words(user_id, user_added_word, word, translation, category, reminder_date) VALUES(?, ?, ?, ?, ?, ?)", (user_id, user_added_word, words[0], words[1], words[2], reminder_date))
    db.commit()

# Изменение слова
async def edit_words(user_id: str, word_id: int, words: list):
    update_date = datetime.utcnow()
    if not words[2]:
        cur.execute("UPDATE words SET word = ?, translation = ?, update_date = ? WHERE user_id = ? AND word_id = ?;", (words[0], words[1], update_date, user_id, word_id))
    else:
        cur.execute("UPDATE words SET word = ?, translation = ?, category = ?, update_date = ? WHERE user_id = ? AND word_id = ?;", (words[0], words[1], words[2], update_date, user_id, word_id))
    db.commit()


# Вывод последних добавленных слов
async def select_words(user_id: str, user_language: str) -> str:
    message = ""
    clients_words = ""
    if not profile_exists(user_id):
        message = message_texts.MSG_NO_WORDS[user_language]
    else:
        query = """SELECT word, translation, category
                    FROM words 
                    WHERE user_id == '{key}' 
                    ORDER BY created_at DESC 
                    LIMIT 15"""
        for word in cur.execute(query.format(key=user_id)).fetchall():
            if not word[2]:
                clients_words = clients_words + word[0] + " | " + word[1] + "\n"
            else:
                clients_words = clients_words + word[0] + " | " + word[1] + " (" +  word[2] + ")" +"\n"
        if clients_words == "":
             message = message_texts.MSG_NO_WORDS[user_language]
        else:
            message = message_texts.MSG_WORDS_LAST[user_language].format(clients_words=clients_words)
    return message


# Кол-во сохраненных слов всего
async def words_num(user_id: str, user_language: str) -> str:
    message = ""
    words_in_group = ""
    if not profile_exists(user_id):
        message = message_texts.MSG_NO_WORDS[user_language]
    else:
        # всего слов
        query = """SELECT count(word_id)
                    FROM words 
                    WHERE user_id == '{key}'"""
        words_num = cur.execute(query.format(key=user_id)).fetchone()[0]
        message = message_texts.MSG_WORDS_NUM[user_language].format(words_num=words_num)
        # в группах
        query = """SELECT category
	                    ,count(distinct a.word_id) as words_num
                    FROM words a
                    WHERE user_id = '{key}'
                    GROUP BY category
                    ORDER BY words_num DESC, category"""
        for word in cur.execute(query.format(key=user_id)).fetchall():
            words_in_group = words_in_group + str(word[0]) + " — " + str(word[1]) + "\n"
        if words_in_group:
            message = message + "\n\n" + message_texts.MSG_WORDS_NUM_GROUP[user_language].format(words_in_group=words_in_group)
    return message


# Удаление слова
async def delete_word(user_id: str, user_language: str, state, word_id: str =None) -> str:
    current_state = await state.get_state()
    if current_state == 'FSMDelete:word_for_delete':
        async with state.proxy() as data:
            try:
                query = """SELECT 1 
                            FROM words 
                            WHERE user_id == '{key}'
                            AND (translation == '{word}' OR word == '{word}')"""
                word_for_del = cur.execute(query.format(key=user_id, word=data['word_for_delete'])).fetchone()
                if not word_for_del:
                    message = message_texts.MSG_DELETE_ERROR[user_language]
                else:
                    query = """DELETE 
                                FROM words 
                                WHERE user_id == '{key}'
                                AND (translation == '{word}' OR word == '{word}')"""
                    cur.execute(query.format(key=user_id, word=data['word_for_delete']))
                    db.commit()
                    message = message_texts.MSG_DELETE_DELETED[user_language]
            except:
                message = message_texts.MSG_DELETE_ERROR_DB[user_language]
    elif current_state == 'FSMCard:word_for_reminder':
        async with state.proxy() as data:
            try:
                query = """DELETE 
                            FROM words 
                            WHERE user_id == '{key}'
                            AND word_id == '{word_id}'"""
                cur.execute(query.format(key=user_id, word_id=word_id))
                db.commit()
                message = message_texts.MSG_DELETE_DELETED[user_language]
            except:
                message = 'Error during deletion'
    else:
        message = 'Error during deletion'
    return message


# Удаление всех слов пользователя
async def delete_all_words(user_id: str, user_language: str) -> str:
    if not profile_exists(user_id):
        message = message_texts.MSG_NO_WORDS[user_language]
    else:
        query = """DELETE 
                    FROM words 
                    WHERE user_id == '{key}'"""
        cur.execute(query.format(key=user_id))
        db.commit()
        message = message_texts.MSG_DELETE_ALL_DELETED[user_language]
    return message


# Последняя выбранная группа слов
async def actual_user_group(user_id: str) -> str:
    user_group = ""
    query = """SELECT CASE WHEN actual_category IS NULL THEN 'None' ELSE actual_category END AS actual_category
                FROM word_groups 
                WHERE user_id == '{key}'"""
    user_group = cur.execute(query.format(key=user_id)).fetchone()
    if not user_group:
        user_group = message_texts.MSG_ALL_WORDS
    else:
        user_group = user_group[0]
    return user_group

# Все группы слов пользователя
async def all_user_groups(user_id: str, state) -> dict:
    user_groups = {'message_groups': str(),
                   'groups': [],
                   'min_group_num': int(), 
                   'max_group_num': int()}
    i = int(0)
    query = """SELECT category
                    ,CASE WHEN num IS NULL THEN 0 ELSE num END AS num
                    ,num_total
                FROM (
                    SELECT '{category}' as category
                        ,SUM(CASE WHEN reminder_date < strftime('%Y-%m-%d %H:%M:%S','now') THEN 1 ELSE 0 END) as num
                        ,COUNT(word_id) as num_total
                    FROM words
                    WHERE user_id == '{key}'
                )
                UNION ALL
                SELECT * FROM (
                    SELECT DISTINCT category
                        ,SUM(case when reminder_date < strftime('%Y-%m-%d %H:%M:%S','now') then 1 else 0 end) as num
                        ,COUNT(word_id) as num_total
                    FROM words 
                    WHERE user_id == '{key}'
                    GROUP BY category
                    ORDER BY category
                )"""
    current_state = await state.get_state()
    if current_state == 'FSMDownload:download_csv':
        for group in cur.execute(query.format(category=message_texts.MSG_ALL_WORDS, key=user_id)).fetchall():
            user_groups['message_groups'] = user_groups['message_groups'] + str(i) + " — " + str(group[0]) + " | "\
                                                        + "<b>" + str(group[2]) + "</b>" + "\n"
            user_groups['groups'].append(str(group[0]))
            user_groups['min_group_num'] = int(0)
            user_groups['max_group_num'] = i
            i += 1
    else:
        for group in cur.execute(query.format(category=message_texts.MSG_ALL_WORDS, key=user_id)).fetchall():
            user_groups['message_groups'] = user_groups['message_groups'] + str(i) + " — " + str(group[0]) + " | "\
                                                        + str(group[1]) + "/<b>" + str(group[2]) + "</b>" + "\n"
            user_groups['groups'].append(str(group[0]))
            user_groups['min_group_num'] = int(0)
            user_groups['max_group_num'] = i
            i += 1
    return user_groups

# Изменяем группу
async def change_cards_group(user_id: str, state) -> str:
    async with state.proxy() as data:
        group_num = data['change_cards_group']['message']
        group = data['change_cards_group']['groups'][group_num]
        if group == "None": group = None
        query = """SELECT 1 
                    FROM word_groups 
                    WHERE user_id == '{key}'"""
        user_group = cur.execute(query.format(key=user_id)).fetchone()
        if not user_group:
            created_at = datetime.utcnow()
            update_date = created_at
            query = """INSERT INTO word_groups(user_id, actual_category, created_at, update_date) VALUES(?, ?, ?, ?)"""
            cur.execute(query, (user_id, group, created_at, update_date))
        else:
            update_date = datetime.utcnow()
            query = """UPDATE word_groups SET actual_category = ?, update_date = ? WHERE user_id == ?"""
            cur.execute(query, (group, update_date, user_id))
        db.commit()
    return group


# Вывод слов для повторения
def cards(user_id: str, group: str) -> list:
    if group == message_texts.MSG_ALL_WORDS: # Запрос для всех слов
        query = """SELECT word_id
                        , word
                        , translation
                    FROM words 
                    WHERE user_id == '{key}'
                    AND reminder_date < strftime('%Y-%m-%d %H:%M:%S','now')
                    ORDER BY reminder_date
                    LIMIT 10"""
    elif str(group) == "None": # Запрос для группы NULL
        query = """SELECT word_id
                        , word
                        , translation
                    FROM words 
                    WHERE user_id == '{key}'
                    AND category IS NULL
                    AND reminder_date < strftime('%Y-%m-%d %H:%M:%S','now')
                    ORDER BY reminder_date
                    LIMIT 10"""
    else: # Запрос для остальных групп
        query = """SELECT word_id
                        , word
                        , translation
                    FROM words 
                    WHERE user_id == '{key}'
                    AND category == '{group}'
                    AND reminder_date < strftime('%Y-%m-%d %H:%M:%S','now')
                    ORDER BY reminder_date
                    LIMIT 10"""
    users_cards = cur.execute(query.format(key=user_id, group=group)).fetchall()
    cards_w_rev_flg = []
    for card in users_cards: # добавляем флаг rev показывается слово или перевод: False = слово
        card_w_rev_flg = (card[0], card[1], card[2], False)
        cards_w_rev_flg.append(card_w_rev_flg)
    users_cards = cards_w_rev_flg
    shuffle(users_cards) # перемешиваем элементы списка
    rev = []
    rev_card = ()
    for card in users_cards:
        rev_card = (card[0], card[2], card[1], True)
        rev.append(rev_card)
    shuffle(rev)
    users_cards = users_cards + rev
    return users_cards


# Загружаем слова в БД из csv
async def upload_csv(user_id: str, fp: str):
    reminder_date = datetime.utcnow()
    user_added_word = user_id
    is_uploaded_from_file = 1
    df = pd.DataFrame()
    df = pd.read_csv(fp, header=None, sep=';')
    df = df.astype(object).where(pd.notnull(df),None)
    if str(df.iloc[0,1]) == 'translation':
        df = df.iloc[1:]
    query = """INSERT INTO words(user_id
                                ,user_added_word
                                ,word
                                ,translation
                                ,category
                                ,is_uploaded_from_file
                                ,reminder_date) VALUES(?, ?, ?, ?, ?, ?, ?)"""
    for i in range(df.shape[0]):
        word = df.iloc[i, 0]
        translation = df.iloc[i, 1]
        category = df.iloc[i, 2]
        if word: word.strip()
        if translation: translation.strip()
        if category: category.strip()
        cur.execute(query, (user_id, user_added_word, word, translation, category, is_uploaded_from_file, reminder_date))
    db.commit()



# Скачать сохраненные слова
async def download_csv(user_id: str, group: str) -> str:
    if group == message_texts.MSG_ALL_WORDS: # Запрос для всех слов
        query = """SELECT word, translation, category, created_at, reminder_date
                FROM words
                WHERE user_id == '{key}'
                ORDER BY created_at dESC"""
    elif str(group) == "None": # Запрос для группы NULL
        query = """SELECT word, translation, category, created_at, reminder_date
                FROM words
                WHERE user_id == '{key}'
                AND category IS NULL
                ORDER BY created_at dESC"""
    else: # Запрос для остальных групп
        query = """SELECT word, translation, category, created_at, reminder_date
                FROM words
                WHERE user_id == '{key}'
                AND category == '{group}'
                ORDER BY created_at dESC"""

    script_dir = os.path.dirname(__file__)
    rel_path = f'tmp/id_{user_id}_{time.strftime("%Y%m%d_%H%M%S")}_UTF8.csv'
    abs_file_path = os.path.join(script_dir, rel_path)

    df = pd.read_sql(query.format(key=user_id, group=group), db)
    df.insert(0, 'row_number', range(1, 1 + len(df)))
    df.to_csv(abs_file_path, sep=';', index=False, encoding='utf-8')

    return abs_file_path


# Обновление даты для повторения
async def update_remind_date(user_id: str, word_id: str, remind_in: str, rev: bool):
    if remind_in == "remind in 1 day":
        remind_in_days = 0.9
        next_reminder_interval = 1
        num_click_button = 'num_click_first_button'
    elif remind_in == "remind in 7 day":
        remind_in_days = 7
        next_reminder_interval = 7
        num_click_button = 'num_click_second_button'
    elif remind_in == "remind in 30 day":
        remind_in_days = 30
        next_reminder_interval = 30
        num_click_button = 'num_click_third_button'
    elif remind_in == "remind in 90 day":
        remind_in_days = 90
        next_reminder_interval = 90
        num_click_button = 'num_click_fourth_button'
    else:
        remind_in_days = 0
        next_reminder_interval = 0
        rev = True # чтобы не обновлять столбце 'num_click_button'
    update_date = (datetime.utcnow() + timedelta(days = remind_in_days))
    if not rev: # если показано само слова, а не перевод
        query = """UPDATE words
                    SET reminder_date = '{update_date}', next_reminder_interval = '{next_reminder_interval}', {num_click_button} = IFNULL({num_click_button}, 0) + 1
                    WHERE user_id == '{key}'
                    AND word_id == '{word_id}'"""
        cur.execute(query.format(update_date=update_date
                        ,next_reminder_interval=next_reminder_interval
                        ,num_click_button=num_click_button
                        ,key=user_id
                        ,word_id=word_id))
    else:
        query = """UPDATE words
                    SET reminder_date = '{update_date}', next_reminder_interval = '{next_reminder_interval}'
                    WHERE user_id == '{key}'
                    AND word_id == '{word_id}'"""
        cur.execute(query.format(update_date=update_date
                        ,next_reminder_interval=next_reminder_interval
                        ,key=user_id
                        ,word_id=word_id))
    db.commit()


# Вывести дублирующиеся слова
async def select_duplicate(user_id: str, user_language: str) -> str:
    message = ""
    duplicates = ""
    query = """WITH duplicates as (
                SELECT word,
	                CASE WHEN category IS NULL THEN 'None' ELSE category END AS category
                FROM words
                WHERE user_id == '{key}'
                )
                SELECT word,
	                COUNT(word) as num,
	                TRIM(REPLACE(GROUP_CONCAT(category),',',', ')) as categories
                FROM duplicates
                GROUP BY word
                HAVING count(word) > 1
                ORDER BY word"""
    for word in cur.execute(query.format(key=user_id)).fetchall():
        duplicates = duplicates + str(word[0]) + " — " + str(word[1]) + " | " + str(word[2]) + "\n"
    if duplicates == "":
        message = message_texts.MSG_DUPLICATE_NO_WORDS[user_language]
    else:
        message = message_texts.MSG_DUPLICATE[user_language].format(duplicates=duplicates)
    return message


# Изменение группы у слова
async def update_group(user_id: str) -> str:
    pass


# Интервал уведомлений для пользователя
async def actual_user_notification_interval(user_id: str) -> str:
    user_notifications = ""
    query = """SELECT CASE WHEN notifications_interval IS NULL THEN 'Никогда' ELSE notifications_interval END AS notifications_interval
                FROM notifications 
                WHERE user_id == '{key}'"""
    user_notifications = cur.execute(query.format(key=user_id)).fetchone()
    if not user_notifications:
        user_notifications = message_texts.KB_NOTIFICATIONS_NEVER
    else:
        user_notifications = str(user_notifications[0])
    return user_notifications


# Изменение частоты уведомлений
async def update_notification_interval(user_id: str, new_notification_interval: str):
    update_date = datetime.utcnow()
    if new_notification_interval.isnumeric():
        new_notification_interval = int(new_notification_interval)
        next_notifications_date = update_date + timedelta(days=new_notification_interval)
    else: 
        new_notification_interval = None
        next_notifications_date = None
    query = """UPDATE notifications SET notifications_interval = ?, next_notifications_date = ?, update_date = ?
            WHERE user_id == ?"""
    cur.execute(query, (new_notification_interval, next_notifications_date, update_date, user_id))
    db.commit()


# Список пользователей, для отправки уведомлений
async def user_list_to_send_notifications() -> list:
    today = str(datetime.utcnow() + timedelta(seconds=1))
    user_list = []
    user_dict = {'user_id': str(),
                'notifications_interval': int(),
                'user_language': str()}
    query = """SELECT DISTINCT n.user_id
                             , n.notifications_interval
                             , coalesce(l.language,'EN') as language
            FROM notifications n
            INNER JOIN access a ON a.user_id = n.user_id AND a.access = 1
            LEFT JOIN user_language l on n.user_id = l.user_id
            WHERE notifications_interval IS NOT NULL
            AND datetime(n.next_notifications_date) <= datetime('{today}')
            ORDER BY n.user_id"""
    for user in cur.execute(query.format(today=today)).fetchall():
        user_dict['user_id'] = str(user[0])
        user_dict['notifications_interval'] = str(user[1])
        user_dict['user_language'] = str(user[2])
        user_list.append(user_dict.copy())
    return user_list


# Список пользователей, для отправки сообщения от автора
async def user_list_to_send_message() -> list:
    user_list = []
    query = """SELECT DISTINCT user_id
            FROM access
            WHERE access = 1"""
    for user in cur.execute(query).fetchall():
        user_list.append(user[0])
    return user_list


# Запись события в БД
async def event_recording(user_id: str, word_id: str = None, event: str = None):
    created_at = datetime.utcnow()
    try:
        query = """INSERT INTO events(user_id
                                    ,word_id
                                    ,event
                                    ,created_at) VALUES(?, ?, ?, ?)"""
        cur.execute(query, (user_id, word_id, event, created_at))
        db.commit()
    except:
        pass


# Любой запрос к БД через ТГ сообщение
async def any_query(query:str) -> str:
    output = ""
    sql_command = query.split(" ", 1)[0].upper()
    if sql_command in ('UPDATE', 'INSERT', 'DELETE'):
        try:
            cur.execute(query)
            db.commit()
            messege = message_texts.MSG_SQL_QUERY_DONE
        except:
            messege = message_texts.MSG_SQL_QUERY_ERROR
    elif sql_command in ('SELECT', 'WITH'):
        if 'LIMIT' not in query.upper():
            query = query + '\n LIMIT 20'
        try:
            data = cur.execute(query)
            for count, column in enumerate(data.description):
                if count == 0:
                    output = output + str(column[0])
                else:
                    output = output + ' | ' + str(column[0])
            output = output + "\n"
            for row in data.fetchall():
                for count, value in enumerate(row):
                    if count == 0:
                        output = output + str(row[count])
                    else:
                        output = output + ' | ' + str(row[count])
                output = output + "\n"
            messege = message_texts.MSG_SQL_QUERY_RETURN.format(output=output)
        except:
            messege = message_texts.MSG_SQL_QUERY_ERROR
    else:
        messege = message_texts.MSG_SQL_QUERY_COMMAND_ERROR
    return messege