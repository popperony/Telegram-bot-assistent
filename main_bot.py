import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PROXY_URL = os.getenv('PROXY_URL')
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == "rejected":
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    params = {'from_date': current_timestamp}
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    homework_statuses = requests.get(
        url,
        params=params,
        headers=headers
        ).json()
    return homework_statuses


def send_message(message):
    proxy = telegram.utils.request.Request(proxy_url=PROXY_URL)
    bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
