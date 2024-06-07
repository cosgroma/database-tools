from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from pydantic import ValidationError
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from .base_controller import DatabaseController
from .base_controller import T


class GenericController(DatabaseController[T]):
    """A generic controller that can be used to perform CRUD operations on a MongoDB collection.

    Attributes:
        collection (Collection): The MongoDB collection to perform operations on.
        model (Type[T]): The Pydantic model associated with the
            collection that represents the documents.

    Methods:
        create(document_data: Dict[str, Any]) -> T:
            Creates a new document in the collection.
        read(query: Dict[str, Any]) -> List[T]:
            Reads documents from the collection.
        update(query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
            Updates documents in the collection.
        delete(query: Dict[str, Any]) -> bool:
            Deletes documents from the collection.

    """

    def __init__(self, collection: Collection, model: Type[T]):
        """Initializes the generic controller.

        Parameters:
            collection (Collection): The MongoDB collection to perform operations on.
            model (Type[T]): The Pydantic model associated with the
                collection that represents the documents.
        """
        self.collection = collection
        self.model = model

    def create(self, document_data: Dict[str, Any]) -> T:
        """
        Creates a new document in the collection.

        Parameters:
            document_data (Dict[str, Any]): The data of the document to create.

        Returns:
            T: The created document as a Pydantic model instance.
        """
        try:
            document = self.model(**document_data)
            result = self.collection.insert_one(document.model_dump(by_alias=True))
            if not result.acknowledged:
                raise PyMongoError("Insert operation not acknowledged by MongoDB.")
            return document
        except ValidationError as e:
            # Handle validation errors
            print(f"Validation error: {e}")
            raise
        except PyMongoError as e:
            # Handle MongoDB errors
            print(f"Database error: {e}")
            raise

    def read(self, query: Dict[str, Any], limit: Optional[int] = None) -> List[T]:
        """
        Reads documents from the collection.

        Parameters:
            query (Dict[str, Any]): The query to filter documents.

        Returns:
            List[T]: A list of document instances as Pydantic model objects.
        """
        try:
            documents = self.collection.find(query).limit(limit) if limit else self.collection.find(query)
            return [self.model(**doc) for doc in documents]
        except ValidationError as e:
            raise ValidationError(f"Validation error: {e}") from e
        except PyMongoError as e:
            raise PyMongoError(f"Database error: {e}") from e
        except Exception as e:
            raise Exception(f"Error: {e}") from e

    def update(self, query: Dict[str, Any], update_data: Dict[str, Any]) -> bool:
        """
        Updates documents in the collection.

        Parameters:
            query (Dict[str, Any]): The query to filter documents to update.
            update_data (Dict[str, Any]): The data to update in the documents.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        result = self.collection.update_many(query, {"$set": update_data})
        return result.modified_count > 0

    def delete(self, query: Dict[str, Any]) -> bool:
        """
        Deletes documents from the collection.

        Parameters:
            query (Dict[str, Any]): The query to filter documents to delete.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        result = self.collection.delete_many(query)
        return result.deleted_count > 0

    def __iter__(self):
        return self.collection.find()

    def __next__(self):
        return next(self.collection.find())

    def __len__(self):
        return self.collection.count_documents({})

    def __repr__(self):
        return f"GenericController(collection={self.collection}, model={self.model})"
