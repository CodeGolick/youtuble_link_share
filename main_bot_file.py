# - *- coding: utf- 8 - *-
import loader
import telebot

from utils.bot_cmds import get_bot_input_cmd
from utils.bot_text import get_bot_input_text
from utils.bot_callbacks import get_bot_callbacks
from utils.bot_functions import *

from config import BOT_TOKEN, adminList

if __name__ == '__main__':

    bot = telebot.TeleBot(BOT_TOKEN)    
    bot.set_update_listener(listener)

    get_bot_input_cmd(bot)
    get_bot_input_text(bot)
    get_bot_callbacks(bot)

    bot.infinity_polling()