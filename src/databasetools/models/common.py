from datetime import datetime
from typing import List
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel
from pydantic import Field


class CommonFields(BaseModel):
    """
    Common fields for MongoDB documents.
    """

    name: str = Field(...)
    description: str
    version: int
    tags: List[str] = []
    type: str
    sub_type: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_by: Optional[str] = None
    modified_at: Optional[datetime] = None
    status: Optional[str] = None


class Relationship(BaseModel):
    """
    Represents a directional relationship between two requirements or documents.

    Attributes:
        type (str): The type of relationship (e.g., 'Derive', 'Refine', 'Satisfy', 'Verifies').
        sourceId (ObjectId): The ObjectId reference to the source requirement or document.
        destinationId (ObjectId): The ObjectId reference to the destination requirement or document.
    """

    type: str
    sourceId: ObjectId = Field(...)
    destinationId: ObjectId = Field(...)

    class Config:
        arbitrary_types_allowed = True
