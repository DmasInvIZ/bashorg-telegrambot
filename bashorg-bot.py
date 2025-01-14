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
import time


keywords = "шутк", ",бугага", "смешн", "смех", "шути", "юмор", "прикол", "смех", "сарказм", "ирония", "гэг", \
           "острота", "пранк", "фантазия", "комизм", "смешинка", "задор", "хохма", "анекдот", "ржака", "балаган", \
           "курьез", "сатира", "абсурд", "веселье", "стёб", "подкол", "аллюзия", "легкомысленность", \
           "пародия", "гротеск", "комед", "лол", "ахаха", "ржунимагу"

logger = logging.getLogger('logger')
logging.basicConfig(level=logging.INFO, filename="file.log", filemode="w")

bot = telebot.TeleBot(token)
url = "https://xn--80abh7bk0c.xn--p1ai/random"

last_call_time = None


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветствие"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/random")
    # btn2 = types.KeyboardButton("Кто ты?")
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
        #logger.info('Ответ: \n', answer, "\n".format(message.from_user))

    except Exception as error:
        print(error)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("/random")
        markup.add(btn1)
        bot.send_message(message.chat.id, "Что-то не так...", reply_markup=markup, parse_mode='HTML')


def get_quote():
    response = requests.get(url)  # получаем страницу от сервера
    soup = BeautifulSoup(response.text, 'lxml')  # создаем объект html страницы
    articles = soup.find('section', class_='quotes')
    article = articles.find('article', class_='quote')
    quote_date = article.find('header', class_='quote__header').find('div', class_='quote__header_date').text.strip()[0:10]  # получаем дату
    quote_number = article.find('header', class_='quote__header').find('a',
                                                                       class_='quote__header_permalink').text  # получаем номер цитаты
    quote_link = article.find('header', class_='quote__header').find('a', class_='quote__header_permalink').get(
        'href')  # получаем ссылку на цитату
    quote_text = str(article.find('div', class_='quote__body')) \
        .replace('<br/>', '\n') \
        .replace('</div>', '') \
        .replace('<div class="quote__body">', '') \
        .replace('&lt;', '  ') \
        .replace('&gt;', '  -').strip()  # готовая строка с цитатой
    link = hlink(quote_number, f'https://xn--80abh7bk0c.xn--p1ai{quote_link}')  # формируем ссылку для телеграмм
    answer = str(f'{link} - Добавлено {quote_date}\n{quote_text}')  # формируем ответ для пользователя
    return answer


# @bot.message_handler(content_types=['text'])
# def dialog(message):
#     if message.text == "Кто ты?":
#         bot.reply_to(message, text="Рад что ты спросил... Я БОТ! Я вывожу случайную \
#         цитату с сайта башорг.рф. Пока я умею только это, но мой создатель работает \
#         над улучшением и расширением моих способностей 😎")
#     else:
#         bot.send_message(message.chat.id, text="Ничего не понял...")


@bot.message_handler(content_types=['text'])
def scanning_messages(message):
    print(message)
    for i in keywords:
        if i in message.text.lower():
            print(message.text)
            bot.send_message(message.chat.id, f"{message.from_user.first_name} сказал(ла) что-то про шутки?", parse_mode='HTML')
            joke = get_quote()
            bot.send_message(message.chat.id, joke, parse_mode='HTML')
            # send_quote(message)


# now_time = time.time()
# if now_time - last_time_calling > 10:
#     joke = get_quote()
#     bot.send_message(-1002438393620, f"Что-то тут тихо... " + "\n" + joke, parse_mode='HTML')


print("Started...")
bot.infinity_polling()



