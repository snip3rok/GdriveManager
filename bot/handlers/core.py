import traceback

from aiohttp import ClientResponseError
from telebot.types import Message

from api import AsyncAPIClient
from bot_instance import bot
from db import async_session, Manager
from exceptions import handle_exception
from handlers.helpers import send_login_message, send_main_menu


async def start_handler(message: Message):
    async with async_session() as ses:
        user = await Manager.get_user(ses, message.from_user.id)
        if user is None:
            user = await Manager.register_user(ses, message.from_user.id, 'wait_token')
        if user.state == 'wait_token':
            await send_login_message(message.from_user.id)
        else:
            user.state = 'lookup'
            await send_main_menu(message)
        await ses.commit()


async def auth_handler(message: Message):
    api_client = AsyncAPIClient(message.text)
    try:
        await api_client.get_me()
    except ClientResponseError as e:
        if e.status == 401:
            await bot.send_message(message.from_user.id, "You enter invalid access_token.\nTry again")
        return
    except Exception as e:
        await handle_exception(message, e)
    async with async_session() as ses:
        user = await Manager.get_user(ses, message.from_user.id)
        user.access_token = message.text
        user.state = 'main'
        await ses.commit()
    await send_main_menu(message)
