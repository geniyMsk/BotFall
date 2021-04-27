import logging

from aiogram import Dispatcher

from bot import schedule_jobs
from loader import ADMINS
from aiogram.utils.emoji import emojize


async def on_startup_notify(dp: Dispatcher):

    for admin in ADMINS:
        try:
            await dp.bot.send_message(546476479, text = "Я запущен")

        except Exception as err:
            logging.exception(err)
