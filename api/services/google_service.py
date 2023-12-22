from typing import Optional

from fastapi import Depends, UploadFile, HTTPException
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from starlette import status

from db.models import User
from schemas.drive_schemas import ListFileParams
from services.google_creds import GoogleCredentialsHelper


class GoogleDriveOperations:
    def __init__(self, user: User):
        self.user = user
        self.ghelper = GoogleCredentialsHelper(user.google_creds)
        self.credentials = self.ghelper.generate_credentials_object()
        self.service = build('drive', 'v3', credentials=self.credentials)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.ghelper.save_credentials(self.credentials)

    def get_files(self, params: ListFileParams = Depends()):
        query = f"'{params.parent}' in parents and trashed = false"
        try:
            results = self.service.files().list(
                q=query,
                pageSize=params.page_size,
                pageToken=params.next_page_token,
                fields="nextPageToken, files(id, name, mimeType, parents)"
            ).execute()
            return results
        except HttpError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_details)

    def get_file(self, file_id: str):
        try:
            result = self.service.files().get(
                fileId=file_id,
                fields="id, kind, name, mimeType, description, starred, trashed, createdTime, modifiedTime, version, fileExtension, exportLinks, parents, iconLink, webViewLink, webContentLink, size"
            ).execute()
        except HttpError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_details)
        return result

    def create_file(self, parent_id: Optional[str] = None, filename: Optional[str] = None,
                    file: Optional[UploadFile] = None):
        try:
            file_metadata = {'name': filename or 'Empty File'}
            if parent_id:
                file_metadata.update({'parents': [parent_id]})

            if file:
                media = MediaIoBaseUpload(file.file, mimetype=file.content_type, chunksize=1024 * 1024, resumable=True)
                request = self.service.files().create(body=file_metadata, media_body=media, fields='id')
                response = None
                while response is None:
                    _status, response = request.next_chunk()
                uploaded_file = response
            else:
                request = self.service.files().create(body=file_metadata, media_body='')
                uploaded_file = request.execute()

            return uploaded_file
        except HttpError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_details)

    def move_file(self, file_id: str, new_parent_folder_id: str):
        try:
            file = self.service.files().get(fileId=file_id, fields="parents").execute()
            previous_parents = ",".join(file.get("parents"))

            updated_file = self.service.files().update(fileId=file_id, fields='id,parents',
                                                       addParents=new_parent_folder_id,
                                                       removeParents=previous_parents).execute()
            return updated_file
        except HttpError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.error_details)
