import re

import telebot
from telebot import types
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import auth_data
import logging

chrome_options = Options()
chrome_options.add_argument('--headless')
prefs = {'profile.managed_default_content_settings.images': 2}
chrome_options.add_experimental_option('prefs', prefs)

def get_cur(url):
    # url = 'https://www.investing.com/currencies/thb-rub'
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)

    try:
        driver.set_script_timeout(5)
        driver.get(url=url)
        # print(driver.page_source)
        soup = BeautifulSoup(driver.page_source, "lxml") #html.parser
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

    find_currency_rate = soup.findAll('span', class_='text-2xl')
    find_short_name = soup.findAll('h1', class_='text-2xl font-semibold instrument-header_title__gCaMF mobile:mb-2')
    # print(find_currency_rate)
    result_currency = re.search(r'\d{2}.\d{4}|\d.\d{4}|\d{2}.\d{3}|\d.\d{3}', str(find_currency_rate[0]))
    name_result = re.search(r'\w\w\w/\w\w\w\b', str(find_short_name[0]))
    ans = f'Курс по валютной паре {name_result[0]}, составляет: {result_currency[0]}\n Данные с Investing.com'
    return ans


def get_currency_pair(urls):
    zamena = re.sub('/', '-', urls)
    url = f'https://www.investing.com/currencies/{zamena.lower()}'
    print(url)
    return url


if __name__ == "__main__":
    logger = telebot.logger
    log_handler = logging.FileHandler('telebot.log')
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    telebot.logger.setLevel(logging.DEBUG)
    bot = telebot.TeleBot(auth_data.token, parse_mode=None)


    @bot.message_handler(func=lambda message: True)
    def log_update(message):
        logger.info(f'Received update: {message}')


    @bot.message_handler(commands=['help', 'Help'])
    def send_help(message):
        bot.reply_to(message, "Сейчас доступны следующие команды: \n"
                              "/Help - список доступных команд, \n"
                              "/start - для вызова клавиатуры с валютными парами \n"
                              "Если нужно узнать курс валюты, необходимо указать пару через слеш, GBP/USD - пример")


    @bot.message_handler(commands=['start'])
    def start(message):
        markup = types.ReplyKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="EUR/USD \u20AC/$")
        button2 = types.InlineKeyboardButton(text="USD/RUB $/\u20BD")
        button3 = types.InlineKeyboardButton(text="EUR/RUB \u20AC/\u20BD")
        button4 = types.InlineKeyboardButton(text="THB/RUB \u0E3F/\u20BD")
        button5 = types.InlineKeyboardButton(text="CNY/RUB \u00A5/\u20BD")
        button6 = types.InlineKeyboardButton(text="GBP/RUB \u00A3/\u20BD")
        markup.add(button1, button2, button3, button4, button5, button6)
        bot.send_message(message.chat.id, 'Основные пары валют, можно написать свою, просто, через слеш тексом',
                         reply_markup=markup)


    @bot.message_handler(content_types=["text"])
    def send_text(message):
        # print(message.text)
        print(re.search(r'\w\w\w/\w\w\w', message.text))
        if bool(re.search(r'\w\w\w/\w\w\w', message.text)) == True:
            print("****")
            print(message.text[0:7])
            bot.send_message(message.chat.id, get_cur(get_currency_pair(message.text[0:7])))
        else:
            bot.send_message(message.chat.id, 'Hi, что бы узнать список доступных команд набери /Help ')


    bot.infinity_polling()
