from datetime import datetime, timedelta
import time
import os
import pandas as pd
import sqlite3 as sq

import message_texts
from fasttext.FastText import _FastText

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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)"""
    cur.execute(query)
    db.commit()

    # Создание таблицы со словами
    query = """CREATE TABLE IF NOT EXISTS words(
                    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    word TEXT,
                    translation TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    reminder_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES profile(user_id))"""
    cur.execute(query)
    db.commit()

    # Создание таблицы группами
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


# Получаем список пользователей с доступами
async def get_users_w_access() -> list:
        users_w_access = []
        query = """SELECT user_id FROM access WHERE access = '{flg}'"""
        for user in cur.execute(query.format(flg=1)).fetchall():
            users_w_access.append(int(user[0]))
        return users_w_access


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


# Выдача прав пользователю
async def add_access(users:  list, flg: int):
    for user_id in users:
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

    if not notification_exists(user_id):
        notifications_interval = 7 # week
        next_notifications_date = (datetime.utcnow() + timedelta(days=notifications_interval))
        created_at = datetime.utcnow()
        update_date = created_at
        cur.execute("INSERT INTO notifications(user_id, notifications_interval, next_notifications_date, created_at, update_date) VALUES(?, ?, ?, ?, ?)", 
                    (user_id, notifications_interval, next_notifications_date, created_at, update_date))
        db.commit()


# Добавление слова
async def insert_words(user_id: str, user_message: str):
    # words = [word.strip() for word in user_message.split('=', 1)]
    words = [word.strip() for word in user_message.split('=', 2)]
    if len(words) == 2:
        words.append('')
    if define_language(words[0]) == '__label__en' and define_language(words[1]) == '__label__en':
        pass
    elif define_language(words[0]) != '__label__en' and define_language(words[1]) == '__label__en':
        words = [words[1], words[0], words[2]]
    reminder_date = (datetime.utcnow() + timedelta(days=0))
    if not words[2]:
        cur.execute("INSERT INTO words(user_id, word, translation, reminder_date) VALUES(?, ?, ?, ?)", (user_id, words[0], words[1], reminder_date))
    else:
        cur.execute("INSERT INTO words(user_id, word, translation, category, reminder_date) VALUES(?, ?, ?, ?, ?)", (user_id, words[0], words[1], words[2], reminder_date))
    db.commit()


# Вывод последних добавленных слов
async def select_words(user_id: str) -> str:
    message = ""
    clients_words = ""
    if not profile_exists(user_id):
        message = message_texts.MSG_NO_WORDS
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
             message = message_texts.MSG_NO_WORDS
        else:
            message = message_texts.MSG_WORDS_LAST.format(clients_words=clients_words)
    return message


# Кол-во сохраненных слов всего
async def words_num(user_id: str) -> str:
    message = ""
    words_in_group = ""
    if not profile_exists(user_id):
        message = message_texts.MSG_NO_WORDS
    else:
        # всего слов
        query = """SELECT count(word_id)
                    FROM words 
                    WHERE user_id == '{key}'"""
        words_num = cur.execute(query.format(key=user_id)).fetchone()[0]
        message = message_texts.MSG_WORDS_NUM.format(words_num=words_num)
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
            message = message + "\n\n" + message_texts.MSG_WORDS_NUM_GROUP.format(words_in_group=words_in_group)
    return message


# Удаление слова
async def delete_word(user_id: str, state) -> str:
    async with state.proxy() as data:
        query = """SELECT 1 
                    FROM words 
                    WHERE user_id == '{key}'
                    AND (translation == '{word}' OR word == '{word}')"""
        word_for_del = cur.execute(query.format(key=user_id, word=data['word_for_delete'])).fetchone()
        if not word_for_del:
            message = message_texts.MSG_DELETE_ERROR
        else:
            query = """DELETE 
                        FROM words 
                        WHERE user_id == '{key}'
                        AND (translation == '{word}' OR word == '{word}')"""
            cur.execute(query.format(key=user_id, word=data['word_for_delete']))
            db.commit()
            message = message_texts.MSG_DELETE_DELETED
    return message


# Удаление всех слов пользователя
async def delete_all_words(user_id: str) -> str:
    if not profile_exists(user_id):
        message = message_texts.MSG_NO_WORDS
    else:
        query = """DELETE 
                    FROM words 
                    WHERE user_id == '{key}'"""
        cur.execute(query.format(key=user_id))
        db.commit()
        message = message_texts.MSG_DELETE_ALL_DELETED
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
    query = """SELECT * FROM (
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
    rev = []
    rev_card = ()
    for card in users_cards:
        rev_card = (card[0], card[2], card[1])
        rev.append(rev_card)
    users_cards = users_cards + rev
    return users_cards


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
async def update_remind_date(user_id: str, word_id: str, remind_in: str):
    query = """UPDATE words
                SET reminder_date = '{update_date}'
                WHERE user_id == '{key}'
                AND word_id == '{word_id}'"""
    if remind_in == "remind in 1 day":
        remind_in_days = 0.9
    elif remind_in == "remind in 7 day":
        remind_in_days = 7
    elif remind_in == "remind in 30 day":
        remind_in_days = 30
    elif remind_in == "remind in 90 day":
        remind_in_days = 90
    else:
        remind_in_days = 0
    update_date = (datetime.utcnow() + timedelta(days = remind_in_days))
    cur.execute(query.format(update_date=update_date, key=user_id, word_id=word_id))
    db.commit()


# Вывести дублирующиеся слова
async def select_duplicate(user_id: str) -> str:
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
        message = message_texts.MSG_DUPLICATE_NO_WORDS
    else:
        message = message_texts.MSG_DUPLICATE.format(duplicates=duplicates)
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
                'notifications_interval': int()}
    query = """SELECT DISTINCT n.user_id
                             , n.notifications_interval
            FROM notifications n
            INNER JOIN access a ON a.user_id = n.user_id AND a.access = 1
            WHERE notifications_interval IS NOT NULL
            AND datetime(next_notifications_date) <= datetime('{today}')
            ORDER BY user_id"""
    for user in cur.execute(query.format(today=today)).fetchall():
        user_dict['user_id'] = str(user[0])
        user_dict['notifications_interval'] = str(user[1])
        user_list.append(user_dict.copy())
    return user_list


# Список пользователей, для отправки сообщения от автора
async def user_list_to_send_message() -> list:
    user_list = []
    query = """SELECT DISTINCT p.user_id
            FROM profile p
            INNER JOIN access a ON a.user_id = p.user_id AND a.access = 1"""
    for user in cur.execute(query).fetchall():
        user_list.append(user[0])
    return user_list


# Любой запрос к БД через ТГ сообщение
async def any_query(query:str) -> str:
    output = ""
    sql_command = query.split(" ", 1)[0]
    if sql_command in ('UPDATE', 'INSERT', 'DELETE'):
        try:
            cur.execute(query)
            db.commit()
            messege = message_texts.MSG_SQL_QUERY_DONE
        except:
            messege = message_texts.MSG_SQL_QUERY_ERROR
    elif sql_command in ('SELECT', 'WITH'):
        query = query + '\n limit 20'
        try:
            for row in cur.execute(query).fetchall():
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