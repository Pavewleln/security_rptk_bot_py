import asyncio
from misc import bot

import config as cfg
# Если нужна проверка подписки на канал
def check_sub_channel(chat_member):
    return chat_member['status'] != 'left'


# Уведомление об запуске бота
async def send_adm(*args, **kwargs):
    await bot.send_message(chat_id=cfg.ADMIN_ID_PAVEL, text='Бот запущен')


async def send_reply_to_message_and_delete_message(message, text, delay):
    sent_message = await message.reply_to_message.reply(text)
    await asyncio.sleep(delay)
    await sent_message.delete()


async def send_reply_and_delete_message(message, text, delay):
    sent_message = await message.reply(text)
    await asyncio.sleep(delay)
    await sent_message.delete()
