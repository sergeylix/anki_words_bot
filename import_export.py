import sqlite3 as sq
import pandas as pd

async def db_start():
    global db, cur
    db = sq.connect('anki_words')
    cur = db.cursor()

async def export_words():
    query = """SELECT user_id, word_eng, word_rus, created_at, reminder_date FROM words"""
    df = pd.read_sql(query, db)
    df.to_csv('export/words.csv', sep=';', encoding='utf-8', index=False)

async def import_words():
    df= pd.read_csv('export/words.csv', sep=';')
    df.to_sql('words', db, if_exists='append', index=False)

# db_start()
# export_words()
# import_words()