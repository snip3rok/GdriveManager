import base64

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from db import async_session, PageToken
from utils import create_page_token, compress_string


class Keyboards:
    @staticmethod
    def auth_url_kb(url):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('Login with Google', url=url))
        return kb

    @staticmethod
    def main_menu_kb():
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('My files', callback_data='list_files:root:'))
        return kb

    @staticmethod
    def file_view_kb(file_info):
        preview_link = file_info.get('webViewLink')
        content_link = file_info.get('webContentLink')
        kb = InlineKeyboardMarkup()
        if preview_link:
            kb.add(InlineKeyboardButton('Preview', url=preview_link))
        if content_link:
            kb.add(InlineKeyboardButton('Download', url=content_link))
        return kb

    @staticmethod
    def cancel_file_creation(folder):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('Cancel', callback_data=f'list_files:{folder}:'))
        return kb

    @staticmethod
    def back_to_files_kb(folder):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton('Back to files', callback_data=f'list_files:{folder}:'))
        return kb

    @staticmethod
    def files_list_kb(files: list, folder='root', prev_page=None, next_page=None):
        kb = InlineKeyboardMarkup(row_width=3)
        for file in files:
            if file.get('mimeType') == 'application/vnd.google-apps.folder':
                kb.add(InlineKeyboardButton(
                    text=f"🗂 {file.get('name')}",
                    callback_data=f"list_files:{file.get('id')}:"
                ))
            else:
                kb.add(InlineKeyboardButton(
                    text=file.get('name'),
                    callback_data=f"get_file:{file.get('id')}"
                ))
        navigate_keys = []
        if prev_page is not None:
            navigate_keys.append(InlineKeyboardButton(
                text="⬅️️",
                callback_data=f"list_files:{folder}:{prev_page}"
            ))
        if folder != 'root':
            navigate_keys.append(InlineKeyboardButton(
                text="⬆️️️",
                callback_data=f"list_files:root:"
            ))
        if next_page:
            navigate_keys.append(InlineKeyboardButton(
                text="➡️",
                callback_data=f"list_files:{folder}:{next_page}"
            ))
        if len(navigate_keys):
            kb.add(*navigate_keys)
        kb.add(InlineKeyboardButton('Create a file', callback_data=f'create_file:{folder}'))
        return kb


    @staticmethod
    async def generate_files_list_kb(files_data: dict, folder='root', current_page_token=None):
        async with async_session() as ses:
            next_page_token = files_data.get('nextPageToken')
            current_page = None
            next_page = None
            prev_page_token = None
            page_number = 2
            if current_page_token:
                stmt = select(PageToken).options(selectinload(PageToken.prev_page)).filter(PageToken.short_token == current_page_token)
                result = await ses.execute(stmt)
                current_page = result.scalars().first()
            if current_page:
                page_number = current_page.page_number + 1
                prev_page_token = current_page.prev_page.short_token if current_page.prev_page else None
                if current_page.page_number == 2:
                    prev_page_token = ''
            if next_page_token:
                next_page = compress_string(next_page_token)
                current_page_id = current_page.id if current_page else None
                next_page_obj = PageToken(next_page_token=next_page_token, short_token=next_page, page_number=page_number, prev_page_id=current_page_id)
                ses.add(next_page_obj)
                await ses.commit()
            return Keyboards.files_list_kb(files_data.get('files'), prev_page=prev_page_token, folder=folder, next_page=next_page)
