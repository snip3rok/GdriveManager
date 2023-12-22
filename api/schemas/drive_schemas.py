from typing import Optional, List

from fastapi import UploadFile, File
from pydantic import BaseModel, AnyUrl


class ListFileParams(BaseModel):
    parent: str = 'root'
    page_size: Optional[int] = None
    next_page_token: Optional[str] = None


class GetFileParams(BaseModel):
    file_id: str


class CreateFileParams(BaseModel):
    parent_id: Optional[str] = None
    filename: Optional[str] = None
    file: Optional[UploadFile]


class MoveFileParams(BaseModel):
    file_id: str
    new_parent_folder_id: str


class FileId(BaseModel):
    id: str


class FileInfo(FileId):
    name: str
    parents: List[str]
    mimeType: str


class FileFullInfo(FileInfo):
    kind: str
    starred: bool
    trashed: bool
    version: int
    webContentLink: Optional[AnyUrl]
    webViewLink: AnyUrl
    iconLink: AnyUrl
    createdTime: str
    modifiedTime: str
    fileExtension: Optional[str]
    size: Optional[str]


class FileList(BaseModel):
    nextPageToken: Optional[str]
    files: List[FileInfo]


class FileMove(FileId):
    parents: List[str]



