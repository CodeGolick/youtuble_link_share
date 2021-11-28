# - *- coding: utf- 8 - *-
import sqlite3
from datetime import datetime
from utils.decorators import catcherError

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@catcherError
def db_con():
    mydb = sqlite3.connect(f'database/database.sqlite')
    mydb.row_factory = dict_factory
    return mydb

@catcherError       
def create_tables():
    mydb = db_con()
    mycursor = mydb.cursor()

    mycursor.execute(""" CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        tg_chatid VARCHAR(255),
                        username VARCHAR(255),
                        last_upd DATETIME,
                        link_send INT DEFAULT 0,
                        status VARCHAR(255) DEFAULT 'PENDING',
                        regdata DATETIME DEFAULT CURRENT_TIMESTAMP) """
    )

@catcherError
def update_username(cid,username):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("UPDATE users SET username = ? WHERE tg_chatid = ?", (username,cid))
    mydb.commit()
    cursor.close()

@catcherError
def get_username(cid):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("SELECT username FROM users WHERE tg_chatid = ?", (cid, ))
    result = cursor.fetchone()['username']
    cursor.close()
    return result

@catcherError
def add_new_user(tg_chatid, username):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("""INSERT INTO users (tg_chatid, username) 
                      VALUES (?,?)""", (tg_chatid, username))
    mydb.commit()
    cursor.close()

@catcherError
def update_user_status(cid,status):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE tg_chatid = ?", (status,cid))
    mydb.commit()
    cursor.close()

@catcherError
def get_user(tg_chatid):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM users WHERE tg_chatid = ? ORDER BY id DESC", (tg_chatid, ))
    result = cursor.fetchone()
    cursor.close()
    return result

@catcherError
def get_all_users():
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM users")
    result = cursor.fetchall()
    cursor.close()
    return result

@catcherError        
def update_user_data(cid,params,data):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute(f"UPDATE users SET {params} = '{data}' WHERE tg_chatid = {cid}")
    mydb.commit()
    cursor.close()

@catcherError
def add_new_bill(tg_chatid, ticket, amount, paylink, payment_type, pay_status):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("""INSERT INTO payments (tg_chatid, ticket, amount, paylink, payment_type, pay_status) 
                      VALUES (?,?,?,?,?,?)""", (tg_chatid, ticket, amount, paylink, payment_type, pay_status))
    mydb.commit()
    cursor.close()
    return cursor.lastrowid

@catcherError
def get_bill(bill_id):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM `payments` WHERE `id` = ?",(bill_id,))
    result = cursor.fetchone()
    cursor.close()
    return result

@catcherError
def update_bill_status(bill_id, new_status,amount):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("UPDATE payments SET pay_status = ?,amount = ? WHERE id = ?",(new_status, amount, bill_id))
    mydb.commit()
    cursor.close()

@catcherError
def update__balance(cid, amount):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("UPDATE users SET balance = balance+? WHERE tg_chatid = ?",(amount,cid))
    mydb.commit()
    cursor.close()

@catcherError
def get_not_paid_checks():
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM payments WHERE pay_status != 'PAIED' and adddata >= DATE_SUB(NOW(),INTERVAL 15 MINUTE)")
    result = cursor.fetchall()
    cursor.close()

    return result

@catcherError
def get_all_checks():
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM payments")
    result = cursor.fetchall()
    cursor.close()

    return result

@catcherError
def get_all_orders():
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM shop")
    result = cursor.fetchall()
    cursor.close()

    return result

@catcherError
def get_row(max_tryies):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("SELECT id,mail,password,session FROM wink_accs WHERE tryies < ? LIMIT 1",(max_tryies,))
    result = cursor.fetchone()
    return result

@catcherError
def update_tryies(cid):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute(f"""UPDATE users SET link_send = link_send + 1 WHERE tg_chatid = ? """, (cid,) )
    mydb.commit()
@catcherError

def set_link_delay(cid):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute(f"""UPDATE users SET last_upd = CURRENT_TIMESTAMP WHERE tg_chatid = ? """, (cid,) )
    mydb.commit()
    


@catcherError
def insert_new_row(mail,password,session):
    mydb = db_con()
    cursor = mydb.cursor()
    cursor.execute("INSERT INTO wink_accs(mail,password,session) VALUES (?,?,?)" , (mail,password,session) )
    mydb.commit()
    