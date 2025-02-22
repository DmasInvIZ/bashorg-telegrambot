""""
Телеграм-бот, пока умеет только присылать рандомную цитату с сайта bashorg.org и отвечать на вопрос 'Кто я?'
Для запуска потребуются некоторые библиотеки:
    pyTelegrambotApi
    beautifulsoup4
    lxml
"""
from aiogram.utils.markdown import hlink
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from token_file import token
import logging
from threading import Timer
import random
from datetime import datetime, timezone, timedelta, time


keywords = "шутк", ",бугага", "смешн", "смех", "шути", "юмор", "прикол", "смех", "сарказм", "ирония", "гэг", \
           "остр", "пранк", "комизм", "смешинка", "задор", "хохма", "анекдот", "ржака", "балаган", \
           "курьез", "сатира", "абсурд", "веселье", "стёб", "подкол", "аллюзия", \
           "комед", "лол", "ахах", "ржунимагу"

logger = logging.getLogger('logger')
custom_time_format = '%Y-%m-%d %H:%M:%S'
logging.basicConfig(level=logging.INFO,
                    filename="file.log",
                    filemode="w",
                    format='%(asctime)s – %(message)s',
                    datefmt=custom_time_format)

bot = telebot.TeleBot(token)
url = "https://xn--80abh7bk0c.xn--p1ai/random"

timer = None
chat_id = None
chat_type = None
time_start = time(9, 0, 0)  # 9:00
time_stop = time(21, 0, 0)  # 21:00

quotes_array = []


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветствие"""
    global chat_type
    chat_type = message.chat.type
    global chat_id
    chat_id = message.chat.id
    print(f"Бот находится в чате типа - {chat_type}")

    logging.info(f"Бот находится в чате типа - {chat_type}")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/random")
    markup.add(btn1)
    bot.reply_to(message, "Привет {0.first_name}! Нажми кнопку или напиши команду /random чтобы получить рандомную цитату. \n \
    Внутри групповых чатов бот будет шутить спустя какое-то время тишины, время активности бота с 9.00 до 21.00. \n \
    Боту можно писать в ЛС, отвечать он будет только на запрос цитат, шутить в рандомное время в ЛС он не будет."\
                 .format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=['random'])
def send_quote(message):
    """Отправка рандомной цитаты"""
    try:
        print('Запрос от {0.first_name}'.format(message.from_user))
        quote = get_quote()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("/random")
        markup.add(btn1)
        bot.reply_to(message, quote, reply_markup=markup, parse_mode='HTML')
        logger.info('Запрос от {0.first_name}'.format(message.from_user))

    except Exception as err:
        print(err)
        logging.info(err)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("/random")
        markup.add(btn1)
        bot.reply_to(message, "Что-то не так...", reply_markup=markup, parse_mode='HTML')
        send_quote(message)


def timer_for_joke():
    if chat_type == "private":
        print(f"Бот не в групповом чате, таймер не включен")
        return
    print("таймер")
    global timer
    if timer:
        timer.cancel()

    next_joke_time = random.randint(60 * 60, 60 * 60 * 5)  # время до следующей шутки в секундах
    timer = Timer(next_joke_time, joking)
    timer.start()
    print(f"Следующая автошутка через {round(next_joke_time / 60)} минут")
    print(f'Серверное время - {datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M:%S")}')
    logging.info(f"Следующая автошутка через {round(next_joke_time / 60)} минут")


def joking():
    if time_start < datetime.now(timezone(timedelta(hours=3))).time().replace(
            microsecond=0) < time_stop:  # проверяем можно ли шутить сейчас
        joke = get_quote()
        bot.send_message(chat_id, f"Что-то тут тихо... " + "\n" + "\n" + joke, parse_mode='HTML')
    else:
        print("Сейчас не время")
        print(f'Серверное время - {datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M:%S")}')
        logging.info("Сейчас не время")
        timer_for_joke()


def load_quotes():
    """Загружает цитаты в массив"""
    response = requests.get(url, verify=False)                                          # получаем страницу от сервера
    soup = BeautifulSoup(response.text, 'lxml')                                         # создаем объект html страницы
    articles = soup.find('section', class_='quotes')
    article = articles.find_all('article', class_='quote')
    if article:
        try:
            for i in article:
                quote_date = i.find('header', class_='quote__header').find('div',
                    class_='quote__header_date').text.strip()[0:10]                         # получаем дату
                quote_number = i.find('header', class_='quote__header').find('a',
                            class_='quote__header_permalink').text                          # получаем номер цитаты
                quote_link = i.find('header', class_='quote__header').find('a',
                            class_='quote__header_permalink').get('href')                   # получаем ссылку на цитату
                quote_text = str(i.find('div', class_='quote__body')) \
                    .replace('<br/>', '\n') \
                    .replace('</div>', '') \
                    .replace('<div class="quote__body">', '') \
                    .replace('&lt;', '  ') \
                    .replace('&gt;', '  -').strip()                                         # готовая строка с цитатой
                link = hlink(quote_number, f'https://xn--80abh7bk0c.xn--p1ai{quote_link}')  # формируем ссылку для телеграм
                quote = str(f'{link} - Добавлено {quote_date}\n\n{quote_text}')          # готовая цитата
                quotes_array.append(quote)

        except UnicodeEncodeError:
            print("Ошибка в получении цитат, еще попытка")
            logging.info("Ошибка в загрузке цитат, еще попытка")
            load_quotes()

    else:
        print('Что-то не так, переменная "article" пуста')
        logging.info('Что-то не так, переменная "article" пуста')


def get_quote():
    """Достаем рандомную цитату, отправляем пользователю и удаляем из массива"""
    if not quotes_array:
        print("Загружаю цитаты")
        logging.info("Загружаю цитаты")
        load_quotes()
    quote_random_number = random.randint(0, len(quotes_array) - 1)
    print(f"В списке {len(quotes_array)} цитат, выбрана {quote_random_number}")
    logging.info(f"В списке {len(quotes_array)} цитат, выбрана {quote_random_number}")
    quote = quotes_array[quote_random_number]
    quotes_array.pop(quote_random_number)
    timer_for_joke()
    return quote


@bot.message_handler(content_types=['text'])
def scanning_messages(message):
    for i in keywords:
        if i in message.text.lower():
            print(f"Триггер сработал на слово {message.text}")
            logging.info(f"{message.from_user.first_name} что-то сказал(ла) про юмор? |{message.text}|")
            bot.send_message(message.chat.id, f"{message.from_user.first_name} что-то сказал(ла) про шутки?",
                             parse_mode='HTML')
            joke = get_quote()
            bot.send_message(message.chat.id, joke, parse_mode='HTML')
    timer_for_joke()


print("Started...")
print(f'Серверное время - {datetime.now(timezone(timedelta(hours=3))).strftime("%H:%M:%S")}')
try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)  # параметр для игнорирования сообщений присланных когда бот был не активен
except telebot.apihelper.ApiTelegramException as error:
    print(f"{error} ------- Ошибка в основном цикле программы, перезапуск")
    logging.info(f"{error} ------- Ошибка в основном цикле программы")

