from typing import Optional

from pydantic import BaseModel


class FileMetadata(BaseModel):
    conversation_id: str
    title: str
    snippet: str
    processed_time: float
    file_name: str
    project: Optional[str] = None
