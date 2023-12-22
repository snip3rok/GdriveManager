from telebot.types import Message

from api import AsyncAPIClient
from bot_instance import bot
from db import async_session, Manager
from keyboards import Keyboards


async def request_login(chat_id):
    async with async_session() as ses:
        user = await Manager.get_user(ses, chat_id)
        user.state = 'wait_token'
        await ses.commit()
    await send_login_message(chat_id)


async def send_login_message(chat_id):
    api_client = AsyncAPIClient()
    auth_url = await api_client.get_auth_url()
    await bot.send_message(chat_id,
                           f'To continue you should authorize\nAfter authorization send me your acces_token',
                           reply_markup=Keyboards.auth_url_kb(auth_url))


async def send_main_menu(message: Message):
    await bot.send_message(message.from_user.id, 'Wellcome!\nUse menu below to manage your files', reply_markup=Keyboards.main_menu_kb())

