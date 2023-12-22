import traceback

import aiohttp

import config


class AsyncAPIClient:
    def __init__(self, access_token=None):
        self.api_key = access_token
        self.base_url = config.API_HOST

    def _build_headers(self):
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    async def _make_request(self, method, endpoint, params=None, data=None):
        url = f'{self.base_url}{endpoint}'
        headers = self._build_headers()

        async with aiohttp.ClientSession() as ses:
            async with ses.request(method, url, headers=headers, params=params, data=data) as response:
                response.raise_for_status()
                return await response.json()

    async def get_auth_url(self):
        endpoint = '/login'
        res = await self._make_request('GET', endpoint)
        return res.get('url')

    async def get_me(self):
        endpoint = '/me'
        return await self._make_request('GET', endpoint)

    async def list_files(self, parent_id='root', next_page_token=''):
        endpoint = '/list'
        params = {
            'parent': parent_id,
            'next_page_token': next_page_token,
            'page_size': 10
        }
        return await self._make_request('GET', endpoint, params=params)

    async def get_file_info(self, file_id):
        endpoint = '/get'
        params = {"file_id": file_id}
        return await self._make_request('GET', endpoint, params=params)

    async def create_file(self, filename, parent_id, file=None):
        endpoint = '/create'
        params = {
            "filename": filename,
            "parent_id": parent_id
        }
        if file:
            form_data = aiohttp.FormData()
            form_data.add_field("file", file, filename="your_filename")
        else:
            form_data = None
        return await self._make_request('POST', endpoint, params=params, data=form_data)
