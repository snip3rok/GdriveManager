from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from starlette.responses import JSONResponse

from db.models import User
from helpers import GoogleCredentialsHelper
from helpers.security import get_current_user
from schemas.drive_schemas import ListFile

drive_router = APIRouter(tags=['drive'])


@drive_router.get('/files')
async def get_files(params: ListFile = Depends(), user: User = Depends(get_current_user)):
    ghelper = GoogleCredentialsHelper(user.google_creds)
    credentials = ghelper.generate_credentials_object()
    service = build('drive', 'v3', credentials=credentials)
    query = f"'{params.parent}' in parents and trashed = false"
    results = service.files().list(q=query, pageSize=params.page_size, pageToken=params.next_page_token,
                                   fields="nextPageToken, files(id, name, mimeType, parents)").execute()
    await ghelper.save_credentials(credentials)
    return results


@drive_router.get('/get')
async def get_file(file_id: str, user: User = Depends(get_current_user)):
    ghelper = GoogleCredentialsHelper(user.google_creds)
    credentials = ghelper.generate_credentials_object()
    service = build('drive', 'v3', credentials=credentials)
    result = service.files().get(fileId=file_id,
                                 fields="id, kind, name, description, starred, trashed, createdTime, modifiedTime, version, fullFileExtension, fileExtension, exportLinks, parents, iconLink, owners, webViewLink, webContentLink, size").execute()
    ghelper.save_credentials(credentials)
    return result


@drive_router.post('/create')
async def create_file(parent_id: Optional[str] = None, filename: Optional[str] = None, file: UploadFile = File(...),
                      user: User = Depends(get_current_user)):
    ghelper = GoogleCredentialsHelper(user.google_creds)
    credentials = ghelper.generate_credentials_object()
    service = build('drive', 'v3', credentials=credentials)
    if not filename:
        filename = file.filename
    try:
        file_metadata = {'name': filename}
        if parent_id:
            file_metadata.update({'parents': [parent_id]})

        media = MediaIoBaseUpload(file.file, mimetype=file.content_type, chunksize=1024 * 1024, resumable=True)

        request = service.files().create(body=file_metadata, media_body=media, fields='id')
        response = None
        while response is None:
            _status, response = request.next_chunk()

        uploaded_file = response
        return JSONResponse(content={"message": "File uploaded successfully", "file_id": uploaded_file['id']})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
    finally:
        await ghelper.save_credentials(credentials)


@drive_router.post("/move-file/")
async def move_file(file_id: str, new_parent_folder_id: str, user: User = Depends(get_current_user)):
    ghelper = GoogleCredentialsHelper(user.google_creds)
    credentials = ghelper.generate_credentials_object()
    service = build('drive', 'v3', credentials=credentials)
    try:
        file = service.files().get(fileId=file_id, fields="parents").execute()
        previous_parents = ",".join(file.get("parents"))

        updated_file = service.files().update(fileId=file_id, fields='id,parents', addParents=new_parent_folder_id,
                                              removeParents=previous_parents).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error moving file: {str(e)}")
    finally:
        await ghelper.save_credentials(credentials)
