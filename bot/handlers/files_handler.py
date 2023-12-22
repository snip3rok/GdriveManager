import traceback

import aiohttp
from sqlalchemy import select

from api import AsyncAPIClient
from bot_instance import bot
from db import async_session, Manager, PageToken
from telebot.types import Message, CallbackQuery

from exceptions import handle_exception
from keyboards import Keyboards
from utils import download_file, format_file_info


async def list_files(call: CallbackQuery):
    try:
        _, folder, short_page_token = call.data.split(':')
        if len(short_page_token):
            async with async_session() as ses:
                stmt = select(PageToken).filter(PageToken.short_token == short_page_token)
                result = await ses.execute(stmt)
                token_record = result.scalars().first()
                next_page_token = token_record.next_page_token
        else:
            next_page_token = ''
        access_token = await Manager.get_user_token(call.from_user.id)
        api_client = AsyncAPIClient(access_token)
        files = await api_client.list_files(next_page_token=next_page_token, parent_id=folder)
        kb = await Keyboards.generate_files_list_kb(files, folder, short_page_token)
        await bot.edit_message_reply_markup(call.from_user.id, call.message.id, reply_markup=kb)
    except Exception as e:
        await handle_exception(call, e)


async def start_file_creation(call: CallbackQuery):
    try:
        _, folder = call.data.split(':')
        async with async_session() as ses:
            user = await Manager.get_user(ses, call.from_user.id)
            user.state = f'create_file:{folder}'
            await ses.commit()
        await bot.edit_message_text('Send me a file or file name to create empty file', call.from_user.id, call.message.id,
                                    reply_markup=Keyboards.cancel_file_creation(folder))
    except Exception as e:
        await handle_exception(call, e)


async def create_file(message: Message):
    try:
        async with async_session() as ses:
            user = await Manager.get_user(ses, message.from_user.id)
            _, parent_id = user.state.split(':')
            api_client = AsyncAPIClient(user.access_token)
            user.state = 'lookup'
            await ses.commit()
        await api_client.create_file(message.text, parent_id)
        await bot.send_message(message.from_user.id, f'File {message.text} was created', reply_markup=Keyboards.back_to_files_kb(parent_id))
    except Exception as e:
        await handle_exception(message, e)


async def upload_file(message: Message):
    try:
        async with async_session() as ses:
            user = await Manager.get_user(ses, message.from_user.id)
            if not user.state.startswith('create_file:'):
                return await bot.send_message(message.from_user.id, 'To upload file press "create file" in your files list menu')
            _, parent_id = user.state.split(':')
            await bot.send_message(message.from_user.id, 'Uploading...')
            file_id = message.document.file_id
            filename = message.document.file_name
            file_url = await bot.get_file_url(file_id)
            file_content = await download_file(file_url)
            api_client = AsyncAPIClient(user.access_token)
            await api_client.create_file(filename, parent_id, file_content)
            await bot.send_message(message.from_user.id, f'File {filename} was uploaded',
                                   reply_markup=Keyboards.back_to_files_kb(parent_id))
    except Exception as e:
        await handle_exception(message, e)


async def get_file_info(call: CallbackQuery):
    try:
        _, file_id = call.data.split(':')
        access_token = await Manager.get_user_token(call.from_user.id)
        api_client = AsyncAPIClient(access_token)
        file_info = await api_client.get_file_info(file_id)
        message_text = format_file_info(file_info)
        kb = Keyboards.file_view_kb(file_info)
        await bot.send_message(call.from_user.id, message_text, reply_markup=kb)
    except Exception as e:
        await handle_exception(call, e)
