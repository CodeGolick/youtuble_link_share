

def nevalid(cc_info):
    return f"""<b>ПРОВЕРКА ЗАВЕРШЕНА</b>
➖➖➖➖➖➖➖➖➖
🏦 {cc_info['name']} | {cc_info['bank']}
💳 {cc_info['paymentSystem']} | {cc_info['country']}
➖➖➖➖➖➖➖➖➖
🔹 Статус: ❌ Невалид"""

def valid(cc_info):
    return f"""<b>ПРОВЕРКА ЗАВЕРШЕНА</b>
➖➖➖➖➖➖➖➖➖
🏦 {cc_info['name']} | {cc_info['bank']}
💳 {cc_info['paymentSystem']} | {cc_info['country']}
➖➖➖➖➖➖➖➖➖
🔹 Статус: ✅ Валид"""