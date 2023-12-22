from aiohttp import ClientResponseError

from bot_instance import bot
from handlers.helpers import request_login


async def handle_exception(message, exc):
    if isinstance(exc, ClientResponseError):
        if exc.status in [401, 403]:
            await bot.send_message(message.from_user.id, 'Your credentials are invalid')
            await request_login(message.from_user.id)
    else:
        await bot.send_message(message.from_user.id, f"An error occurred: {str(exc)}")
