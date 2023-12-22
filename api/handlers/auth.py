import httpx
from fastapi import APIRouter, Request
from google.oauth2.credentials import Credentials

from db.models import GoogleCreds, User
from helpers.google_auth_flow import flow
from helpers.tokenizator import create_token
from schemas.auth import AuthURL, Token

auth_router = APIRouter(tags=['auth'])


@auth_router.get('/login')
def login_via_google() -> AuthURL:
    auth_url, _ = flow.authorization_url(access_type='offline')
    return AuthURL(url=auth_url)


async def save_creds(credentials: Credentials, instance: GoogleCreds = None) -> GoogleCreds:
    creds_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "expiry": credentials.expiry,
    }
    if instance:
        await instance.update(**creds_data)
    else:
        instance = await GoogleCreds.objects.create(**creds_data)
    return instance


@auth_router.get('/auth')
async def auth_via_google(request: Request) -> Token:
    code = request.query_params.get('code')
    flow.fetch_token(code=code)
    credentials = flow.credentials
    access_token = credentials.token
    user_info_resp = httpx.get("https://www.googleapis.com/userinfo/v2/me",
                               headers={"Authorization": f"Bearer {access_token}"})
    user_info = user_info_resp.json()
    user, created = await User.objects.get_or_create(email=user_info.get('email'))
    gcreds = await save_creds(credentials, user.google_creds)
    await user.update(google_creds=gcreds)
    token = create_token(user.id)
    return Token(**token)
