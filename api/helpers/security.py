from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from starlette import status

import config
from db.models import User

security = HTTPBearer()


async def get_current_user(token: str = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"Authorization": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        user = await User.objects.select_related("google_creds").get_or_none(id=user_id)
        if user is None or user.google_creds is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
