from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from loader import db

def lottery_menu():
    markup= InlineKeyboardMarkup(row_width=1)
    for i in db.get_lotteries():
        sold=i[3] - db.count_notSold(i[2])[0]
        markup.add(
            InlineKeyboardButton(f'{str(i[1])}  {sold} / {i[3]}', callback_data= f'lot_{i[2]}')
        )
    
    return markup

def buy_menu(table_name):
    markup= InlineKeyboardMarkup(row_width=1)
    
    markup.add(
            InlineKeyboardButton(f'💳 Купить билет', callback_data= f'buy_{table_name}')
        )
    
    return markup

def payment_menu(url, bill_id):
    markup= InlineKeyboardMarkup()
    markup.insert(
    InlineKeyboardButton('💳 ОПЛАТИТЬ', url=url)
    )
    markup.add(
    InlineKeyboardButton('✅ Проверить платеж', callback_data='checkbill_'+ str(bill_id))
    )
    return markup

edit_menu= InlineKeyboardMarkup(row_width=1)

edit_menu.add(
    InlineKeyboardButton('✏️ Изменить данные', callback_data='edit')
)