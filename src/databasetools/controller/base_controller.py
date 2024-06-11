""" This module contains the base controller class.

The base controller class is a generic controller that can be used to perform
CRUD operations on a MongoDB collection. It is used as a base class for
controllers that perform operations on specific collections.
"""

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Dict
from typing import Generic
from typing import List
from typing import TypeVar
from typing import Type

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class DatabaseController(ABC, Generic[T]):
    """
    Abstract base class for database controllers.
    """
    model: Type[T]

    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entry in the database.
        """
        ...

    @abstractmethod
    def read(self, query: Dict[str, Any]) -> List[T]:
        """
        Read entries from the database based on a query.
        """
        ...

    @abstractmethod
    def update(self, identifier: T, update_data: Dict[str, Any]) -> bool:
        """
        Update an entry in the database.
        """
        ...

    @abstractmethod
    def delete(self, identifier: T) -> bool:
        """
        Delete an entry from the database.
        """
        ...

    @abstractmethod
    def __iter__(self):
        """
        Iterate over all entries in the database.
        """
        ...

    @abstractmethod
    def __repr__(self):
        """
        Return a string representation of the database controller.
        """
        ...

    def __getitem__(self, key):
        if isinstance(key, slice):
            # Handle slice for pagination maybe
            # pseudocode: read(page=key.start, page_size=(key.stop - key.start))
            ...
        elif isinstance(key, dict):
            # Handle dict as query
            return self.read(key)
        else:
            raise TypeError("Invalid argument type.")

    def __setitem__(self, item: T, value: Dict[str, Any]):

        if not isinstance(value, dict):
            raise ValueError("Value must be a dictionary with update data.")

        self.update(item, value)

    def __delitem__(self, item: T):
        self.delete(item)
