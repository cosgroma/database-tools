"""Common models for the database tools.

This module contains the common models that are shared by the database tools. The models are used to define the structure of the data that is stored in the database.

Classes:
    Element: A base element.
    Relationship: A relationship between two elements.
    RelationshipType: The type of relationship between two elements.

"""

from datetime import datetime
from typing import List
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class Element(BaseModel):
    """A base element

    A base element contains common attributes that are shared by all elements. It contains information about the unique identifier, name, description, version, tags, type, sub-type, created by, created at, modified by, modified at, status, and documentation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: ObjectId = Field(default_factory=ObjectId, description="The unique identifier of the element.")
    name: Optional[str] = Field(None, description="The name of the element.")
    description: Optional[str] = Field(None, description="The description of the element.")
    version: Optional[str] = Field(None, description="The version of the element.")
    tags: List[str] = Field([], description="The tags associated with the element.")
    type: Optional[str] = Field(None, description="The type of the element.")
    sub_type: Optional[str] = Field(None, description="The sub-type of the element.")
    created_by: Optional[str] = Field(None, description="The user who created the element.")
    created_at: datetime = Field(default_factory=datetime.now, description="The date and time the element was created.")
    modified_by: Optional[str] = Field(None, description="The user who last modified the element.")
    modified_at: Optional[datetime] = Field(None, description="The date and time the element was last modified.")
    status: Optional[str] = Field(None, description="The status of the element.")
    documentation: Optional[str] = Field(None, description="The documentation associated with the element.")


class Relationship(Element):
    """A relationship between two elements.

    A relationship element represents a relationship between two elements. It contains information about the source element, target element, and the type of relationship between the two elements.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    source_element_id: ObjectId = Field(..., description="The ObjectId reference to the source element.")
    target_element_id: ObjectId = Field(..., description="The ObjectId reference to the target element.")
    relationship_type: Optional[str] = Field(None, description="The type of relationship between the source and target elements.")


class RelationshipType:
    ASSOCIATION = "Association"
    DEPENDENCY = "Dependency"
    AGGREGATION = "Aggregation"
    COMPOSITION = "Composition"
    INHERITANCE = "Inheritance"
    REALIZATION = "Realization"
