from fastapi import APIRouter, Depends

from db.models import User
from helpers.security import get_current_user
from schemas.drive_schemas import (
    ListFileParams, GetFileParams, CreateFileParams, MoveFileParams, FileFullInfo, FileList, FileId, FileMove
)
from services.google_service import GoogleDriveOperations

drive_router = APIRouter(tags=['drive'])


@drive_router.get('/list')
async def get_files(params: ListFileParams = Depends(), user: User = Depends(get_current_user)) -> FileList:
    async with GoogleDriveOperations(user) as gd_ops:
        result = gd_ops.get_files(params)
        return FileList(**result)


@drive_router.get('/get')
async def get_file(params: GetFileParams = Depends(), user: User = Depends(get_current_user)) -> FileFullInfo:
    async with GoogleDriveOperations(user) as gd_ops:
        result = gd_ops.get_file(params.file_id)
        return FileFullInfo(**result)


@drive_router.post('/create')
async def create_file(params: CreateFileParams = Depends(), user: User = Depends(get_current_user)) -> FileId:
    async with GoogleDriveOperations(user) as gd_ops:
        result = gd_ops.create_file(params.parent_id, params.filename, params.file)
        return FileId(**result)


@drive_router.post("/move-file/")
async def move_file(params: MoveFileParams = Depends(), user: User = Depends(get_current_user)):
    async with GoogleDriveOperations(user) as gd_ops:
        result = gd_ops.move_file(params.file_id, params.new_parent_folder_id)
        return FileMove(**result)
