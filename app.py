from aiogram import executor

from loader import dp, scheduler
import bot, loging
from admin import on_startup_notify


async def on_startup(dispatcher):
    # Уведомляет про запуск
    bot.schedule_jobs()
    #await on_startup_notify(dispatcher)



if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)
