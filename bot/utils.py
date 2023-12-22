import hashlib
from io import BytesIO

import aiohttp
from sqlalchemy import select

from db import async_session, PageToken


def compress_string(data):
    sha256_hash = hashlib.sha256(data.encode()).hexdigest()
    return sha256_hash[:15]


async def create_page_token(next_page_token, prev_page_short_token=None):
    short_token = compress_string(next_page_token)
    prev_page = None
    async with async_session() as ses:
        if prev_page_short_token:
            stmt = select(PageToken).filter(PageToken.short_token == prev_page_short_token)
            result = await ses.execute(stmt)
            prev_page = result.scalars().first()
        page_token_obj = PageToken(next_page_token=next_page_token, short_token=short_token, prev_page=prev_page)
        ses.add(page_token_obj)
        await ses.commit()
    return page_token_obj


async def download_file(file_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            response.raise_for_status()
            return BytesIO(await response.read())


def format_file_info(file_info):
    filename = file_info.get('name', 'N/A')
    size = file_info.get('size', 'N/A')
    mimeType = file_info.get('mimeType', 'N/A')
    createdTime = file_info.get('createdTime', 'N/A')
    modifiedTime = file_info.get('modifiedTime', 'N/A')

    result = f"name: {filename}\nsize: {size}\nmimeType: {mimeType}\ncreatedTime: {createdTime}\nmodifiedTime: {modifiedTime}"
    return result