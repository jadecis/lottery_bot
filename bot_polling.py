from loader import dp
from aiogram import executor
from aiogram.types import BotCommand
from src.handlers import admin, user



async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "restart bot")
    ])


executor.start_polling(dp, skip_updates=False, on_startup=set_default_commands)