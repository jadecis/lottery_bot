from aiogram.types import Message, CallbackQuery
from loader import dp, bot, html, db, User
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.dispatcher import FSMContext
from src.keyboards.reply import main_menu
from src.keyboards.inline import lottery_menu, buy_menu, payment_menu, edit_menu
from config import YOOMONEY_TOKEN, YOOMONEY_WALLET, admin_chat
from yoomoney import Quickpay, Client
import uuid

@dp.message_handler(CommandStart(), state="*")
async def start_command(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer("Привет!", parse_mode=html,
                     reply_markup=main_menu)

@dp.message_handler(Text(['🎟 Активные лотереи', '⚙️ Профиль']), state="*")
async def text_handler(msg: Message, state: FSMContext):
    user= db.get_user(msg.chat.id)
    if msg.text == '⚙️ Профиль':
        if user:
             await msg.answer(f"<b>ID:</b> <code>{user[1]}</code>\n"
                              +f"<b>Username:</b> <code>{user[2]}</code>\n"
                              +f"<b>Имя:</b> <code>{user[3]}</code>\n"
                              +f"<b>Фамилия:</b> <code>{user[4]}</code>\n"
                              +f"<b>Отчество:</b> <code>{user[5]}</code>\n"
                              +f"<b>Номер телефона:</b> <code>{user[6]}</code>\n",
                              parse_mode=html,
                              reply_markup=edit_menu)
        else:
            await msg.answer("<b>Для просмотра профиля нужно пройти регистрацию. "
                            +f"Просто отвечай на мои вопросы\n\n"
                            +f"Напиши свое ФИО через пробел</b>\n"
                            +f"<i>Пример: Иванов Иван Иванович</i>",
                            parse_mode=html)
            await User.name.set()
    else:
        if user:
            if db.get_lotteries():
                await msg.answer('Выбирай лотерею:', reply_markup=lottery_menu())
            else:
                await msg.answer('На данный момент нет активных лотерей')
        else:
            await msg.answer("<b>Для просмотра лотереи нужно пройти регистрацию. "
                            +f"Просто отвечай на мои вопросы\n\n"
                            +f"Напиши свое ФИО через пробел</b>\n"
                            +f"<i>Пример: Иванов Иван Иванович</i>",
                            parse_mode=html)
            await User.name.set()

@dp.callback_query_handler(text='edit')
async def edit_handler(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(f"<b>Напиши свое ФИО через пробел</b>\n"
                            +f"<i>Пример: Иванов Иван Иванович</i>",
                            parse_mode=html)
    await User.name.set()

@dp.message_handler(content_types='text', state=User.name)
async def name_hand(msg: Message, state: FSMContext):
    await state.update_data(name= msg.text)
    await msg.answer(f"Напиши номер телефона для связи:")
    await User.number.set()
    
@dp.message_handler(content_types='text', state=User.number)
async def number_hand(msg: Message, state: FSMContext):
    data= await state.get_data()
    full= data.get('name').split()
    if db.get_user(msg.chat.id):
        db.up_user(
            user_id=msg.chat.id,
            username=msg.chat.username,
            name=full[1],
            lastname=full[0],
            patronymic=full[2],
            number=msg.text)
    else:
        db.add_user(
            user_id=msg.chat.id,
            username=msg.chat.username,
            name=full[1],
            lastname=full[0],
            patronymic=full[2],
            number=msg.text)
    await msg.answer('Регистрация закончена.\nЧтобы посмотреть или изменить данные нажимайте на кнопку «⚙️ Профиль»')
    await state.finish()

@dp.callback_query_handler(text_contains='lot_')
async def lot_hadler(call: CallbackQuery, state: FSMContext):
    table_name= call.data.replace('lot_', '')
    info= db.get_lottery(table_name)
    sold=db.count_notSold(table_name)[0]
    if sold != 0:
        await call.message.edit_text(f'<b>Лотерея {info[1]}</b>\n'
                              +f"<b>Количество билетов:</b> <code>{info[3]}</code>\n"
                              +f"<b>Количество не распроданных билетов:</b> <code>{sold}</code>\n"
                              +f"<b>Цена 1 билета:</b> <code>{info[4]} ₽\n</code>", 
                              parse_mode=html, 
                              reply_markup=buy_menu(table_name))
    else:
        await call.message.edit_text(f"<b>Билетов нет в наличии!</b>", parse_mode=html)
    
@dp.callback_query_handler(text_contains='buy_')
async def lot_hadler(call: CallbackQuery, state: FSMContext):
    table_name= call.data.replace('buy_', '')
    await state.update_data(table_name=table_name)
    info= db.get_lottery(table_name)
    bill_id= str(call.message.chat.id) + table_name
    bill = Quickpay(
        receiver=YOOMONEY_WALLET,
        quickpay_form='shop',
        targets='Photo bot',
        paymentType='SB',
        sum=info[4],
        label=bill_id)
    await call.message.edit_text(text=f"📍 <b>Счет для оплаты готов</b> 📍\n\n"
                             +f"<i>Для оплаты нажмите кнопку ниже 💳\n\n"
                             +f"<b>❗️ Счет действителен только 1 час</b> ❗️\n"
                             +f"После оплаты нажмите на кнопку «Проверить платеж», для проверки платежа</i>", 
                             reply_markup=payment_menu(url=bill.redirected_url, bill_id=bill_id),
                             parse_mode=html)
    
@dp.callback_query_handler(text_contains='checkbill_')
async def lot_hadler(call: CallbackQuery, state: FSMContext):
    bill_id= call.data.replace('checkbill_', '')
    table_name= bill_id.replace(f'{call.message.chat.id}', '')
    client = Client(YOOMONEY_TOKEN)
    try:
        history = client.operation_history(label=bill_id)
        result= history.operations[-1]
        result=result.status
        if result== 'PAID' or result == 'success' or result == 'paid':
            ticket_id= db.get_ticket(table_name)[0]
            user= db.get_user(call.message.chat.id)
            db.up_ticket(
                table_name=table_name,
                user_id= int(user[1]),
                username=user[2],
                name=user[3],
                lastname=user[4],
                patronymic=user[5],
                number=user[6],
                id=ticket_id
            )
            await call.message.edit_text(f"""
<b>✅ Вы успешно преобрели билет на лотерею <i>{db.get_lottery(table_name)[1]}</i>
🔢 Номер вашего билета:</b> №<code>{ticket_id}</code>

Спасибо за покупку!""", parse_mode=html)
            if not(db.get_ticket(table_name)):
                await bot.send_message(chat_id=admin_chat, text=f'Билеты из лотереи {db.get_lottery(table_name)[1]} раскуплены!')
    except Exception as ex:
        print(ex)
        await bot.answer_callback_query(call.id, "❌ Оплата не прошла!\nПовторите попытку!", show_alert=True)
        