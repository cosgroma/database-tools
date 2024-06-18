from databasetools.models.common import Element
from databasetools.models.common import Relationship
from databasetools.models.common import RelationshipType


def test_element():
    element = Element(name="Test Element")
    assert element.name == "Test Element"
    assert element.id is not None
    assert element.created_at is not None
    assert element.tags == []
    assert element.model_dump() == {
        "id": element.id,
        "name": "Test Element",
        "description": None,
        "version": None,
        "tags": [],
        "type": None,
        "sub_type": None,
        "created_by": None,
        "created_at": element.created_at,
        "modified_by": None,
        "modified_at": None,
        "status": None,
        "documentation": None,
    }


def test_element_with_tags():
    element = Element(name="Test Element", tags=["tag1", "tag2", "tag3"])
    assert element.name == "Test Element"
    assert element.id is not None
    assert element.created_at is not None
    assert element.tags == ["tag1", "tag2", "tag3"]
    assert element.model_dump() == {
        "id": element.id,
        "name": "Test Element",
        "description": None,
        "version": None,
        "tags": ["tag1", "tag2", "tag3"],
        "type": None,
        "sub_type": None,
        "created_by": None,
        "created_at": element.created_at,
        "modified_by": None,
        "modified_at": None,
        "status": None,
        "documentation": None,
    }


def test_element_all_fields():
    element = Element(
        name="Test Element",
        description="Test Description",
        version="1.0",
        tags=["tag1", "tag2", "tag3"],
        type="Test Type",
        sub_type="Test Sub-Type",
        created_by="Test User",
        modified_by="Test User",
        status="Test Status",
        documentation="Test Documentation",
    )
    assert element.name == "Test Element"
    assert element.id is not None
    assert element.created_at is not None
    assert element.tags == ["tag1", "tag2", "tag3"]
    assert element.model_dump() == {
        "id": element.id,
        "name": "Test Element",
        "description": "Test Description",
        "version": "1.0",
        "tags": ["tag1", "tag2", "tag3"],
        "type": "Test Type",
        "sub_type": "Test Sub-Type",
        "created_by": "Test User",
        "created_at": element.created_at,
        "modified_by": "Test User",
        "modified_at": None,
        "status": "Test Status",
        "documentation": "Test Documentation",
    }


def test_relationship():
    source_element = Element(name="Source Element")
    target_element = Element(name="Target Element")
    relationship = Relationship(
        name="Test Relationship",
        source_element_id=source_element.id,
        target_element_id=target_element.id,
        relationship_type=RelationshipType.ASSOCIATION,
    )
    assert relationship.name == "Test Relationship"
    assert relationship.source_element_id == source_element.id
    assert relationship.target_element_id == target_element.id
    assert relationship.relationship_type == RelationshipType.ASSOCIATION
    assert relationship.id is not None
    assert relationship.created_at is not None
