from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_validator


class ElementType(str, Enum):
    GENERIC = "generic"
    USER = "user"
    PROJECT = "project"
    TASK = "task"


class Element(BaseModel):
    element_id: str = Field(..., description="Unique identifier for the element")
    name: str = Field(..., description="Name of the element")
    element_type: ElementType = Field(..., description="Type of the element")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp of the element")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp of the element")
    labels: List[str] = Field(default_factory=list, description="Labels associated with the element")

    class ConfigDict:
        use_enum_values = True


class Relationship(BaseModel):
    source_id: str = Field(..., description="The ID of the source element")
    destination_id: str = Field(..., description="The ID of the destination element")
    relation_type: str = Field(..., description="Type of the relationship")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp of the relationship")

    @field_validator("relation_type")
    def validate_relation_type(cls, value):
        valid_relation_types = {"generalizes", "implements", "contains"}
        if value not in valid_relation_types:
            raise ValueError("Invalid relation type")
        return value


class Relation(BaseModel):
    source_id: str = Field(..., description="The ID of the source element")
    destination_id: str = Field(..., description="The ID of the destination element")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp of the relation")
    relation_type: str = Field(..., description="Type of the relationship")

    @field_validator("relation_type")
    def validate_relation_type(cls, value):
        valid_relation_types = {"capability_to_epic", "epic_to_story", "story_to_task", "many_to_one", "one_to_many", "many_to_many"}
        if value not in valid_relation_types:
            raise ValueError("Invalid relation type")
        return value
