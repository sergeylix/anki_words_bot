"""----------------------------------------------------------------------"""
"""-----------------------------LANGUAGE---------------------------------"""
"""----------------------------------------------------------------------"""

MSG_LANGUAGE = {
    'EN':"Select interface language:"
    ,'RU':"Select interface language:"
}
MSG_LANGUAGE_SET = {
    'EN':"🇬🇧 <b>English</b> language selected\n/language — to change the language"
    ,'RU':"🇷🇺 Выбран <b>русский</b> язык\n/language — to change the language"
}


"""----------------------------------------------------------------------"""
"""-------------------------------ACCESS---------------------------------"""
"""----------------------------------------------------------------------"""

MSG_ACCESS_DENIED = {
    'EN':"Access Denied -_-"
    ,'RU':"Нет доступа -_-"
}

MSG_ACCESS_DENIED_REQUEST = {
    'EN':"Access Denied.\nTo get access run — /access_request"
    ,'RU':"Нет доступа.\nЧтобы запросить доступ нажми — /access_request"
}

MSG_ACCESS = {
    'EN':"🔑 Access granted! To get started run — /start"
    ,'RU':"🔑 Доступ открыт! Чтобы начать нажми — /start"
}

"""----------------------------------------------------------------------"""
"""--------------------------INFO AND HELP-------------------------------"""
"""----------------------------------------------------------------------"""

MSG_HI = {
    'EN':"Hi, {user_name}!"
    ,'RU':"Привет, {user_name}!"
}

MSG_GREETINGS = {
    'EN':"""🧠 Anki bot makes it easy to memorize words using interval repetition.

🔮 The bot is able to:
• save words/phrases and their translation;
• show the translation of words;
• set how many days to show the word next time;
• send notifications when words are repeated.

✍️ To add a new word write:
<code>[word] = [translation]</code>
EXAMPLE: <b>buenos días = good morning</b>\n
✍️ Or to add a new word and assign it to a group write:
<code>[word] = [translation] = [group]</code>
*Group names can be any.
EXAMPLE: <b>contento = glad = feelings</b>\n
🚀 To repeat the added words use the cards mode: /cards

💬 If you have any questions about the bot, you can contact us here — @Sergeylih 🦄

🤖 All commands: /commands"""

    ,'RU':"""🧠 Anki bot облегчает запоминание слов с помощью интервальных повторений.

🔮 Бот умеет:
• сохранять слова/фразы и их перевод;
• показывать перевод слов;
• устанавливать, через сколько дней показывать слово в следующий раз;
• отправлять уведомления о повторении слов.

✍️ Чтобы добавить новое слово напиши:
<code>[слово] = [перевод]</code>
ПРИМЕР: <b>memory = память</b>\n
✍️ Или чтобы добавить новое слово и отнести его к группе напиши:
<code>[слово] = [перевод] = [группа]</code>
*Названия групп могут быть любыми.
ПРИМЕР: <b>melon = дыня = фрукты</b>\n
🚀 Чтобы повторять добавленные слова используй режим карточек: /cards

💬 По вопросам работы бота связаться можно тут — @Sergeylih 🦄

🤖 Все команды: /commands"""
}

MSG_COMANDS = {
    'EN':"""🤖 All commands:
/cards — start cards mode
/words — show the last 15 saved words
/words_num — show the number of saved words
/duplicates — show duplicate words
/import_export — upload or download words
/delete — delete one word mode
/delete_all — delete all words mode
/cancel — turn off any mode
/language — 🇬🇧 change interface language
/notifications — set up notifications
/onboarding — quick start
/donate — support the project"""

    ,'RU':"""🤖 Все команды:
/cards — включить режим карточек
/words — показать последние 15 сохраненных слов
/words_num — показать количество сохраненных слов
/duplicates — показать дублирующиеся слова
/import_export — загрузить или скачать слова
/delete — включить режим удаления одного слова
/delete_all — включить режим удаления всех слов
/cancel — выйти из любого режима
/language — 🇬🇧 change interface language
/notifications — настроить уведомления
/onboarding — быстрый старт
/donate — поддержать проект"""
}

MSG_START = MSG_GREETINGS
MSG_HELP = MSG_GREETINGS

MSG_AUTH_HELP = """👾 Команды доступные только автору:
/auth — просмотр списка команд автора
/access <code>user_id</code> — выдача доступа
/block <code>user_id</code> — блокировка доступа
/access_request — запросить доступ (доступно всем)
/send_for_all — отправка сообщения всем пользователям
/query — режим выполнения SQL скриптов

Чтобы поменять режим выдачи доступа выполни запрос:
<code>UPDATE auth_access SET is_auth_access = 1</code>
"""

MSG_NO_WORDS = {
    'EN':"💬 There are no saved words yet"
    ,'RU':"💬 Еще нет сохраненных слов"
}

"""----------------------------------------------------------------------"""
"""----------------------------ONBOARDING--------------------------------"""
"""----------------------------------------------------------------------"""

MSG_ONBOARDING_START = {
    'EN':"""⚡️ For a quick start, use the command — /onboarding
It explains the basic features of the bot in 5 steps."""

    ,'RU':"""⚡️ Для быстрого старта воспользуйся командой — /onboarding
Там за 5 шагов объясняются основные возможности бота."""
}

MSG_ONBOARDING = {
    'EN':"""🐣 <b>5 steps for a quick start</b>:

1. /add_basic_words — add 5 basic Spanish words, you can remove them later;
2. /words — look at the added words;
3. /cards — start card mode, and repeat the added words;
4. Add any word of your own, just write for example: <b>gracias = thank you</b>
5. /del_basic_words — remove 5 basic words from your word list if you wish.

😎 Done! For other commands, see the menu or /help"""

    ,'RU':"""🐣 <b>5 шагов для быстрого старта</b>:

1. /add_basic_words — добавь 5 базовых английских слов, позже их можно будет удалить;
2. /words — посмотри на добавленные слова;
3. /cards — запусти режим карточек, и повтори добавленные слова;
4. Добавь любое свое слово, просто напиши, например: <b>garden = сад</b>
5. /del_basic_words — при желании удали 5 базовых слов из своего списка слов.

😎 Готово! Остальные команды смотри в меню или в /help"""
}

MSG_ONBOARDING_ADD_BASIC_WORDS = {
    'EN':"""✍️ Added 5 basic words"""
    ,'RU':"""✍️ Добавил 5 базовых слов"""
}

MSG_ONBOARDING_DEL_BASIC_WORDS = {
    'EN':"""🗑 Removed the base words"""
    ,'RU':"""🗑 Удалил базовые слова"""
}

MSG_ONBOARDING_BASIC_WORDS = {
    'EN':"""hola = hello = onboarding
perdónа = sorry = onboarding
adiós = bye = onboarding
amigo = friend = onboarding
mañana = tomorrow = onboarding"""

    ,'RU':"""forbid = запрещать = onboarding
vacuum = пылесосить = onboarding
against the law = незаконно = onboarding
old-fashioned = старомодно = onboarding
a doctor appointment = запись к врачу = onboarding"""
}

"""----------------------------------------------------------------------"""
"""---------------------------WORD INSERT--------------------------------"""
"""----------------------------------------------------------------------"""

MSG_INSERT_WORD = {
    'EN':"""✍️ Wrote it down"""
    ,'RU':"""✍️ Записал"""
}

"""----------------------------------------------------------------------"""
"""-------------------------------CARDS----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_CARDS_NO_WORDS = {
    'EN':"""⚡️ There are no words to repeat today.\n
The group of words has been selected: <b>{group}</b>
/cards_group — to change the group"""

    ,'RU':"""⚡️ На сегодня нет слов для повторения.\n
Выбрана группа слов: <b>{group}</b>
/cards_group — чтобы изменить группу"""
}

MSG_CARDS_INFO = {
    'EN':"""🚀 Card mode is activated.
You'll be shown 10 words + 10 of their translations.
For each word, you can show the translation and then choose how many days to show that word in card mode next time:
1 — after 1 day
7 — after 7 days
30 — after 30 days
90 — after 90 days\n
📌 Current word group: <b>{group}</b>
/cards_group — to change the group"""
    
    ,'RU':"""🚀 Режим карточек включен.
Тебе будут показываться 10 слов + 10 их переводов.
Для каждого слова можно показать перевод и затем выбрать, через сколько дней показать это слово в карточках в следующий раз:
1 — через 1 день
7 — через 7 дней
30 — через 30 дней
90 — через 90 дней\n
📌 Текущая группа слов: <b>{group}</b>
/cards_group — чтобы изменить группу"""
}

MSG_CARDS_FINISH = {
    'EN':"""⭐️ Words are out. Good job!\nCard mode is off"""
    ,'RU':"""⭐️ Слова закончились. Так держать!\nВышел из режима карточек"""
}

MSG_CARDS_CANCEL = {
    'EN':"""🔙 Card mode is off"""
    ,'RU':"""🔙 Вышел из режима карточек"""
}

MSG_CARDS_USER_GROUPS = {
    'EN':"""⚙️ Write the group <b>number</b> to switch to. 
The groups are given in the format:
<code>[number] — [title] | [can_be_repeated]/[total_words]</code>\n
{user_groups}\nTo cancel — /cancel"""

    ,'RU':"""⚙️ Напиши <b>номер</b> группы, чтобы переключиться на неё. 
Группы приведены в формате:
<code>[номер] — [название] | [можно_повторить]/[всего_слов]</code>\n
{user_groups}\nДля отмены — /cancel"""
}

MSG_CARDS_GET_GROUPS = {
    'EN':"""📌 Selected group: <b>{group}</b>\n/cards — to switch to card mode"""
    ,'RU':"""📌 Выбрана группа: <b>{group}</b>\n/cards — перейти в режим карточек"""
}
MSG_CARDS_GET_GROUPS_WRONG1 = {
    'EN':"""That group number doesn't exist.\nTo cancel — /cancel"""
    ,'RU':"""Написан не существующий номер группы.\nДля отмены — /cancel"""
}
MSG_CARDS_GET_GROUPS_WRONG2 = {
    'EN':"""That's not a group number.\nTo cancel — /cancel"""
    ,'RU':"""Написан не номер группы.\nДля отмены — /cancel"""
}

MSG_ALL_WORDS = """All words"""


"""----------------------------------------------------------------------"""
"""------------------------------WORDS-----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_WORDS_LAST = {
    'EN':"""🗒 15 last saved words:\n\n{clients_words}"""
    ,'RU':"""🗒 15 последних сохраненных слов:\n\n{clients_words}"""
}

"""----------------------------------------------------------------------"""
"""----------------------------WORDS_NUM---------------------------------"""
"""----------------------------------------------------------------------"""

MSG_WORDS_NUM = {
    'EN':"""🗒 Total words saved: <b>{words_num}</b>"""
    ,'RU':"""🗒 Сохранено слов всего: <b>{words_num}</b>"""
}
MSG_WORDS_NUM_GROUP = {
    'EN':"""By group:\n{words_in_group}"""
    ,'RU':"""По группам:\n{words_in_group}"""
}

"""----------------------------------------------------------------------"""
"""---------------------------IMPORT_EXPORT------------------------------"""
"""----------------------------------------------------------------------"""

MSG_IMPORT_EXPORT = {
    'EN':"""/upload_csv — to upload the word list into the bot
/download_csv — to download the words from the bot"""

    ,'RU':"""/upload_csv — чтобы загрузить список слов в бота
/download_csv — чтобы скачать слова из бота"""
}

"""----------------------------------------------------------------------"""
"""----------------------------UPLOAD_CSV--------------------------------"""
"""----------------------------------------------------------------------"""

MSG_UPLOAD_CSV = {
    'EN':"""🗄 To upload a word list, attach a CSV file:
• under 20 MB
• with a column <a href='https://www.ablebits.com/office-addins-blog/change-excel-csv-delimiter/'>separator</a> ";"
• with 3 columns in the file:
<code>word | translation | group</code>
*The <code>group</code> column may be empty
\nTo cancel — /cancel"""

    ,'RU':"""🗄 Чтобы загрузить список слов, прикрепи CSV файл: 
• размером до 20 MB
• с <a href='https://www.ablebits.com/office-addins-blog/change-excel-csv-delimiter/'>разделителем</a> колонок ";"
• с 3-мя колонками:
<code>word | translation | group</code>
*Колонка <code>group</code> может быть пустой
\nДля отмены — /cancel"""
}

MSG_UPLOAD_CSV_TEMPLATE = {
    'EN':"""Here is the csv file template"""
    ,'RU':"""Вот шаблон csv файла"""
}

MSG_UPLOAD_CSV_PROCESSING = {
    'EN':"""⌛️ Processing the file..."""
    ,'RU':"""⌛️ Обрабатываю файл..."""
}
MSG_UPLOAD_CSV_PREVIEW = {
    'EN':"""🧐 There's the first 5 words of the file:
\n<code>word | translation | group</code>
{preview}
\n<b>Is that right?</b>"""

    ,'RU':"""🧐 Ниже первые 5 слов из файла:
\n<code>word | translation | group</code>
{preview}
\n<b>Всё верно?</b>"""
}

MSG_UPLOAD_CSV_YES = {
    'EN':"""✅ The words have been uploaded!"""
    ,'RU':"""✅ Слова загружены!"""
}
MSG_UPLOAD_CSV_YES_ERR = {
    'EN':"""⚠️ Error while uploading to the bot"""
    ,'RU':"""⚠️ Ошибка в процессе загрузки"""
}
MSG_UPLOAD_CSV_NO = {
    'EN':"""⏸ The loading has been stopped.\nAttach another CSV file
\nTo cancel — /cancel"""
    ,'RU':"""⏸ Загрузка остановлена.\nПрикрепи другой CSV файл
\nДля отмены — /cancel"""
}

MSG_UPLOAD_CSV_ERR_1 = {
    'EN':f"""⚠️ File not attached.\n\n{MSG_UPLOAD_CSV['EN']}"""
    ,'RU':f"""⚠️ Не прикреплен файл.\n\n{MSG_UPLOAD_CSV['RU']}"""
}
MSG_UPLOAD_CSV_ERR_2 = {
    'EN':f"""⚠️ This is not a CSV file.\n\n{MSG_UPLOAD_CSV['EN']}"""
    ,'RU':f"""⚠️ Загружен не CSV файл.\n\n{MSG_UPLOAD_CSV['RU']}"""
}
MSG_UPLOAD_CSV_ERR_3 = {
    'EN':f"""⚠️ CSV file is too big.\n\n{MSG_UPLOAD_CSV['EN']}"""
    ,'RU':f"""⚠️ CSV файл слишком большой.\n\n{MSG_UPLOAD_CSV['RU']}"""
}
MSG_UPLOAD_CSV_ERR_4 = {
    'EN':"""⚠️ Something went wrong....
CSV format — OK
Size up to 20 MB — OK

Try recreating the file and uploading again.
Common problems: 
1. incorrect encoding, you need UTF-8;
2. the file is incorrectly resaved, for example from XLSX to CSV.
3. file is empty
\nTo cancel — /cancel"""

    ,'RU':"""⚠️ Что-то пошло не так... 
Формат CSV — ОК
Размер до 20 MB — ОК

Попробуй пересоздать файл и загрузить заново.
Возможные проблемы: 
1. некорректная кодировка, нужна UTF-8;
2. файл некорректно пересохранен, например из XLSX в CSV.
3. файл пустой
\nДля отмены — /cancel"""
}

MSG_UPLOAD_CSV_ERR_5 = {
    'EN':"""⚠️ The file has blank fields in the 1st or 2nd column, for example in the {row} row.
Attach the corrected file
\nTo cancel — /cancel"""

    ,'RU':"""⚠️ В файле есть пустые поля в 1 или 2 столбце, например в строке {row}. 
Прикрепи скорректированный файл
\nДля отмены — /cancel"""
}

MSG_UPLOAD_CSV_ERR_6 = {
    'EN':"""⚠️ There are no words in the file. 
Attach the corrected file
\nTo cancel — /cancel"""

    ,'RU':"""⚠️ В файле нет слов. 
Прикрепи скорректированный файл
\nДля отмены — /cancel"""
}

"""----------------------------------------------------------------------"""
"""---------------------------DOWNLOAD_CSV-------------------------------"""
"""----------------------------------------------------------------------"""

MSG_DOWNLOAD_CSV = {
    'EN':"""📎 What are the words to download?"""
    ,'RU':"""📎 Какие слова скачать?"""
}

MSG_DOWNLOAD_CSV_CONCEL = {
    'EN':"""🔙 Download mode is off"""
    ,'RU':"""🔙 Вышел из режима скачивания"""
}

MSG_DOWNLOAD_CSV_GROUPS = {
    'EN':"""⚙️ Write the <b>number</b> of the group to download it.
The groups are given in the format:
<code>[number] — [title] | [number_of_words]</code>\n
{user_groups}\nTo cancel — /cancel"""

    ,'RU':"""⚙️ Напиши <b>номер</b> группы, чтобы скачать её.
Группы приведены в формате:
<code>[номер] — [название] | [кол-во слов]</code>\n
{user_groups}\nДля отмены — /cancel"""
}

MSG_DOWNLOAD_CSV_ALL = {
    'EN':"""✔️ All words downloaded"""
    ,'RU':"""✔️ Скачены все слова"""
}
MSG_DOWNLOAD_CSV_GROUP = {
    'EN':"""✔️ Group downloaded: <b>{group}</b>"""
    ,'RU':"""✔️ Скачена группа: <b>{group}</b>"""
}



"""----------------------------------------------------------------------"""
"""----------------------------DUPLICATE---------------------------------"""
"""----------------------------------------------------------------------"""

MSG_DUPLICATE = {
    'EN':"""🔗 Duplicated words in the format:
<code>[word] — [number_of_duplicates] | [groups]</code>
*If the group is <b>None</b>, then the word has no group specified.\n\n{duplicates}"""

    ,'RU':"""🔗 Повторяющиеся слова в формате:
<code>[слово] — [количество повторений] | [группы]</code>
*Если группа <b>None</b>, значит у слова не указана группа.\n\n{duplicates}"""
}

MSG_DUPLICATE_NO_WORDS = {
    'EN':"""🔗 No duplicated words"""
    ,'RU':"""🔗 Нет повторяющихся слов"""
}


"""----------------------------------------------------------------------"""
"""------------------------------DELETE----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_DELETE = {
    'EN':"""⚠️ Write the word to be deleted\n\nTo cancel — /cancel"""
    ,'RU':"""⚠️ Напиши слово, которое нужно удалить\n\nДля отмены — /cancel"""
}
MSG_DELETE_ERROR = {
    'EN':"""🔙 There is no such word. Delete Mode is off.\nDelete another word? — /delete"""
    ,'RU':"""🔙 Такого слова нет. Вышел из режима удаления.\nУдалим другое слово? — /delete"""
}
MSG_DELETE_ERROR_DB = {
    'EN':"""🔙 Deletion error. Try to delete the translation of word — /delete"""
    ,'RU':"""🔙 Ошибка в удалении. Попробуй удалить перевод слова — /delete"""
}
MSG_DELETE_DELETED = {
    'EN':"""🗑 Deleted. Delete mode is off.\nDelete another word? — /delete"""
    ,'RU':"""🗑 Удалил. Вышел из режима удаления.\nУдалим другое слово? — /delete"""
}

MSG_DELETE_ALL = {
    'EN':"""⚠️ To start the process of deleting all words, run again — /delete_all\n\nTo cancel — /cancel"""
    ,'RU':"""⚠️ Чтобы запустить процесс удаления всех слов напиши еще раз — /delete_all\n\nДля отмены — /cancel"""
}
MSG_DELETE_ALL_X2 = {
    'EN':"""‼️ You will not be able to get words back after deleting
Delete all words? — /yes\n\nTo cancel — /cancel"""
    ,'RU':"""‼️ После удаления слова нельзя будет восстановить.
Чтобы удалить все слова — /yes\n\nДля отмены — /cancel"""
}
MSG_DELETE_ALL_DELETED = {
    'EN':"""🗑 All words have been deleted"""
    ,'RU':"""🗑 Удалил все слова"""
}


"""----------------------------------------------------------------------"""
"""----------------------CHANGE GROUP FOR WORDS--------------------------"""
"""----------------------------------------------------------------------"""

CHANGE_GROUP_FOR_WORDS = {
    'EN':"""🛠 Which words have a different group?"""
    ,'RU':"""🛠 У каких слов нужно изменить группу?"""
}

CHANGE_GROUP_FOR_WORDS_CONCEL = {
    'EN':"""🔙 Group change mode is off"""
    ,'RU':"""🔙 Вышел из режима изменения групп"""
}


"""----------------------------------------------------------------------"""
"""------------------------------CANCEL----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_CANCEL = {
    'EN':"""💬 Cancel what? Nothing is happening :)"""
    ,'RU':"""💬 Что отменить? Ничего и не происходит :)"""
}

MSG_CANCEL_DELETE = {
    'EN':"""🔙 Deletion mode is off"""
    ,'RU':"""🔙 Вышел из режима удаления"""
}

MSG_CANCEL_REMINDER = {
    'EN':"""🔙 Card mode is off"""
    ,'RU':"""🔙 Вышел из режима карточек"""
}

MSG_CANCEL_CHANGE_GROUP = {
    'EN':"""🔙 Group selection mode is off"""
    ,'RU':"""🔙 Вышел из режима выбора групп"""
}

MSG_CANCEL_UPLOAD_CSV = {
    'EN':"""🔙 CSV upload mode is off"""
    ,'RU':"""🔙 Вышел из режима загрузки csv"""
}

MSG_CANCEL_CHANGE_DOWNLOAD = {
    'EN':"""🔙 Download mode is off"""
    ,'RU':"""🔙 Вышел из режима скачивания"""
}

MSG_CANCEL_NOTIFICATIONS = {
    'EN':"""🔙 The notification frequency setting mode is off"""
    ,'RU':"""🔙 Вышел из режима настройки частоты уведомлений"""
}

MSG_CANCEL_LANGUAGE = {
    'EN':"""🔙 The interface language change mode is off\n/language — to change the language"""
    ,'RU':"""🔙 Вышел из режима изменения языка интерфейса\n/language — to change the language"""
}

MSG_CANCEL_GENETAL = {
    'EN':"""🔙 Canceled"""
    ,'RU':"""🔙 Отменил"""
}


"""----------------------------------------------------------------------"""
"""---------------------------NOTIFICATIONS------------------------------"""
"""----------------------------------------------------------------------"""

MSG_NOTIFICATIONS_INFO = {
    'EN':"""🔔 Current notification frequency:\n<b>{notification_freq}</b> {add_info}\n
⚙️ Change the frequency of notifications and receive them after:"""
    ,'RU':"""🔔 Текущая частота уведомлений:\n<b>{notification_freq}</b> {add_info}\n
⚙️ Изменить частоту уведомлений на:"""
}
MSG_NOTIFICATIONS_ADD_INFO = {
    'EN':"""after inaction"""
    ,'RU':"""после бездействия"""
}

MSG_NOTIFICATIONS_SET = {
    'EN':"""🔔 The notification frequency is selected:\n<b>{notification_freq}</b> {add_info}"""
    ,'RU':"""🔔 Выбрана частота уведомлений:\n<b>{notification_freq}</b> {add_info}"""
}
MSG_NOTIFICATIONS_SET_NEVER = {
    'EN':"""🔕 The notification frequency is selected: <b>{notification_freq}</b>"""
    ,'RU':"""🔕 Выбрана частота уведомлений: <b>{notification_freq}</b>"""
}

MSG_NOTIFICATIONS = {
    'EN':"""🧠 Let's repeat the words or add new ones?\n
/cards — go to card mode
/notifications — customize the frequency of notifications"""

    ,'RU':"""🧠 Повторим слова или добавим новые?\n
/cards — перейти в режим карточек
/notifications — настроить частоту уведомлений"""
}

"""----------------------------------------------------------------------"""
"""------------------------------DONATE----------------------------------"""
"""----------------------------------------------------------------------"""

MSG_DONATE = {
    'EN':"""/donate — support the project!"""
    ,'RU':"""/donate — чтобы поддержать проект!"""
}

MSG_DONATE_INFO = {
    'EN':"""💸 Please support the Anki bot project:

Patreon — https://www.patreon.com/sergeylix
/Georgian_iban — GE44BG0000000538934249 (Sergei Likhachev)
/BUSD_BEP20: 0xaFC0c26B0eD046c704C346c135430f132938cD9a
/USDT_TRC20: TDC8ba6kKfZYBQbhcJ8PypsnfCoFNL74rQ
/USDC_ERC20: 0xaFC0c26B0eD046c704C346c135430f132938cD9a

Thank you for your support."""

    ,'RU':"""💸 Пожалуйста, поддержи разработку бота Anki:

Patreon — https://www.patreon.com/sergeylix
/Georgian_iban — GE44BG0000000538934249 (Sergei Likhachev)
/BUSD_BEP20: 0xaFC0c26B0eD046c704C346c135430f132938cD9a
/USDT_TRC20: TDC8ba6kKfZYBQbhcJ8PypsnfCoFNL74rQ
/USDC_ERC20: 0xaFC0c26B0eD046c704C346c135430f132938cD9a

Спасибо за поддержку."""
}

MSG_DONATE_Georgian_iban = """GE44BG0000000538934249"""

MSG_DONATE_BUSD_BEP20 = """0xaFC0c26B0eD046c704C346c135430f132938cD9a"""

MSG_DONATE_USDT_TRC20 = """TDC8ba6kKfZYBQbhcJ8PypsnfCoFNL74rQ"""

MSG_DONATE_USDC_ERC20 = """0xaFC0c26B0eD046c704C346c135430f132938cD9a"""


"""----------------------------------------------------------------------"""
"""-----------------------COMMAND NOT DEFINED----------------------------"""
"""----------------------------------------------------------------------"""

MSG_COMMAND_NOT_DEFINED = {
    'EN':"""💬 Don't get it. Maybe it's missing the '=' sign?"""
    ,'RU':"""💬 Не понимаю. Может не хватает знака '='?"""
}

"""----------------------------------------------------------------------"""
"""---------------------------SEND FOR ALL-------------------------------"""
"""----------------------------------------------------------------------"""

MSG_SEND_FOR_ALL = """✉️ Напиши сообщение, которое получат все пользователи.\n\nДля отмены — /cancel"""
MSG_SEND_FOR_ALL_SUCCESS = """✔️ Сообщения отправлены пользователям: <b>{count}</b>.\nНедоставлено:\n{not_delivered}"""

"""----------------------------------------------------------------------"""
"""-----------------------------SQL QUERY--------------------------------"""
"""----------------------------------------------------------------------"""

MSG_SQL_QUERY = """Напиши SQL запрос. После запроса автоматически добавится limit 20, если это SELECT или WITH.\n\nДля отмены — /cancel"""

MSG_SQL_QUERY_ERROR = """Ошибка в запросе. Вышел из режима написания запросов"""
MSG_SQL_QUERY_COMMAND_ERROR = """Команда не поддерживается"""

MSG_SQL_QUERY_DONE = """✔️ Запрос выполнен"""
MSG_SQL_QUERY_RETURN = """✔️ Результат запроса:\n\n{output}"""


"""----------------------------------------------------------------------"""
"""------------------------------KEYBOARDS-------------------------------"""
"""----------------------------------------------------------------------"""

KB_CARDS_SHOW_TRANSLATION = {
    'EN':"Show translation"
    ,'RU':"Показать перевод"
}
KB_CARDS_SHOW_CANCEL = {
    'EN':"Turn off the mode"
    ,'RU':"Выйти из режима"
}
KB_CARDS_SHOW_OPTIONS = {
    'EN':"Options"
    ,'RU':"Параметры"
}

KB_WORD_OPTIONS_DELETE = {
    'EN':"Delete this word"
    ,'RU':"Удалить это слово"
}
KB_WORD_OPTIONS_BACK = {
    'EN':"Back to cards"
    ,'RU':"Вернуться к карточке"
}
KB_WORD_OPTIONS_GO_TO_GOOGLETRANS = {
    'EN':"Open in Google Translate"
    ,'RU':"Открыть в Google Translate"
}
GOOGLETRANS_LINK = """https://translate.google.com/?hl=en&sl={sl}&tl={tl}&text={text}&op=translate"""

KB_WORD_OPTIONS_GO_TO_GOOGLETRANS_TRANS = {
    'EN':"Translate: "
    ,'RU':"Перевести: "
}

KB_CARD_OPTIONS_DELETED_SURE = {
    'EN':"Yes, delete this word"
    ,'RU':"Да, удали это слово"
}
KB_CARD_OPTIONS_DELETE_BACK = {
    'EN':"Back to options"
    ,'RU':"Вернуться к параметрам"
}
WORD_OPTIONS_DELETED = {
    'EN':"(deleted)"
    ,'RU':"(удалено)"
}

KB_UPLOAD_YES = {
    'EN':"Yes, save the words"
    ,'RU':"Да, сохранить слова"
}
KB_UPLOAD_NO = {
    'EN':"No, I'll upload another file"
    ,'RU':"Нет, загружу другой файл"
}
KB_UPLOAD_CANCEL = {
    'EN':"Cancel"
    ,'RU':"Отмена"
}

KB_DOWNLOAD_ALL = {
    'EN':"Download all words"
    ,'RU':"Скачать все слова"
}
KB_DOWNLOAD_GROUP = {
    'EN':"Download group of words"
    ,'RU':"Скачать группу слов"
}
KB_DOWNLOAD_CANCEL = {
    'EN':"Cancel"
    ,'RU':"Отмена"
}

KB_CHANGE_GR_ONE_WORD = {
    'EN':"Change for one word"
    ,'RU':"Изменить у одного слова"
}
KB_CHANGE_GR_IN_GR = {
    'EN':"Change for group"
    ,'RU':"Изменить у группы"
}
KB_CHANGE_GR_ALL = {
    'EN':"Change for all words"
    ,'RU':"Изменить у всех слов"
}
KB_CHANGE_GR_CANCEL = {
    'EN':"Cancel"
    ,'RU':"Отмена"
}

KB_NOTIFICATIONS_DAY = {
    'EN':"One day"
    ,'RU':"Через день"
}
KB_NOTIFICATIONS_2DAYS = {
    'EN':"Two days"
    ,'RU':"Через два дня"
}
KB_NOTIFICATIONS_WEEK = {
    'EN':"One week"
    ,'RU':"Через неделю"
}
KB_NOTIFICATIONS_MONTH = {
    'EN':"One month"
    ,'RU':"Через месяц"
}
KB_NOTIFICATIONS_NEVER = {
    'EN':"Never"
    ,'RU':"Никогда"
}
KB_NOTIFICATIONS_CONCEL = {
    'EN':"Cancel"
    ,'RU':"Отмена"
}