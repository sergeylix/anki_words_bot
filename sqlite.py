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
        message = "Еще нет сохраненных слов"
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
             message = "Еще нет сохраненных слов"
        else:
            message = f"15 последних добавленных слов:\n\n{clients_words}"
    return message


# Кол-во сохраненных слов всего
async def words_num(user_id: str) -> str:
    message = ""
    if not profile_exists(user_id):
        message = "Еще нет сохраненных слов"
    else:
        query = """SELECT count(word_id)
                    FROM words 
                    WHERE user_id == '{key}'"""
        words_num = cur.execute(query.format(key=user_id)).fetchone()[0]
        message = f"Сохранено слов: {words_num}"
    return message

# Кол-во сохраненных слов в группах
async def words_in_group_num(user_id: str) -> str:
    message = ""
    words_in_group = ""
    if not profile_exists(user_id):
        message = "Еще нет сохраненных слов"
    else:
        query = """SELECT category
	                    ,count(distinct a.word_id) as words_num
                    FROM words a
                    WHERE user_id = '{key}'
                    GROUP BY category
                    ORDER BY words_num DESC"""
        for word in cur.execute(query.format(key=user_id)).fetchall():
            words_in_group = words_in_group + str(word[0]) + " — " + str(word[1]) + "\n"
        message = f"Сохранено слов в группах:\n{words_in_group}"
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
            message = "Такого слова нет. Вышел из режима удаления.\nУдалим другое слово? - /delete"
        else:
            query = """DELETE 
                        FROM words 
                        WHERE user_id == '{key}'
                        AND (translation == '{word}' OR word == '{word}')"""
            cur.execute(query.format(key=user_id, word=data['word_for_delete']))
            db.commit()
            message = "Удалил! И вышел из режима удаления.\nУдалим другое слово? - /delete"
    return message


# Удаление всех слов пользователя
async def delete_all_words(user_id: str) -> str:
    if not profile_exists(user_id):
        message = "Еще нет сохраненных слов"
    else:
        query = """DELETE 
                    FROM words 
                    WHERE user_id == '{key}'"""
        cur.execute(query.format(key=user_id))
        db.commit()
        message = "Все слова удалил!"
    return message


# Вывод слов для повторения
def cards(user_id: str) -> list:
    query = """SELECT word_id
                    , word
                    , translation
                FROM words 
                WHERE user_id == '{key}'
                AND reminder_date < strftime('%Y-%m-%d %H:%M:%S','now')
                ORDER BY reminder_date
                LIMIT 10"""
    users_cards = cur.execute(query.format(key=user_id)).fetchall()
    rev = []
    rev_card = ()
    for card in users_cards:
        rev_card = (card[0], card[2], card[1])
        rev.append(rev_card)
    users_cards = users_cards + rev
    return users_cards


# Скачать все сохраненные слова
async def download_csv(user_id: str) -> str:
    query = """SELECT word, translation, category, created_at, reminder_date
                FROM words
                WHERE user_id == '{key}'
                ORDER BY created_at dESC"""

    script_dir = os.path.dirname(__file__)
    rel_path = f'tmp/id_{user_id}_{time.strftime("%Y%m%d_%H%M%S")}_UTF8.csv'
    abs_file_path = os.path.join(script_dir, rel_path)

    df = pd.read_sql(query.format(key=user_id), db)
    df.insert(0, 'row_number', range(1, 1 + len(df)))
    df.to_csv(abs_file_path, sep=';', index=False, encoding='utf-8')

    return abs_file_path


# Обновление даты для повторения
async def update_remind_date(user_id: str, word_id: str, remind_in: str):
    query = """UPDATE words
                SET reminder_date = '{update_date}'
                WHERE user_id == '{key}'
                AND word_id = '{word_id}'"""
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
                HAVING count(word) > 1"""
    for word in cur.execute(query.format(key=user_id)).fetchall():
        duplicates = duplicates + str(word[0]) + " — " + str(word[1]) + " (" + str(word[2]) + ")" + "\n"
    if duplicates == "":
        message = message_texts.MSG_DUPLICATE_NO_WORDS
    else:
        message = f"Повторяющиеся слова в формате:\n<слово> — <количество повторений> (<категории>)\nЕсли группа None, значит у слова не указана группа\n\n{duplicates}"
    return message


# Любой запрос к БД через ТГ сообщение
async def any_query(query:str) -> str:
    output = ""
    query = query + '\n limit 20'
    try:
        for row in cur.execute(query).fetchall():
            for count, value in enumerate(row):
                if count == 0:
                    output = output + str(row[count])
                else:
                    output = output + ' - ' + str(row[count])
            output = output + "\n"
        messege = f"Результат запроса:\n\n{output}"
    except:
        messege = "Ошибка в запросе"
    return messege