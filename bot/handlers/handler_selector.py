from db import Manager
from handlers.core import start_handler, auth_handler
from handlers.files_handler import create_file


async def redirect_handler(message):
    user_state = await Manager.get_user_state(message.from_user.id)
    if user_state is None:
        return await start_handler(message)
    if user_state == 'wait_token':
        return await auth_handler(message)
    elif user_state.startswith('create_file:'):
        return await create_file(message)

