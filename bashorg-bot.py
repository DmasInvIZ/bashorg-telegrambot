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
import sqlite3
import os
from os import path


def create_database():
    """Cоздаем БД и ее таблицы, если их нет"""
    os.chdir(r"D:\Prog\Python\Projects\bashorg-telegrambot")
    if not path.exists("sqdb.db"):
        try:
            print("Создаем БД")
            connection = sqlite3.connect("sqdb.db")
            cursor = connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Quotes (
                id INTEGER PRIMARY KEY,
                quote TEXT
                )
                ''')

            connection.commit()

        except Exception as error:
            print(error)

        else:
            connection.close()

    else:
        print("БД существует")


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


def timer_for_joke():
    global timer
    if timer:
        timer.cancel()
    if "21:00:00" < datetime.datetime.now().strftime("%H:%M:%S") < "9:00:00":
        print("Сейчас не время")
        next_joke_time = random.randint(60*60*3, 60*60*6)
        print(f"Таймер сработает через {next_joke_time} секунд")
        timer = Timer(next_joke_time, timer_for_joke)
        timer.start()
    else:
        next_joke_time = random.randint(60*60*1, 60*60*5)
        print(f"Следующая цитата через {next_joke_time} секунд")
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
        print(error)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("/random")
        markup.add(btn1)
        bot.send_message(message.chat.id, "Что-то не так...", reply_markup=markup, parse_mode='HTML')


def load_quotes():
    response = requests.get(url, verify=False)  # получаем страницу от сервера
    soup = BeautifulSoup(response.text, 'lxml')  # создаем объект html страницы
    articles = soup.find('section', class_='quotes')
    article = articles.find_all('article', class_='quote')
    if article:
        connection = sqlite3.connect("sqdb.db")
        cursor = connection.cursor()
        try:
            for i in article:
                quote_date = i.find('header', class_='quote__header').find('div',
                                                                                 class_='quote__header_date').text.strip()[0:10]
                quote_number = i.find('header', class_='quote__header').find('a',
                                                                                   class_='quote__header_permalink').text
                quote_link = i.find('header', class_='quote__header').find('a',
                                                                                 class_='quote__header_permalink').get('href')
                quote_text = str(i.find('div', class_='quote__body')) \
                    .replace('<br/>', '\n') \
                    .replace('</div>', '') \
                    .replace('<div class="quote__body">', '') \
                    .replace('&lt;', '  ') \
                    .replace('&gt;', '  -').strip()  # готовая строка с цитатой
                link = hlink(quote_number, f'https://xn--80abh7bk0c.xn--p1ai{quote_link}')
                quote = str(f'{link} - Добавлено {quote_date}\n{quote_text}')
                print(quote)
                cursor.execute("INSERT INTO Quotes (quote) VALUES (?)", (quote,))

        except UnicodeEncodeError:
            print("Ошибка в получении цитат, еще попытка")
            load_quotes()

        except sqlite3.OperationalError:
            print("Ошибка записи в БД, проверь синтаксис")

        finally:
            connection.commit()
            connection.close()
    else:
        print('Что-то не так, переменная "article" пуста')


create_database()
load_quotes()


def get_quote():
    response = requests.get(url, verify=False)  # получаем страницу от сервера
    soup = BeautifulSoup(response.text, 'lxml')  # создаем объект html страницы
    articles = soup.find('section', class_='quotes')
    article = articles.find('article', class_='quote')
    quote_date = article.find('header', class_='quote__header').find('div',
                                        class_='quote__header_date').text.strip()[0:10]  # получаем дату
    quote_number = article.find('header', class_='quote__header').find('a',
                                        class_='quote__header_permalink').text  # получаем номер цитаты
    quote_link = article.find('header', class_='quote__header').find('a',
                                        class_='quote__header_permalink').get('href')  # получаем ссылку на цитату
    quote_text = str(article.find('div', class_='quote__body')) \
        .replace('<br/>', '\n') \
        .replace('</div>', '') \
        .replace('<div class="quote__body">', '') \
        .replace('&lt;', '  ') \
        .replace('&gt;', '  -').strip()  # готовая строка с цитатой
    link = hlink(quote_number, f'https://xn--80abh7bk0c.xn--p1ai{quote_link}')  # формируем ссылку для телеграмм
    answer = str(f'{link} - Добавлено {quote_date}\n{quote_text}')  # формируем ответ для пользователя
    timer_for_joke()
    return answer


@bot.message_handler(content_types=['text'])
def scanning_messages(message):
    global chat_id
    chat_id = message.chat.id
    for i in keywords:
        if i in message.text.lower():
            print(message.text)
            bot.send_message(message.chat.id, f"{message.from_user.first_name} что-то сказал(ла) про шутки?",
                             parse_mode='HTML')
            joke = get_quote()
            bot.send_message(message.chat.id, joke, parse_mode='HTML')
    timer_for_joke()


print("Started...")
# create_database()
# bot.infinity_polling()

