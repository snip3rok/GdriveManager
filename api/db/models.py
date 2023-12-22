import datetime

import ormar
from cryptography.fernet import Fernet

from .core import database, metadata
import config

cipher_suite = Fernet(config.FERNET_SECRET_KEY)


class GoogleCreds(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)
    token: str = ormar.String(max_length=250, encrypt_secret=config.SECRET_KEY,
                              encrypt_backend=ormar.EncryptBackends.FERNET)
    refresh_token: str = ormar.String(max_length=250, encrypt_secret=config.SECRET_KEY,
                                      encrypt_backend=ormar.EncryptBackends.FERNET)
    expiry: datetime.datetime = ormar.DateTime()


class User(ormar.Model):
    class Meta:
        database = database
        metadata = metadata

    id: int = ormar.Integer(primary_key=True)
    email: str = ormar.String(max_length=100, unique=True)
    google_creds: GoogleCreds = ormar.ForeignKey(GoogleCreds, unique=True, nullable=True, skip_reverse=True)
