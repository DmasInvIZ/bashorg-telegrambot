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

bot = telebot.TeleBot(token)
url = "https://xn--80abh7bk0c.xn--p1ai/random"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветствие"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/random")
    btn2 = types.KeyboardButton("Кто ты?")
    markup.add(btn1, btn2)
    bot.reply_to(message, 'Привет {0.first_name}! Нажми кнопку или напиши команду /random \
            чтобы получить рандомную цитату'.format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=['random'])
def send_quote(message):

    """Отправка рандомной цитаты"""
    print('Запрос от {0.first_name}'.format(message.from_user))  #########
    response = requests.get(url)                                            # получаем страницу от сервера
    soup = BeautifulSoup(response.text, 'lxml')                             # создаем объект html страницы

    date = soup.find('div', class_='quote__header_date').text.strip()[0:10]  # получаем дату
    quote_num = soup.find('a', class_='quote__header_permalink').text  # получаем номер цитаты
    print(quote_num)
    quote_num_link = soup.find('a', class_='quote__header_permalink').get('href')
    print(quote_num_link)
    dirty_quote = str(soup.find('div', class_='quote__frame').find('div', class_='quote__body'))  # строка с цитатой со спец символами и со склееными строками
    quote = dirty_quote.replace("<br/>", "\n").replace('<div class="quote__body">', "").replace("</div>", "")\
        .replace('&lt;', '<').replace('&gt;', '>').strip()  # готовая строка с цитатой

    #link = hlink(f"{quote_num}", "https://xn--80abh7bk0c.xn--p1ai{quote_num_link}")
    #print(link)
    answer = f'{quote_num} - {date}' + "\n" + quote
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/random")
    markup.add(btn1)
    bot.send_message(message.chat.id, answer, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(content_types=['text'])
def dialog(message):
    if message.text == "Кто ты?":
        bot.reply_to(message, text="Рад что ты спросил... Я БОТ! Я вывожу случайную \
        цитату с сайта башорг.рф. Пока я умею только это, но мой создатель работает \
        над улучшением и расширением моих способностей 😎")
    else:
        bot.send_message(message.chat.id, text="Ничего не понял...")


print("Started...")
bot.infinity_polling()
