from pydantic import BaseModel


class FileRead(BaseModel):
    file_name: str
