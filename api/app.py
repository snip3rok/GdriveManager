from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

import config
from db.core import database, metadata, engine
from handlers.auth import auth_router
from handlers.drive import drive_router
from handlers.user import user_router

app = FastAPI()

app.state.database = database
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)

app.include_router(auth_router)
app.include_router(drive_router)
app.include_router(user_router)

metadata.create_all(engine)


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()
