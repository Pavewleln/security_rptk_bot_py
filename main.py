# -*- coding: utf8 -*-
import logging
import time
import config as cfg
from misc import bot, dp, db
from aiogram import executor, types
from helpers import send_adm, send_reply_and_delete_message, send_reply_to_message_and_delete_message


# start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Че нада? :/")


# bot_info
@dp.message_handler(commands=['bot_info'])
async def welcome_send_info(message: types.Message):
    if str(message.from_user.id) in cfg.ADMIN_IDS:
        await message.answer(f"{message.from_user.full_name}, привет!\n\n"
                             f"Это бот модератор, для использования добавьте бота в ваш чат с разрешениями админа"
                             f" админа, иначе бот не сможет функционировать\n\n"
                             f"Команды для администраторов:\n\n"
                             f" <code>/ban</code> - бан пользователя и удаление его из чата\n"
                             f" <code>/mute _m</code> - запретить "
                             f"пользователю отправлять сообщение в чат в указанное время (минуты)\n"
                             f"<code>/unmute</code> - разрешить отправку сообщений\n\n"
                             f"Команды для 'обычных людишек':\n\n"
                             f" <code>/me</code> - проверка ваших данных(проверяйте это в самом боте)\n"
                             f" <code>/admins</code> - информация об админах этой группы\n"
                             f" <code>/report</code> - оставить жалобу на пользователя\n\n"
                             f"❗Все команды (кроме /me и /admins) нужно отправлять ответом на сообщение \n"
                             " пользователя над которым проводится действие!\n"
                             f"Бота сделал @dedMefedroniy")
    else:
        await send_reply_to_message_and_delete_message(message,
                                                       f"{message.from_user.username}, че самый(ая) умный(ая) тип?\n"
                                                       f"(Нет доступа)", 5)
        await message.delete()


# new_chat_member
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], content_types=["new_chat_members"])
async def new_chat_member(message: types.Message):
    chat_id = message.chat.id
    await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    await bot.send_message(chat_id=chat_id, text=f"[{message.new_chat_members[0].full_name}]"
                                                 f"(tg://user?id={message.new_chat_members[0].id})"
                                                 f", Салам Алейкум", parse_mode=types.ParseMode.MARKDOWN)


# me
@dp.message_handler(commands=['me'], commands_prefix="/")
async def welcome(message: types.Message):
    if message.chat.type == types.ChatType.PRIVATE:
        if message.from_user.username is None:
            await message.reply(f"Имя - {message.from_user.full_name}\nID - {message.from_user.id}\n")
        else:
            # Получение значения mute_time из базы данных
            mute_time = db.mute_info(message.from_user.id)

            # Получение текущего времени
            current_time = time.time()

            # Расчет оставшегося времени в минутах
            remaining_time = (mute_time - current_time) / 60.0
            if remaining_time > 0:
                await message.reply(f"Имя - {message.from_user.full_name}\n"
                                    f"ID - <code>{message.from_user.id}</code>\n"
                                    f"До конца мута - {remaining_time:.1f} минут(ы)\n"
                                    f"Username - @{message.from_user.username}\n")
            else:
                await message.reply(f"Имя - {message.from_user.full_name}\n"
                                    f"ID - <code>{message.from_user.id}</code>\n"
                                    f"Мута нет\n"
                                    f"Username - @{message.from_user.username}\n")

    else:
        await message.delete()


# mute
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=["mute"], commands_prefix="/")
async def mute(message: types.Message):
    if str(message.from_user.id) in cfg.ADMIN_IDS:
        if not message.reply_to_message:
            await send_reply_and_delete_message(message, "Эта команда должна быть ответом на сообщение!", 5)
            return

        if not bool(message.text[6:]):
            await send_reply_and_delete_message(message, "Вы не указали минуты!", 5)
            return
        mute_min = int(message.text[6:])
        db.add_mute(message.reply_to_message.from_user.id, mute_min)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await send_reply_to_message_and_delete_message(message,
                                                       f"Пользователь {message.reply_to_message.from_user.username}\n"
                                                       f" был замучен на {mute_min} минут(ы)",
                                                       5)
    else:
        await send_reply_to_message_and_delete_message(message,
                                                       f"{message.from_user.username}, че самый(ая) умный(ая) тип?\n"
                                                       f"(Нет доступа)", 5)
    await message.delete()


# unmute
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=["unmute"],
                    commands_prefix="/")
async def un_mute_user(message: types.Message):
    if str(message.from_user.id) in cfg.ADMIN_IDS:
        if not message.reply_to_message:
            await send_reply_and_delete_message(message, "Эта команда должна быть ответом на сообщение!", 5)
            return

        db.unmute(message.reply_to_message.from_user.id)
        await send_reply_to_message_and_delete_message(message,
                                                       f"Пользователь {message.reply_to_message.from_user.username},\n"
                                                       f" теперь можешь писать в чат",
                                                       5)
    else:
        await send_reply_to_message_and_delete_message(message,
                                                       f"{message.from_user.username}, че самый(ая) умный(ая) тип?\n"
                                                       f"(Нет доступа)", 5)
    await message.delete()


# ban
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['ban'], commands_prefix='/')
async def ban(message: types.Message):
    if str(message.from_user.id) in cfg.ADMIN_IDS:
        if not message.reply_to_message:
            await send_reply_and_delete_message(message, "Эта команда должна быть ответом на сообщение!", 5)
            return
        replied_user = message.reply_to_message.from_user.id
        admin_id = message.from_user.id
        await bot.send_message(chat_id=message.chat.id, text=f"[{message.reply_to_message.from_user.full_name}]"
                                                             f"(tg://user?id={replied_user})"
                                                             f" был(а) забанен админом [{message.from_user.full_name}]"
                                                             f"(tg://user?id={admin_id})",
                               parse_mode=types.ParseMode.MARKDOWN)
        await bot.kick_chat_member(chat_id=message.chat.id, user_id=replied_user)
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    else:
        await send_reply_to_message_and_delete_message(message,
                                                       f"{message.from_user.username}, че самый(ая) умный(ая) тип?\n"
                                                       f"(Нет доступа)", 5)
    await message.delete()


# admins
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['admins'],
                    commands_prefix='/')
async def get_admin_list(message: types.Message):
    admins = await message.chat.get_administrators()
    msg = str("Админы :\n")

    for admin in admins:
        msg += f"{admin.user.full_name}\n"

    await message.reply(msg, parse_mode=types.ParseMode.MARKDOWN)


# report
@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP], commands=['report'])
async def report_by_user(message: types.Message):
    if str(message.from_user.id) in cfg.ADMIN_IDS:
        await send_reply_and_delete_message(message, "Ты админ, не за чем это делать", 5)
        return
    if not message.reply_to_message:
        await send_reply_and_delete_message(message, "Эта команда должна быть ответом на сообщение!", 5)
        return
    msg_id = message.reply_to_message.message_id
    user_id = message.from_user.id
    admins_list = await message.chat.get_administrators()

    for admin in admins_list:
        try:
            await bot.send_message(text=f"Пользователь: [{message.from_user.full_name}](tg://user?id={user_id})\n"
                                        f"Оставили жалобу на данное сообщение:\n"
                                        f"[Возможное нарушение](t.me/{message.chat.username}/{msg_id})",
                                   chat_id=admin.user.id, parse_mode=types.ParseMode.MARKDOWN,
                                   disable_web_page_preview=True)
        except Exception as e:
            logging.debug(f"\nНе получилось отправить жалобу к {admin.user.id}\nError - {e}")

    await send_reply_to_message_and_delete_message(message, "Жалоба будет рассмотрена админом, спасибо!", 5)


# Фильтр сообщений
@dp.message_handler()
async def mess_handler(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)

    if not db.mute_bool(message.from_user.id):
        text = message.text.lower()
        for word in cfg.BAD_WORDS:
            if word in text:
                await message.delete()
    else:
        await message.delete()


# Polling
if __name__ == '__main__':
    executor.start_polling(dp, on_startup=send_adm, skip_updates=True)
