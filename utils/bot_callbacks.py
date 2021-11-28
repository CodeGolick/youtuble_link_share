# - *- coding: utf- 8 - *-
import config
from database import db
from utils.decorators import catcherError
from utils.bot_functions import get_user_step

from datetime import datetime
from time import sleep
from telebot import types,util
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@catcherError
def get_bot_callbacks(bot):

    @catcherError
    @bot.callback_query_handler(func=lambda call: True)
    def command(call):
        cid = call.from_user.id
        username = call.from_user.username
        params = call.data.split('-')
        print(str(cid) +': '+str(params))

        config.userStep[cid] = get_user_step(bot, cid)
        if config.knownUsers[cid] == 'BAN':
            return

        if params[0] == 'menu':
            config.userStep[cid] = 'START'
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('🔹 Новая заявка на накрутку', callback_data=f"share-new_link"))
            markup.row(InlineKeyboardButton('🔖 О боте', callback_data=f"about"))
            bot.edit_message_text(f'🖐🏻 Добро пожаловать, {username}!', chat_id=cid, message_id=call.message.id,reply_markup=markup)

        elif params[0] == 'about':
            config.userStep[cid] = 'ABOUT'
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('◀️Назад', callback_data=f"menu"))
            bot.edit_message_text(f'''🔖О боте

Приветсвтую! Это бот для накрутки!

Лимит в день - 3 видео
Накручиваем только если есть 5 логов за неделю
''', chat_id=cid, message_id=call.message.id,reply_markup=markup)

        elif params[0] == 'share':

            if params[1] == 'new_link':

                user_data = db.get_user(cid)
                print(user_data)
                config.userStep[cid] = 'NEW_LINK_MENU'
                tryies = user_data['link_send']
                last_time = user_data['last_upd']
                # print(config.max_per_day)
                if tryies >= config.max_per_day:
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f"menu"))
                    bot.edit_message_text("❌ Вы израсходовали свой лимит", chat_id=cid, message_id=call.message.id,reply_markup=markup)

                    diffs = datetime.now() - datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
                    diffs_in_days = round( diffs.total_seconds()/(60*60*24) )
                    if diffs_in_days >= 1:
                        db.update_user_data(cid,'link_send',0)
                        markup = types.InlineKeyboardMarkup()
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f"menu"))
                        bot.edit_message_text("🚀 Введите URL на ютуб видео для накрутки", chat_id=cid, message_id=call.message.id,reply_markup=markup)
                        config.data_transfer_dict[cid] = {'mid':call.message.id}
                        config.userStep[cid] = 'NEW_URL'
                
                else:
                    if last_time == None:
                        db.set_link_delay(cid)
                    else:
                        diffs = datetime.now() - datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')
                        diffs_in_days = round( diffs.total_seconds()/(60*60*24) )
                        if diffs_in_days >= 1:
                            db.update_user_data(cid,'link_send',0)
                            db.set_link_delay(cid)

                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f"menu"))
                    bot.edit_message_text("🚀 Введите URL на ютуб видео для накрутки", chat_id=cid, message_id=call.message.id,reply_markup=markup)
                    config.data_transfer_dict[cid] = {'mid':call.message.id}
                    config.userStep[cid] = 'NEW_URL'

            elif params[1] == 'ok':
                user_id = params[2]
                markup = types.InlineKeyboardMarkup()
                bot.send_message(user_id, '✅ Накрутака запущена', parse_mode = 'HTML',reply_markup=markup)
                bot.edit_message_text(call.message.text + '\n\n✅ Накрутака запущена', chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)


            elif params[1] == 'decline':
                user_id = params[2]
                markup = types.InlineKeyboardMarkup()
                bot.send_message(user_id, '❌ Накрутака отклонена', parse_mode = 'HTML',reply_markup=markup)
                bot.edit_message_text(call.message.text + '\n\n❌ Накрутака отклонена', chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)


        elif params[0] == 'new_user':
            if params[1] == 'new_connect':
                if username == None or username == '':
                    bot.edit_message_text("❌ Никнейм не установлен", chat_id=cid, message_id=call.message.id,reply_markup=None)
                    return

                bot.edit_message_text("✅ Заявка отправлена", chat_id=cid, message_id=call.message.id,reply_markup=None)
                for each in config.adminList:

                    msg = f"💠 Новый юзер:\n"\
                            "➖➖➖➖➖➖➖\n"\
                            f"🧑🏻‍💻 @{username} [{str(cid)}]\n"\
                            "➖➖➖➖➖➖➖"
                    try:
                        markup = types.InlineKeyboardMarkup()
                        markup.row(
                            InlineKeyboardButton('✅ Принять', callback_data=f"new_user-accept-{str(cid)}-{username}"), 
                            InlineKeyboardButton('❌ Отказать', callback_data=f"new_user-decline-{str(cid)}-{username}")
                        )
                        bot.send_message(each, msg,parse_mode = 'HTML', reply_markup = markup) 
                    except Exception as e:
                        pass
            elif params[1] == 'accept':
                user_id = params[2]
                user_username = params[3]

                db.update_user_data(user_id,'status','ACTIVE')
                config.knownUsers[cid] = 'ACTIVE'
                config.userStep[cid] = 'START'

                markup = types.InlineKeyboardMarkup()
                markup.row(InlineKeyboardButton('🔹 Новая заявка на накрутку', callback_data=f"share-new_link"))
                markup.row(InlineKeyboardButton('🔖 О боте', callback_data=f"about"))
                bot.send_message(user_id, f'🖐🏻 Добро пожаловать, {user_username}!',parse_mode = 'HTML', reply_markup = markup)

                bot.edit_message_text(call.message.text + '\n\n✅ Принят', chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)
            elif params[1] == 'decline':
                user_id = params[2]
                user_username = params[3]
                bot.send_message(user_id, f'❌ Заявка отклонена',parse_mode = 'HTML', reply_markup = types.ReplyKeyboardRemove())
                bot.edit_message_text(call.message.text + '\n\n❌ Заявка отклонена', chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)


