import json
from pydantic import Field
from pymongo import MongoClient
from pymongo.collection import Collection

from pydantic import BaseModel
from databasetools import MongoCollectionController

import os
MONGO_URI = os.getenv("MONGO_URI")


MONGO_TEST_DB = "test_db"
MONGO_TEST_COLLECTION = "test_collection"

def check_environment():
    assert MONGO_URI is not None, "MONGO_URI is not set in the environment variables."

class User(BaseModel):
    name: str = Field(..., title="Name of the user")
    age: int = Field(..., title="Age of the user")

def test_mongo_controller():
    check_environment()
    client = MongoClient(MONGO_URI)
    db = client[MONGO_TEST_DB]
    collection: Collection = db[MONGO_TEST_COLLECTION]

    controller = MongoCollectionController[User](collection, User)
    # Clear the collection for testing
    controller.delete({})
    
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
    
    # Create with class instance
    user = User(name="Alice", age=30)
    user = controller.create(user)
    assert user.name == "Alice"
    assert user.age == 30
    
    # Test delete_item
    deleted = controller.delete_item(user)
    assert deleted
    users = controller.read({"name": "Alice"})
    assert len(users) == 0
    
    # Test repr
    assert "MongoCollectionController" in repr(controller)
    
def test_save_all_to_json():
    check_environment()

    client = MongoClient(MONGO_URI)
    db = client[MONGO_TEST_DB]
    collection: Collection = db[MONGO_TEST_COLLECTION]

    controller = MongoCollectionController[User](collection, User)

    # Test create
    user_data = {"name": "Alice", "age": 30}
    user = controller.create(user_data)
    assert user.name == "Alice"
    assert user.age == 30
    
    # Make more
    user2 = User(name="Bob", age=25)
    user2 = controller.create(user2)
    assert user2.name == "Bob"
    assert user2.age == 25
    
    user3 = User(name="Charlie", age=35)
    user3 = controller.create(user3)
    assert user3.name == "Charlie"
    assert user3.age == 35
    
    # Test save_all_to_json
    file_path = "test_users.json"
    controller.save_all_to_json(file_path)
    assert os.path.exists(file_path)
    
    # load the file
    
    with open(file_path, "r") as f:
        data = json.load(f)
        
    assert len(data) == 3
    assert data[0]["name"] == "Alice"
    assert data[0]["age"] == 30
    assert data[1]["name"] == "Bob"
    assert data[1]["age"] == 25
    assert data[2]["name"] == "Charlie"
    assert data[2]["age"] == 35
    
    # Delete the users
    controller.delete({})
    
    assert len(controller) == 0
    
    # Delete the file
    os.remove(file_path)
    
    assert not os.path.exists(file_path)

def test_iterate():
    check_environment()

    client = MongoClient(MONGO_URI)
    db = client[MONGO_TEST_DB]
    collection: Collection = db[MONGO_TEST_COLLECTION]

    controller = MongoCollectionController[User](collection, User)
    controller.delete({})
    # Test create
    user_data = {"name": "Alice", "age": 30}
    user = controller.create(user_data)
    assert user.name == "Alice"
    assert user.age == 30
    
    user2 = User(name="Bob", age=25)
    user2 = controller.create(user2)
    assert user2.name == "Bob"
    assert user2.age == 25

    # Test iteration
    for user in controller:
        assert user.name == "Alice"
        assert user.age == 30
        break
    
    # Test Next    
    user = next(controller)
    assert user.name == "Bob"
    assert user.age == 25
    
    # Test len
    assert len(controller) == 2
    
    # Clear the collection
    controller.delete({})
    
    assert len(controller) == 0
    

    
    