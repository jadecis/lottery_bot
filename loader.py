from aiogram import Bot, Dispatcher, types
from config  import TOKEN_BOT
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from src.database.db import Database
from aiogram.dispatcher.filters.state import StatesGroup, State
import logging


bot = Bot(token=TOKEN_BOT)
logging.basicConfig(level=logging.INFO)
dp= Dispatcher(bot, storage=MemoryStorage())
html= types.ParseMode.HTML #<- &lt; >- &gt; &- &amp;
db= Database('src/database/database.db')

class Data(StatesGroup):
    name= State()
    name_tabl= State()
    tickets= State()
    price= State()
    
class Admin(StatesGroup):
    delete= State()
    upload= State()
    
class User(StatesGroup):
    name= State()
    number= State()