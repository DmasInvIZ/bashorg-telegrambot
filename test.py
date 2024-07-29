from aiogram.utils.markdown import hlink
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
from token_file import token

bot = telebot.TeleBot(token)
url = "https://xn--80abh7bk0c.xn--p1ai/random"


def find_quote():
    response = requests.get(url)                                                # получаем страницу от сервера
    soup = BeautifulSoup(response.text, 'lxml')                                   # создаем объект html страницы
    quotes = list()
    articles = soup.find('section', class_='quotes')
    article = articles.find('article', class_='quote')
    quote_date = article.find('header', class_='quote__header').find('div', class_='quote__header_date').text.strip()[0:10]
    quote_number = article.find('header', class_='quote__header').find('a', class_='quote__header_permalink').text
    quote_link = article.find('header', class_='quote__header').find('a', class_='quote__header_permalink').get('href')
    quote_text = str(article.find('div', class_='quote__body'))\
                     .replace('<br/>', '\n')\
                     .replace('</div>', '')\
                     .replace('<div class="quote__body">', '')\
                     .replace('&lt;', '<')\
                     .replace('&gt;', '>').strip()
    link = hlink(quote_number, f'https://xn--80abh7bk0c.xn--p1ai{quote_link}')  # формируем ссылку для телеграмм
    print(quote_date, link, quote_number, quote_text)

find_quote()
