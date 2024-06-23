from datetime import datetime
from typing import List
from typing import Optional

from pydantic import Field

from .common import Element


class ModelElementType:
    REQUIREMENT = "Requirement"
    SYSTEM_COMPONENT = "SystemComponent"
    SYSTEM_BUILD = "SystemBuild"
    BEHAVIOR = "Behavior"
    RELATIONSHIP = "Relationship"


class Requirement(Element):
    """A requirement element

    A requirement element represents a requirement of a system. It contains information about the requirement text, priority, rationale, verification method, verification status, verification results, and verification date.
    """

    type: str = ModelElementType.REQUIREMENT
    req_id: Optional[str] = Field(None, description="The unique identifier of the requirement.")
    text: Optional[str] = Field(None, description="The text of the requirement.")
    priority: Optional[str] = Field(None, description="The priority of the requirement.")
    rationale: Optional[str] = Field(None, description="The rationale of the requirement.")
    verification_method: Optional[str] = Field(None, description="The verification method of the requirement.")
    verification_status: Optional[str] = Field(None, description="The verification status of the requirement.")
    verification_results: Optional[str] = Field(None, description="The verification results of the requirement.")
    verification_date: Optional[datetime] = Field(None, description="The verification date of the requirement.")


class SystemComponent(Element):
    """A system component element

    A system component element represents a component of a system. It contains information about the type of component and its specifications.
    """

    type: str = ModelElementType.SYSTEM_COMPONENT
    component_type: Optional[str] = Field(None, description="The type of the system component.")
    specifications: Optional[dict] = Field(None, description="The specifications of the system component.")


class SystemBuild(Element):
    """A system build element

    A system build element represents a build of a system. It contains information about the build number and the components that are included in the build.
    """

    type: str = ModelElementType.SYSTEM_BUILD
    build_number: Optional[str] = Field(None, description="The build number of the system build.")
    components: Optional[List[str]] = Field(None, description="The components of the system build.")


class Behavior(Element):
    type: str = ModelElementType.BEHAVIOR
    behavior_type: Optional[str] = Field(None, description="The type of behavior.")
    specific_behavior_id: Optional[str] = Field(None, description="The specific behavior id.")
