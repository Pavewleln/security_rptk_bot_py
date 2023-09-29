import logging
from aiogram import Bot, Dispatcher, types
from db import Database
import config as cfg

logging.basicConfig(level=logging.INFO)

# Bot configs
bot = Bot(token=cfg.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

db = Database('database.db')
