# - *- coding: utf- 8 - *-
import config
from database import db
from utils.decorators import catcherError

from telebot import types,util
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@catcherError
def get_bot_input_cmd(bot):

    @catcherError
    @bot.message_handler(commands=['start'])
    def command(m):
        cid = m.chat.id
        username = m.chat.username
        print(config.adminList)
        if cid in config.adminList:
            config.knownUsers[cid] = 'ACTIVE'
            config.userStep[cid] = 'START'
            return

        if cid not in config.knownUsers:
            user_data = db.get_user(cid)

            if user_data == None:
                db.add_new_user(cid, username)
                if username == '' or username == None:
                    username = f'#user_{str(cid)}'
                else:
                    username = f'@{username}'
                markup = types.InlineKeyboardMarkup()
                markup.row(InlineKeyboardButton('🔐 Запросить доступ', callback_data=f"new_user-new_connect"))
                bot.send_message(cid, f'🖐🏻 Добро пожаловать, {username}!',parse_mode = 'HTML', reply_markup = markup)
                config.knownUsers[cid] = 'PENDING'

            else:
                if user_data['status'] == 'BAN':
                    return
                else:
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('🔹 Новая заявка на накрутку', callback_data=f"share-new_link"))
                    markup.row(InlineKeyboardButton('🔖 О боте', callback_data=f"about"))
                    bot.send_message(cid, f'Добро пожаловать, {username}!',parse_mode = 'HTML', reply_markup = markup)
                    config.knownUsers[cid] = user_data['status']

        else:
            if config.knownUsers[cid] == 'BAN':
                return
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('🔹 Новая заявка на накрутку', callback_data=f"share-new_link"))
            markup.row(InlineKeyboardButton('🔖 О боте', callback_data=f"about"))
            bot.send_message(cid, f'Добро пожаловать, {username}!',parse_mode = 'HTML', reply_markup = markup)

        config.userStep[cid] = 'START'


    @catcherError
    @bot.message_handler(commands=['add'])
    def command_reg(m):
        cid = m.chat.id
        text = m.text
        if cid not in config.adminList:
            return

        try:
            user_id = int(text.split(' ')[1])
            username = bot.get_chat(user_id).username
            if username == '' or username == None:
                username = '@nousername'
        except:
            bot.send_message(cid, 'Не правильная форма записи /add chat_id')
            return

        db.add_new_user(user_id, username)
        db.update_user_data(user_id,'status','ACTIVE')
        bot.send_message(user_id, '✅ Доступ открыт.\n\n👉🏼 Для продолжения  /start')
        bot.send_message(cid, f'✅ Доступ для {username} открыт.')

    @catcherError
    @bot.message_handler(commands=['ban'])
    def command_reg(m):
        cid = m.chat.id
        text = m.text
        if cid not in config.adminList:
            return

        try:
            user_id = int(text.split(' ')[1])
        except:
            bot.send_message(cid, 'Не правильная форма записи /ban chat_id')
            return

        # db.add_new_user(user_id, username)
        db.update_user_data(user_id,'status','BAN')
        bot.send_message(user_id, '❌ Доступ закрыт')
        bot.send_message(cid, f'❌ Доступ для {user_id} закрыт.')
        try:
            del config.knownUsers[int(cid)]
            del config.userStep[int(cid)]
        except Exception as e: 
            pass

@catcherError
def restart(bot, cid):
    if cid in config.adminList:
        config.knownUsers[cid] = 'ACTIVE'
        config.userStep[cid] = 'START'
        return

    if cid not in config.knownUsers:
        user_data = db.get_user(cid)
        if user_data == None:
            config.knownUsers[cid] = 'PENDING'
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('Запросить доступ', callback_data=f"new_user-new_connect"))
            bot.send_message(cid, '🖐🏻 Добро пожаловать!', parse_mode = 'HTML',reply_markup=markup)
        else:
            config.knownUsers[cid] = user_data['status']
            if config.knownUsers[cid] == 'BAN':
                del config.knownUsers[int(cid)]
                del config.userStep[int(cid)]
    config.userStep[cid] = 'START'
