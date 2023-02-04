from aiogram.types import Message, CallbackQuery
from loader import dp, bot, html, Data, Admin, db
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.dispatcher import FSMContext
from src.keyboards.reply import admin_menu, main_menu
from src.keyboards.inline import lottery_menu
from itertools import product
import os
import csv

@dp.message_handler(CommandStart(), state="*")
async def start_command(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer("Привет!", parse_mode=html,
                     reply_markup=main_menu)

@dp.message_handler(commands=['admin'], state="*")
async def admin_command(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer("Выбери дальниейшие действия:", reply_markup=admin_menu)
    
@dp.message_handler(Text(['Создать лотерею', 'Удалить лотерею', 'Выгрузить таблицу c билетами']), state="*")
async def create_hadler(msg: Message, state: FSMContext):
    if msg.text == 'Создать лотерею':
        await msg.answer('Введи название лотереи (что будут видеть пользователи):')
        await Data.name.set()
    elif msg.text == 'Удалить лотерею':
        await msg.answer('Выбери какую лотерею ты хочешь удалить:', reply_markup=lottery_menu())
        await Admin.delete.set()
    else:
        await msg.answer('Выбери лотерею c которой ты хочешь выгрузить билеты:', reply_markup=lottery_menu())
        await Admin.upload.set()

@dp.callback_query_handler(text_contains='lot_', state=Admin.upload)
async def lot_hadler(call: CallbackQuery, state: FSMContext):
    table_name= call.data.replace('lot_', '')
    with open(f'src/tables/{table_name}.csv', 'w', newline="") as file:
        writer= csv.writer(file)
        writer.writerow(
            ('id', 'user_id', 'username', 'name', 'lastname', 'patronymic', 'number')
        )
        writer.writerows(
            db.get_tickets(table_name)
        )
    await call.message.answer_document(document= open(f'src/tables/{table_name}.csv', 'rb'), caption='Вот таблица с билетами')
    os.remove(f'src/tables/{table_name}.csv')
    await state.finish()
    
@dp.callback_query_handler(text_contains='lot_', state=Admin.delete)
async def lot_hadler(call: CallbackQuery, state: FSMContext):
    table_name= call.data.replace('lot_', '')
    db.del_lottery(table_name)
    await call.message.edit_text("Лотерея успешна удалена!")
    await state.finish()

   
@dp.message_handler(content_types=['text'], state=Data.name)
async def name_handler(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer('Введи название лотереи на английском языке без инных знаков')
    await Data.name_tabl.set()
    
@dp.message_handler(content_types=['text'], state=Data.name_tabl)
async def name_handler(msg: Message, state: FSMContext):
    await state.update_data(name_tabl=msg.text)
    await msg.answer('Введи количество билетов')
    await Data.tickets.set()
    
    
@dp.message_handler(content_types=['text'], state=Data.tickets)
async def name_handler(msg: Message, state: FSMContext):
    await state.update_data(tickets=msg.text)
    await msg.answer('Введи цену 1 билета (в рублях)')
    await Data.price.set()
    
@dp.message_handler(content_types=['text'], state=Data.price)
async def name_handler(msg: Message, state: FSMContext):
    data= await state.get_data()
    try:
        db.add_lottery(
            name= data.get('name'),
            table_name=str(data.get('name_tabl')),
            count= int(data.get('tickets')),
            price= int(msg.text)
        )
    except:
        await msg.answer(f"Такая лотеря уже существует! Пройди регистрацию еще раз!\n\n"
                         +"Введи название лотереи (что будут видеть пользователи):")
        await Data.name.set()
    db.create_table(data.get('name_tabl'))
    msg_id= await msg.answer("Создание таблицы...")
    for i in range(0, int(data.get('tickets'))):
        db.add_ids(table_name=data.get('name_tabl'))
        
    await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg_id.message_id,
                    text= f"<b>Лотерея {data.get('name')}</b>\n"
                     +f"<b>Количество билетов:</b> <code>{data.get('tickets')}</code>\n"
                     +f"<b>Цена одного билета:</b>. <code>{msg.text}</code>\n\n"
                     +f"<b>Успешно создано!</b>",
                     parse_mode=html)
    await state.finish()