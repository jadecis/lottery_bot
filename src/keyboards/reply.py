from aiogram.types import ReplyKeyboardMarkup

main_menu= ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

main_menu.add(
    '🎟 Активные лотереи',
    '⚙️ Профиль'
)

admin_menu= ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

admin_menu.add(
    'Создать лотерею',
    'Удалить лотерею',
    'Выгрузить таблицу c билетами'
)