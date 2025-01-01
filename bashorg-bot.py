""""
Телеграм-бот, пока умеет только присылать рандомную цитату с сайта bashorg.org и отвечать на вопрос "Кто я?"
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
import datetime


keywords = "шутк", ",бугага", "смешн", "смех", "шути", "юмор", "прикол", "смех", "сарказм", "ирония", "гэг", \
           "остр", "пранк", "комизм", "смешинка", "задор", "хохма", "анекдот", "ржака", "балаган", \
           "курьез", "сатира", "абсурд", "веселье", "стёб", "подкол", "аллюзия", "легкомысленность", \
           "комед", "лол", "ахах", "ржунимагу"

logger = logging.getLogger('logger')
logging.basicConfig(level=logging.INFO, filename="file.log", filemode="w")

bot = telebot.TeleBot(token)
url = "https://xn--80abh7bk0c.xn--p1ai/random"

timer = None
chat_id = None

quotes_array = []


def timer_for_joke():
    global timer
    if timer:
        timer.cancel()
    if "21:00:00" < datetime.datetime.now().strftime("%H:%M:%S") < "9:00:00":       # время в которое шуток не будет
        # print("Сейчас не время")
        logging.info("Сейчас не время")
        next_joke_time = random.randint(60*60*3, 60*60*6)        # время до следующей шутки в секундах
        # print(f"Таймер сработает через {next_joke_time/60} минут")
        logging.info(f"Таймер сработает через {round(next_joke_time/60)} минут")
        timer = Timer(next_joke_time, timer_for_joke)
        timer.start()
    else:
        next_joke_time = random.randint(60*60*1, 60*60*5)
        # print(f"Следующая цитата через {round(next_joke_time/60)} минут")
        logging.info(f"Следующая цитата через {round(next_joke_time/60)} минут")
        timer = Timer(next_joke_time, joking)  # изменить время на рандомное
        timer.start()  # настроить таймер чтобы не срабатывал ночью


def joking():
    joke = get_quote()
    bot.send_message(chat_id, f"Что-то тут тихо... " + "\n" + "\n" + joke, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветствие"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/random")
    markup.add(btn1)
    bot.reply_to(message, 'Привет {0.first_name}! Нажми кнопку или напиши команду /random \
            чтобы получить рандомную цитату'.format(message.from_user), reply_markup=markup)


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

    except Exception as error:
        # print(error)
        logging.info(error)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("/random")
        markup.add(btn1)
        bot.reply_to(message.chat.id, "Что-то не так...", reply_markup=markup, parse_mode='HTML')


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
                quote = str(f'{link} - Добавлено {quote_date}\n{quote_text}')          # готовая цитата
                quotes_array.append(quote)

        except UnicodeEncodeError:
            # print("Ошибка в получении цитат, еще попытка")
            logging.info("Ошибка в получении цитат, еще попытка")
            load_quotes()

    else:
        # print('Что-то не так, переменная "article" пуста')
        logging.info('Что-то не так, переменная "article" пуста')


def get_quote():
    """Достаем рандомную цитату, отправляем пользователю и удаляем из массива"""
    if not quotes_array:
        # print("Загружаю цитаты")
        logging.info("Загружаю цитаты")
        load_quotes()
    quote_random_number = random.randint(0, len(quotes_array) - 1)
    # print(f"В списке {len(quotes_array)} цитат, выбрана {quote_random_number}")
    logging.info(f"В списке {len(quotes_array)} цитат, выбрана {quote_random_number}")
    quote = quotes_array[quote_random_number]
    quotes_array.pop(quote_random_number)
    timer_for_joke()
    return quote


@bot.message_handler(content_types=['text'])
def scanning_messages(message):
    global chat_id
    chat_id = message.chat.id
    for i in keywords:
        if i in message.text.lower():
            # print(message.text)
            logging.info(f"{message.from_user.first_name} что-то сказал(ла) про шутки? |{message.text}|")
            bot.send_message(message.chat.id, f"{message.from_user.first_name} что-то сказал(ла) про шутки?",
                             parse_mode='HTML')
            joke = get_quote()
            bot.send_message(message.chat.id, joke, parse_mode='HTML')
    timer_for_joke()


print("Started...")
bot.infinity_polling()

