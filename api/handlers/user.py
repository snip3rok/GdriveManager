from fastapi import APIRouter, Depends

from db.models import User
from helpers.security import get_current_user
from schemas.user import UserInfo

user_router = APIRouter(tags=['user'])


@user_router.get('/me')
def get_my_data(user: User = Depends(get_current_user)) -> UserInfo:
    return UserInfo(id=user.id, email=user.email)
