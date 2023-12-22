from google.oauth2.credentials import Credentials

import config
from db.models import GoogleCreds


class GoogleCredentialsHelper:
    def __init__(self, gcreds: GoogleCreds):
        self._gcreds = gcreds

    def generate_credentials_object(self) -> Credentials:
        credentials = Credentials(
            token=self._gcreds.token,
            refresh_token=self._gcreds.refresh_token,
            token_uri='https://accounts.google.com/o/oauth2/token',
            client_id=config.GOOGLE_CLIENT_ID,
            client_secret=config.GOOGLE_CLIENT_SECRET,
            scopes=config.SCOPES,
            universe_domain='googleapis.com',
            expiry=self._gcreds.expiry
        )
        return credentials

    async def save_credentials(self, credentials: Credentials):
        creds_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expiry": credentials.expiry,
        }
        await self._gcreds.update(**creds_data)
