# - *- coding: utf- 8 - *-
import re
import random
import logging
import requests
from datetime import datetime

import config
from utils.decorators import catcherError
from utils.bot_cmds import restart

@catcherError
def listener(messages):
    for m in messages:
        if m.content_type == 'text':
            print(str(m.from_user.username) + " [" + str(m.chat.id) + "]: " + m.text)
            try:
                print(f'knownUsers:{knownUsers}\nuserStep:{userStep}')
            except Exception as e:
                pass

@catcherError
def log(e):
    print(e)
    logging.exception(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


def randWord(count):
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    number = 1
    length = count
    for pwd in range(number):
            word = ''
            for c in range(length):
                word += random.choice(chars)
    return word

@catcherError
def get_user_step(bot, uid):
    if uid in config.userStep:
        return config.userStep[uid]
    else:
        restart(bot, uid)
