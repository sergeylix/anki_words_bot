MSG = """Этот бот сохраняет слова и их перевод, кроме этого можно просматривать слова и вспоминать их перевод в режиме карточек.\n
Напиши слово, затем знак равно '=', и затем перевод. И бот сохранит слово в твоей базе слов.
Например: hello = привет"""

MSG_HELP = """Коменды:
/help - вывести список команд
/cards - включить режим карточек (режим напоминания слов)
/my_words - вывести последние 15 сохраненных слов
/my_words_num - вывести количество сохраненных слов
/duplicates - вывести дублирующиеся слова
/download_csv - скачать все слова в csv
/delete - включить режим удаления слов
/delete_all - удаление всех слов
/cancel - выход из любого режима"""

MSG_START = MSG + "\n\n" + MSG_HELP

MSG_AUTH_HELP = """Команды доступные только автору:
/auth - просмотр списка команд автора
/access <user_id> - выдача доступа
/block <user_id> - блокировка доступа
/access_request - запросить доступ (доступно всем)
/query - режим выполнения SQL скриптов
"""

MSG_DONATE = """/donate - support the project!"""

MSG_DONATE_INFO = """Please support the memorising words bot project:
Patreon - https://www.patreon.com/sergeylix
/Georgian_iban - GE44BG0000000538934249 (Sergei Likhachev)
/BUSD_BEP20: 0xaFC0c26B0eD046c704C346c135430f132938cD9a
/USDT_TRC20: TDC8ba6kKfZYBQbhcJ8PypsnfCoFNL74rQ
/USDC_ERC20: 0xaFC0c26B0eD046c704C346c135430f132938cD9a
"""

MSG_DONATE_Georgian_iban = """GE44BG0000000538934249"""

MSG_DONATE_BUSD_BEP20 = """0xaFC0c26B0eD046c704C346c135430f132938cD9a"""

MSG_DONATE_USDT_TRC20 = """TDC8ba6kKfZYBQbhcJ8PypsnfCoFNL74rQ"""

MSG_DONATE_USDC_ERC20 = """0xaFC0c26B0eD046c704C346c135430f132938cD9a"""