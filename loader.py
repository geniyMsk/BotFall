from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN='1779677036:AAEoG6GDC472Qy4wg6tKjPblBl6M9n3VGyE'
ADMINS = [384405346, 546476479]
chat =  -1001345952317

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()

