import re
import telebot
from bs4 import BeautifulSoup
from selenium import webdriver
import auth_data

# page = requests.get("https://www.investing.com/currencies/thb-rub")
# print(page.status_code)
# from auth_data import token


def get_cur(url):
    url = 'https://www.investing.com/currencies/thb-rub'
    driver = webdriver.Chrome(executable_path="chromedriver.exe")

    try:
        driver.get(url=url)
        # time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()

    # soup = BeautifulSoup(data, "html.parser")
    find_currency_rate = soup.findAll('span', class_='text-2xl')
    find_short_name = soup.findAll('h1', class_='text-2xl font-semibold instrument-header_title__gCaMF mobile:mb-2')
    # print(find_currency_rate)
    result_currency = re.search(r'\d{2}.\d{4}|\d.\d{4}|\d{2}.\d{3}|\d.\d{3}', str(find_currency_rate[0]))
    name_result = re.search(r'\w\w\w/\w\w\w\b', str(find_short_name[0]))
    ans = f'Курс по валютной паре {name_result[0]}, составляет: {result_currency[0]}\n Данные с Investing.com'
    return ans


def get_currency_pair(urls):
    zamena = re.sub('/', '-', urls)
    # print(zamena)
    url = f'https://www.investing.com/currencies/{zamena.lower()}'
    print(url)
    return url


if __name__ == "__main__":
    bot = telebot.TeleBot(auth_data.token, parse_mode=None)


    @bot.message_handler(commands=['help', 'Help'])
    def send_help(message):
        bot.reply_to(message, "Сейчас доступны следующие команды: \n"
                              "/Help - список доступных команд, \n"
                              "Если нужно узнать курс валюты, необходимо указать пару через слеш, GBP/USD - пример")


    @bot.message_handler(content_types=["text"])
    def send_text(message):
        print(message.text)
        print(re.search(r'\w\w\w/\w\w\w', message.text))
        if bool(re.search(r'\w\w\w/\w\w\w', message.text)) == True:
            print("****")
            print(message.text[0:7])
            bot.send_message(message.chat.id, get_cur(get_currency_pair(message.text[0:7])))
        else:
            bot.send_message(message.chat.id, 'Hi, что бы узнать список доступных команд набери /Help ')


    bot.infinity_polling()
