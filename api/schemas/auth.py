from pydantic import BaseModel, AnyUrl


class AuthURL(BaseModel):
    url: AnyUrl


class Token(BaseModel):
    access_token: str
    token_type: str
