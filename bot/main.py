import asyncio

from bot_instance import bot
from db.core import engine, Base
from handlers.core import start_handler
from handlers.files_handler import list_files, create_file, start_file_creation, upload_file, get_file_info
from handlers.handler_selector import redirect_handler

bot.register_message_handler(start_handler, commands=['start'])
bot.register_message_handler(redirect_handler, content_types=['text'])
bot.register_message_handler(upload_file, content_types=['document'])

bot.register_callback_query_handler(list_files, func=lambda call: call.data.startswith("list_files:"))
bot.register_callback_query_handler(get_file_info, func=lambda call: call.data.startswith("get_file:"))
bot.register_callback_query_handler(start_file_creation, func=lambda call: call.data.startswith("create_file:"))


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await bot.polling()


asyncio.run(main())