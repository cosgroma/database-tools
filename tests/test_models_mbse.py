from databasetools.models.mbse import ModelElementType
from databasetools.models.mbse import Requirement
from databasetools.models.mbse import SystemComponent


def test_requirement():
    requirement = Requirement(name="Test Requirement", text="This is a test requirement.")
    assert requirement.name == "Test Requirement"
    assert requirement.text == "This is a test requirement"
    assert requirement.id is not None
    assert requirement.created_at is not None
    assert requirement.model_dump() == {
        "id": requirement.id,
        "name": "Test Requirement",
        "description": None,
        "version": None,
        "tags": [],
        "type": ModelElementType.REQUIREMENT,
        "sub_type": None,
        "created_by": None,
        "created_at": requirement.created_at,
        "modified_by": None,
        "modified_at": None,
        "status": None,
        "documentation": None,
        "req_id": None,
        "text": "This is a test requirement.",
        "priority": None,
        "rationale": None,
        "verification_method": None,
        "verification_status": None,
        "verification_results": None,
        "verification_date": None,
    }


def test_system_component():
    system_component = SystemComponent(name="Test System Component", component_type="Test Type")
    assert system_component.name == "Test System Component"
    assert system_component.component_type == "Test Type"
    assert system_component.id is not None
    assert system_component.created_at is not None
    assert system_component.model_dump() == {
        "id": system_component.id,
        "name": "Test System Component",
        "description": None,
        "version": None,
        "tags": [],
        "type": None,
        "sub_type": None,
        "created_by": None,
        "created_at": system_component.created_at,
        "modified_by": None,
        "modified_at": None,
        "status": None,
        "documentation": None,
        "component_type": "Test Type",
        "specifications": None,
    }
