import logging
import os
import re
import traceback

import requests
from telebot import TeleBot
from telebot.handler_backends import State, StatesGroup
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, BotCommand, ReplyKeyboardRemove

from utils import init_logging

BOT_TOKEN = os.getenv('AUTH_BOT_TOKEN')
bot = TeleBot(BOT_TOKEN)
BACKEND_PORT = os.getenv('BACKEND_PORT')

API_URL = f'http://backend:{BACKEND_PORT}/api'

logger = init_logging()

USER_TOKENS = {}


class PhoneState(StatesGroup):
    phone = State()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(text="Поделиться номером", request_contact=True)
    keyboard.add(button)

    splitted_text = message.text.split(' ')
    if splitted_text == 0:
        bot.send_message(message.chat.id, "Перейдите по ссылке еще раз")
        return
    token = splitted_text[1]
    USER_TOKENS[user_id] = token

    logger.info(f'Пользователь {user_id}')
    bot.send_message(message.chat.id, "Пожалуйста, поделитесь своим номером телефона", reply_markup=keyboard)
    bot.set_state(message.from_user.id, PhoneState.phone, message.chat.id)


@bot.message_handler(content_types=['contact'])
def get_phone(message):
    if message.from_user.id not in USER_TOKENS:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте еще раз')
        return
    data = {
        'tg_username': message.from_user.username,
        'phone': re.sub(r'\+-\(\)', '', message.contact.phone_number),
        'last_name': message.from_user.last_name,
        'first_name': message.from_user.first_name,
        'tg_id': message.from_user.id,
        'token': USER_TOKENS[message.from_user.id],
    }
    response = request_api(url=f'{API_URL}/users/create_bot_user/', data=data)
    if response is None:
        bot.send_message(message.chat.id, 'Сервис временно не доступен')
        return
    bot.send_message(message.chat.id, response['data'], reply_markup=ReplyKeyboardRemove())


def request_api(url, data):
    logger.info('Проверка пользователя в базе')
    attempt = 0
    while attempt < 3:
        try:
            logger.info(f'Отправка запроса в бэк, попытка {attempt}')
            response = requests.post(
                url,
                json=data,
                headers={'Authorization': f'Bot {BOT_TOKEN}'},
                timeout=(3, 3),
            )
            logger.info(response.text)
            if response.status_code != 200:
                raise Exception(response.status_code)
            response = response.json()
            return response
        except Exception as e:
            attempt += 1
            traceback.print_exc(15)
            logger.error(f'Error request api: {e}')


if __name__ == '__main__':
    logger.info('Запуск бота')
    bot.set_my_commands([BotCommand('/start', 'start')])
    bot.infinity_polling(restart_on_change=os.getenv('DEBUG', False), logger_level=logging.INFO)