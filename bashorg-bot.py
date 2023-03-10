""""
Телеграм-бот, пока умеет только присылать рандомную цитату с сайта bashorg.org и отвечать на вопрос "Кто я?"
Для запуска потребуются некоторые библиотеки:
    pyTelegrambotApi
    beautifulsoup4
    lxml
"""

import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup


bot = telebot.TeleBot('5478114841:AAFTQV9LPqHoVcMq7B6cTKa6WPCsQwuq00A')
url = "http://bashorg.org/casual"

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
    print('Запрос от {0.first_name}'.format(message.from_user)) #########
    response = requests.get(url)  # получаем страницу от сервера
    soup = BeautifulSoup(response.text, 'lxml')  # создаем объект html страницы
    dirty_date = soup.find('div', class_='vote').text.strip().split()  # сырая строка с датой

    if len(dirty_date) == 8:
        if_date = dirty_date[3:-2]  # иногда попадается слово 'цитата', условие для корректного отобраэжения даты
    else: if_date = dirty_date[4:-2]

    date = ' '.join(if_date)  # готовая строка с датой
    quote = soup.find('div', class_='q').find('div', class_=None).text  # получаем чистую цитату из безямянного div
    answer = date +'\n'+ quote
    
##    response = requests.get(url)  # получаем страницу от сервера
##    soup = BeautifulSoup(response.text, 'lxml')  # создаем объект html страницы
##    quote = soup.find('div', class_='q')  # получаем сырой div 
##    quote_list = quote.text.split(' ')[3:]  # разбиваем на список и отрезаем лишнее
##    result = ' '.join(quote_list).rstrip()  # соединяем воедино и обрезаем лишние пробелы в конце
    
    bot.reply_to(message, answer) 
    print('Ответ:\n' + answer) #######

@bot.message_handler(content_types=['text'])
def dialog(message):
    if(message.text == "Кто ты?"):
        bot.send_message(message.chat.id, text="Рад что ты спросил... Я БОТ! Я вывожу случайную \
цитату с сайта Bashorg.org. Пока я умею только это, но мой создатель работает \
над улучшением и расширением моих способостей 😎")
    else: bot.send_message(message.chat.id, text="Ничего не понял...")

bot.infinity_polling()
