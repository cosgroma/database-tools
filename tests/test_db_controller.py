from pydantic import Field
from pymongo import MongoClient
from pymongo.collection import Collection

from databasetools import BaseModel
from databasetools import DatabaseController


def test_generic_controller():

    class User(BaseModel):
        name: str = Field(..., title="Name of the user")
        age: int = Field(..., title="Age of the user")

    client = MongoClient("mongodb://localhost:27017/")
    db = client["test_db"]
    collection: Collection = db["test_collection"]

    controller = DatabaseController[User](collection, User)

    # Test create
    user_data = {"name": "Alice", "age": 30}
    user = controller.create(user_data)
    assert user.name == "Alice"
    assert user.age == 30

    # Test read
    users = controller.read({"name": "Alice"})
    assert len(users) == 1
    assert users[0].name == "Alice"
    assert users[0].age == 30

    # Test update
    update_data = {"age": 31}
    updated = controller.update({"name": "Alice"}, update_data)
    assert updated
    users = controller.read({"name": "Alice"})
    assert users[0].age == 31

    # Test delete
    deleted = controller.delete({"name": "Alice"})
    assert deleted
    users = controller.read({"name": "Alice"})
    assert len(users) == 0

    print("All tests passed!")
