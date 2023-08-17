"""----------------------------------------------------------------------"""
"""--------------------------INFO AND HELP-------------------------------"""
"""----------------------------------------------------------------------"""

MSG_GREETINGS = """🧠 Memorizing words bot умеет сохранять слова/фразы и их перевод.\n
🚀 В режиме карточек можно:
• просматривать ранее добавленные слова;
• вспоминать их перевод;
• выбирать, через сколько дней показать это слово в карточках в следующий раз.\n
✍️ Чтобы добавить новое слово напиши:
<b>[слово] = [перевод]</b>
ПРИМЕР: <b>memory = память</b>\n\n
✍️ Чтобы добавить новое слово и отнести его к группе напиши:
<b>[слово] = [перевод] = [группа]</b>
*Названия групп могут быть любыми.
ПРИМЕР: <b>melon = дыня = фркуты</b>
"""

MSG_COMANDS = """🤖 Команды:
/cards — включить режим карточек
/words — показать последние 15 сохраненных слов
/words_num — показать количество сохраненных слов
/duplicates — показать дублирующиеся слова
/download_csv — скачать слова в csv
/delete — включить режим удаления слов
/delete_all — включить режим удаления всех слов
/cancel — выйти из любого режима
/notifications — настроить частоту ведомлений
/donate — поддержать проект"""

MSG_START = MSG_GREETINGS + "\n\n" + MSG_COMANDS
MSG_HELP = MSG_GREETINGS + "\n\n" + MSG_COMANDS

MSG_AUTH_HELP = """👾 Команды доступные только автору:
/auth — просмотр списка команд автора
/access <user_id> — выдача доступа
/block <user_id> — блокировка доступа
/access_request — запросить доступ (доступно всем)
/query — режим выполнения SQL скриптов
"""

MSG_NO_WORDS = """💬 Еще нет сохраненных слов"""


"""----------------------------------------------------------------------"""
"""---------------------------WORD INSERT--------------------------------"""
"""----------------------------------------------------------------------"""

MSG_INSERT_WORD = """✍️ Записал"""


"""----------------------------------------------------------------------"""
"""-------------------------------CARDS----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_CARDS_NO_WORDS = """⚡️ На сегодня нет слов для повторения.\n
Выбрана группа слов: <b>{group}</b>
/cards_group — чтобы изменить группу"""

MSG_CARDS_INFO = """🚀 Режим карточек включен.
Тебе будут показываться 10 слов + 10 их переводов.
Для каждого слова можно показать перевод, и затем выбрать, через сколько дней показать это слово в карточках в следующий раз:
1 — через 1 день
7 — через 7 дней
30 — через 30 дней
90 — через 90 дней\n
📌 Текущая группа слов: <b>{group}</b>
/cards_group — чтобы изменить группу"""

MSG_CARDS_FINISH = """⭐️ Слова закончились. Так держать!\nВышел из режима карточек"""

MSG_CARDS_CANCEL = """🔙 Вышел из режима карточек"""

MSG_CARDS_USER_GROUPS = """⚙️ Напиши <b>номер</b> группы, чтобы переключиться на неё. 
Формат:
<b>[номер] — [название] | [можно повторить]/[всего слов]</b>\n
{user_groups}\nДля отмены — /cancel"""

MSG_CARDS_GET_GROUPS = """📌 Выбрана группа: <b>{group}</b>\n/cards — перейти в режим карточек"""
MSG_CARDS_GET_GROUPS_WRONG1 = """Написан не существующий номер группы.\nДля отмены — /cancel"""
MSG_CARDS_GET_GROUPS_WRONG2 = """Написан не номер группы.\nДля отмены — /cancel"""

MSG_ALL_WORDS = """All words"""


"""----------------------------------------------------------------------"""
"""------------------------------WORDS-----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_WORDS_LAST = """🗒 15 последних сохраненных слов:\n\n{clients_words}"""


"""----------------------------------------------------------------------"""
"""----------------------------WORDS_NUM---------------------------------"""
"""----------------------------------------------------------------------"""

MSG_WORDS_NUM = """🗒 Сохранено слов всего: <b>{words_num}</b>"""
MSG_WORDS_NUM_GROUP = """По группам:\n{words_in_group}"""


"""----------------------------------------------------------------------"""
"""---------------------------DOWNLOAD_CSV-------------------------------"""
"""----------------------------------------------------------------------"""

MSG_DOWNLOAD_CSV = """📎 Какие слова скачать?"""

MSG_DOWNLOAD_CSV_CONCEL = """🔙 Вышел из режима скачивания"""

MSG_DOWNLOAD_CSV_GROUPS = """⚙️ Напиши <b>номер</b> группы, чтобы скачать её.
Формат:
<b>[номер] — [название] | [кол-во слов]</b>\n
{user_groups}\nДля отмены — /cancel"""

MSG_DOWNLOAD_CSV_ALL = """✔️ Скачены все слова"""
MSG_DOWNLOAD_CSV_GROUP = """✔️ Скачена группа: <b>{group}</b>"""


"""----------------------------------------------------------------------"""
"""----------------------------DUPLICATE---------------------------------"""
"""----------------------------------------------------------------------"""

MSG_DUPLICATE = """🔗 Повторяющиеся слова в формате:
<b>[слово] — [количество повторений] | [группы]</b>
*Если группа <b>None</b>, значит у слова не указана группа.\n\n{duplicates}"""

MSG_DUPLICATE_NO_WORDS = """🔗 Нет повторяющихся слов"""


"""----------------------------------------------------------------------"""
"""------------------------------DELETE----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_DELETE = """⚠️ Напиши слово, которое нужно удалить\n\nДля отмены — /cancel"""
MSG_DELETE_ERROR = """🔙 Такого слова нет. Вышел из режима удаления.\nУдалим другое слово? — /delete"""
MSG_DELETE_DELETED = """🗑 Удалил. Вышел из режима удаления.\nУдалим другое слово? — /delete"""

MSG_DELETE_ALL = """⚠️ Чтобы запустить процесс удаления всех слов напиши еще раз — /delete_all\n\nДля отмены — /cancel"""
MSG_DELETE_ALL_X2 = """‼️ После удаления слова нельзя будет восстановить. 
Чтобы удалить все слова — /yes\n\nДля отмены — /cancel"""
MSG_DELETE_ALL_DELETED = """🗑 Удалил все слова"""


"""----------------------------------------------------------------------"""
"""----------------------CHANGE GROUP FOR WORDS--------------------------"""
"""----------------------------------------------------------------------"""

CHANGE_GROUP_FOR_WORDS = """🛠 У каких слов нужно изменить группу?"""

CHANGE_GROUP_FOR_WORDS_CONCEL = """🔙 Вышел из режима изменения групп"""


"""----------------------------------------------------------------------"""
"""------------------------------CANCEL----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_CANCEL = """💬 Что отменить? Ничего и не происходит :)"""

MSG_CANCEL_DELETE = """🔙 Вышел из режима удаления"""

MSG_CANCEL_REMINDER = """🔙 Вышел из режима карточек"""

MSG_CANCEL_CHANGE_GROUP = """🔙 Вышел из режима выбора групп"""

MSG_CANCEL_CHANGE_DOWNLOAD = """🔙 Вышел из режима скачивания"""

MSG_CANCEL_NOTIFICATIONS = """🔙 Вышел из режима настройки частоты уведомлений"""

MSG_CANCEL_GENETAL = """🔙 Отменил"""


"""----------------------------------------------------------------------"""
"""---------------------------NOTIFICATIONS------------------------------"""
"""----------------------------------------------------------------------"""

MSG_NOTIFICATIONS_INFO = """🔔 Текущая частота уведомлений:\n<b>{notification_freq}</b>\n
⚙️ Изменить частоту уведомлений на..."""

MSG_NOTIFICATIONS_SET = """🔔 Выбрана частота уведомлений:\n<b>{notification_freq}</b>"""
MSG_NOTIFICATIONS_SET_NEVER = """🔕 Выбрана частота уведомлений: <b>{notification_freq}</b>"""

MSG_NOTIFICATIONS = """🧠 Повторим слова?\n
/cards — перейти в режим карточек
/notifications — настроить частоту уведомлений"""


"""----------------------------------------------------------------------"""
"""------------------------------DONATE----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_DONATE = """/donate — support the project!"""

MSG_DONATE_INFO = """💸 Please support the Memorizing words bot project:
Patreon — https://www.patreon.com/sergeylix
/Georgian_iban — GE44BG0000000538934249 (Sergei Likhachev)
/BUSD_BEP20: 0xaFC0c26B0eD046c704C346c135430f132938cD9a
/USDT_TRC20: TDC8ba6kKfZYBQbhcJ8PypsnfCoFNL74rQ
/USDC_ERC20: 0xaFC0c26B0eD046c704C346c135430f132938cD9a
Thank you for your support.
"""

MSG_DONATE_Georgian_iban = """GE44BG0000000538934249"""

MSG_DONATE_BUSD_BEP20 = """0xaFC0c26B0eD046c704C346c135430f132938cD9a"""

MSG_DONATE_USDT_TRC20 = """TDC8ba6kKfZYBQbhcJ8PypsnfCoFNL74rQ"""

MSG_DONATE_USDC_ERC20 = """0xaFC0c26B0eD046c704C346c135430f132938cD9a"""


"""----------------------------------------------------------------------"""
"""-----------------------COMMAND NOT DEFINED----------------------------"""
"""----------------------------------------------------------------------"""

MSG_COMMAND_NOT_DEFINED = """💬 Не понимаю. Может не хватает знака '='?"""


"""----------------------------------------------------------------------"""
"""-----------------------------SQL QUERY--------------------------------"""
"""----------------------------------------------------------------------"""

MSG_SQL_QUERY = """Напиши SQL запрос без переноса строк. После запроса автоматически добавится limit 20.\n\nДля отмены — /cancel"""

MSG_SQL_QUERY_ERROR = """Ошибка в запросе. Вышел из режима написания запросов"""

MSG_SQL_QUERY_RETURN = """✔️ Результат запроса:\n\n{output}"""


"""----------------------------------------------------------------------"""
"""------------------------------KEYBOARDS-------------------------------"""
"""----------------------------------------------------------------------"""

KB_DOWNLOAD_ALL = """Скачать все слова"""
KB_DOWNLOAD_GROUP = """Скачать группу слов"""
KB_DOWNLOAD_CANCEL = """Отмена"""

KB_CHANGE_GR_ONE_WORD = """Изменить у одного слова"""
KB_CHANGE_GR_IN_GR = """Изменить у группы"""
KB_CHANGE_GR_ALL = """Изменить у всех слов"""
KB_CHANGE_GR_CANCEL = """Отмена"""

KB_NOTIFICATIONS_DAY = """Раз в день"""
KB_NOTIFICATIONS_WEEK = """Раз в неделю"""
KB_NOTIFICATIONS_MONTH = """Раз в месяц"""
KB_NOTIFICATIONS_NEVER = """Никогда"""
KB_NOTIFICATIONS_CONCEL = """Отмена"""