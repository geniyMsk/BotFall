import sqlite3, time, re
from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType, Message, ReplyKeyboardRemove, ParseMode
from aiogram.utils.markdown import text, bold, italic, code, underline, strikethrough
from aiogram.utils.emoji import emojize
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters import Command

import schedule
import time


from loader import bot, dp,  ADMINS, scheduler, chat



from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.helper import Helper, HelperMode, ListItem

from random import randint

import requests
import json
class PLAN (StatesGroup):
    plan = State()

class FINE (StatesGroup):
    fine = State()


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message):
    print(message.chat)
    with sqlite3.connect('server.db') as db:
        cursor = db.cursor()
        query = """CREATE TABLE IF NOT EXISTS users(fullname TEXT, username TEXT, fine INTEGER, plan INTEGER, chatid INTEGER UNIQUE, id INTEGER)"""
        cursor.execute(query)

@dp.message_handler(commands=['help'], state='*')
async def help(message: types.Message):
    text = f"Команды для сотрудников:\n" \
           f"/addme - Добавление пользователя в бд\n" \
           f"/plan - Сдал отчёт\n\n" \
           f"Команды для админов:\n" \
           f"/all - Cписок сотрудников и их штрафы\n" \
           f"/id ID - Поменять штраф в бд\n" \
           f"/check - Проверить сдачу отчёта\n" \
           f"/delplan - Обнулить все сдачи отчётов"
    await message.answer(text)

@dp.message_handler(commands=['addme'], state='*')
async def addme(message: types.Message):
    with sqlite3.connect('server.db') as db:
        cursor = db.cursor()
        fullname = message.from_user.full_name
        username = message.from_user.username
        chatid = message.from_user.id

        cursor.execute(f"SELECT count(*) FROM users WHERE chatid = {chatid}")
        data = cursor.fetchone()[0]
        if data == 0:
            cursor.execute(f"""INSERT INTO users (fullname, username, plan, fine, chatid)
            VALUES
            ('{fullname}', '{username}', 0, 0, {chatid})""")
            await message.answer(f"В базу данных пользователей добавлен:\n{fullname} @{username}(штрафы = 0, id = {chatid}) ")
@dp.message_handler(commands=['plan'], state='*')
async def plan(message: types.Message):
    fullname = message.from_user.full_name
    username = message.from_user.username
    with sqlite3.connect('server.db') as db:
        chatid = message.from_user.id
        cursor = db.cursor()
        cursor.execute(f"""UPDATE users SET plan = 1 WHERE chatid = {chatid}""")

    await message.answer(f"{fullname} @{username}\nНапишите пожалуйста свой отчет и план")
    #await PLAN.plan.set()
#@dp.message_handler(state=PLAN.plan)
#async def plan(message: types.Message):
#    chatid = message.from_user.id
#    with sqlite3.connect('server.db') as db:
 #       cursor = db.cursor()
 #       cursor.execute(f"""UPDATE users SET plan = 1 WHERE chatid = {chatid}""")




for admin in ADMINS:
    @dp.message_handler(user_id=admin, commands=['all'], state='*')
    async def add_fine(message: types.Message):
        #await message.answer("Выберите кому из следующих пользователей вы хотите добавить/убавить штраф (для этого напишите /id и сам ID пользователя)")
        with sqlite3.connect('server.db') as db:
            cursor = db.cursor()
            fullname =cursor.execute("""SELECT fullname FROM users""").fetchall()
            #username =cursor.execute("""SELECT username FROM users""").fetchall()
            #fine =cursor.execute("""SELECT fine FROM users""").fetchall()
            #chatid =cursor.execute("""SELECT chatid FROM users""").fetchall()
            for f in fullname:

                username = cursor.execute(f"""SELECT username FROM users WHERE fullname ='{f[0]}' """).fetchone()[0]
                fine = cursor.execute(f"""SELECT fine FROM users WHERE fullname ='{f[0]}'""").fetchone()[0]
                chatid = cursor.execute(f"""SELECT chatid FROM users WHERE fullname ='{f[0]}'""").fetchone()[0]

                text = f"{f[0]} @{username}\nШтраф: {fine}\nID \= "+code(f"{chatid   }")
                await message.answer(text=text, parse_mode=ParseMode.MARKDOWN_V2)


    @dp.message_handler(user_id=admin, commands=['id'], state='*')
    async def add_fine(message: types.Message):
        id = message.get_args()
        try:
           a =int(id)
        except:
            await message.answer("Вы не указали ID пользователя или указали неправильно\n "
                                 "Например: /id 546476479")
            return
        with sqlite3.connect('server.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""UPDATE users SET id = {id} WHERE chatid={admin}""")
        await message.answer("Напишите новый штраф")

        await FINE.fine.set()
    @dp.message_handler(user_id = admin, state=FINE.fine)
    async def fine(message: types.Message):
        fine =message.text
        try:
           a =int(fine)
        except:
            await message.answer("Вы неправильно указали штраф")
            return
        with sqlite3.connect('server.db') as db:
            cursor = db.cursor()
            id = cursor.execute(f"""SELECT id FROM users WHERE chatid={admin}""").fetchone()[0]
            cursor.execute(f"""UPDATE users SET fine ={fine} WHERE chatid = {id}""")

            fullname = cursor.execute(f"""SELECT fullname FROM users WHERE chatid ='{id}' """).fetchone()[0]
            username = cursor.execute(f"""SELECT username FROM users WHERE chatid ='{id}' """).fetchone()[0]
            fine = cursor.execute(f"""SELECT fine FROM users WHERE chatid ='{id}' """).fetchone()[0]


            text = f"{fullname} @{username}\nШтраф: {fine}\nID \=" + code(f"{id}")
            await message.answer(text=text, parse_mode=ParseMode.MARKDOWN_V2)\



    @dp.message_handler(user_id=admin, state='*', commands=['check'])
    async def fine(message: types.Message):
        with sqlite3.connect('server.db') as db:
            cursor = db.cursor()
            await message.answer("Список не сдавших отчёты")

            for i in cursor.execute("""SELECT chatid FROM users WHERE plan = 0""").fetchall():
                chatid = i[0]
                fullname = cursor.execute(f"""SELECT fullname FROM users WHERE chatid={chatid}""").fetchone()[0]
                username = cursor.execute(f"""SELECT username FROM users WHERE chatid={chatid}""").fetchone()[0]


                await message.answer(text=f"{fullname} @{username}\n"
                                     f"ID \= "+code(f"{chatid}"), parse_mode=ParseMode.MARKDOWN_V2)
    @dp.message_handler(user_id=admin, state='*', commands=['delplan'])
    async def delete(message:types.Message):
        with sqlite3.connect('server.db') as db:
            cursor = db.cursor()
            cursor.execute(f"""UPDATE users SET plan = 0""")





async def send_message_to_admin():
    with sqlite3.connect('server.db') as db:
        cursor = db.cursor()
        await bot.send_message(chat_id=chat,text="Список не сдавших отчёты")

        for i in cursor.execute("""SELECT chatid FROM users WHERE plan = 0""").fetchall():
            chatid = i[0]
            fullname = cursor.execute(f"""SELECT fullname FROM users WHERE chatid={chatid}""").fetchone()[0]
            username = cursor.execute(f"""SELECT username FROM users WHERE chatid={chatid}""").fetchone()[0]
            fine = cursor.execute(f"""SELECT fine FROM users WHERE chatid={chatid}""").fetchone()[0]
            cursor.execute(f"""UPDATE users SET fine = {fine + 1000} WHERE chatid={chatid}""")
            fine = cursor.execute(f"""SELECT fine FROM users WHERE chatid={chatid}""").fetchone()[0]
            text = f"{fullname} @{username}\nШтраф: {fine}\n ID \= " + code(f"{chatid}")
            await bot.send_message(chat_id=chat,text=text, parse_mode=ParseMode.MARKDOWN_V2)
            cursor.execute(f"""UPDATE users SET plan = 0""")




def schedule_jobs():
    scheduler.add_job(send_message_to_admin, "cron", day_of_week='mon-fri',hour=11)


