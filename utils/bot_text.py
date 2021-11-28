# - *- coding: utf- 8 - *-
import config
from utils.decorators import catcherError
from telebot import types,util
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db

@catcherError
def get_bot_input_text(bot):

    @bot.message_handler(func=lambda message: True, content_types=['text'])
    def command(m):
        # cid = m.from_user.id
        cid = m.chat.id
        username = m.from_user.username
        text = m.text
        mode = m.chat.type
        mid = m.message_id         

        if cid in config.userStep:
            step = config.userStep[cid]
        else:
            return

        if mode == 'supergroup' or mode == 'group':
            return
        else:
            if step == 'NEW_URL':
                bot.delete_message(cid,mid)
                url = text
                mid = config.data_transfer_dict[cid]['mid']

                markup = types.InlineKeyboardMarkup()
                markup.row(InlineKeyboardButton('Готово', callback_data=f"menu"))
                bot.edit_message_text("✅ Заявка отправлена", chat_id=cid, message_id=mid, reply_markup=markup)

                msg = f"""
👊🏻 Заявка на накрутку:
➖➖➖➖➖➖➖
🧑🏻‍💻 Пользовательнь
 └ @{username}
🔗 Ссылка
 └ {url}
➖➖➖➖➖➖➖
"""             
                db.update_tryies(cid)
                
                for each in config.adminList:
                    markup = types.InlineKeyboardMarkup()
                    markup.row(
                        InlineKeyboardButton('✅ Сделано', callback_data=f"share-ok-{cid}"), 
                        InlineKeyboardButton('❌ Отказ', callback_data=f"share-decline-{cid}")
                    )
                    bot.send_message(each, msg, parse_mode = 'HTML',reply_markup=markup)

                config.userStep[cid] = 'NEW_URL_OK'




