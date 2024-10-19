from pymongo import MongoClient, ASCENDING
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


class MongoDBAdapter:
    """
    A MongoDB Adapter class for connecting to MongoDB and performing CRUD operations.

    This class encapsulates database connection logic and provides methods for creating,
    reading, updating, and deleting documents in a MongoDB collection.

    Attributes:
        uri (str): The MongoDB connection string.
        client (MongoClient): The pymongo MongoClient instance.
        db_name (str): The name of the MongoDB database.
    """

    def __init__(self, uri: str, db_name: str):
        """
        Initializes the MongoDBAdapter class and establishes a connection to the MongoDB server.

        Args:
            uri (str): The MongoDB connection string.
            db_name (str): The name of the database to connect to.
        """
        self.uri = uri
        self.client = MongoClient(self.uri)
        self.db_name = db_name
        self.db = self.client[db_name]

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """
        Inserts a single document into a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            document (Dict[str, Any]): The document to insert.

        Returns:
            str: The inserted document's ID.
        """
        collection = self.db[collection_name]
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Finds a single document in a MongoDB collection that matches the query.

        Args:
            collection_name (str): The name of the collection.
            query (Dict[str, Any]): The query to match.

        Returns:
            Optional[Dict[str, Any]]: The matched document, or None if no document is found.
        """
        collection = self.db[collection_name]
        return collection.find_one(query)

    def find_all(self, collection_name: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Finds all documents in a MongoDB collection that match the query.

        Args:
            collection_name (str): The name of the collection.
            query (Optional[Dict[str, Any]]): The query to match (if not provided, all documents are returned).

        Returns:
            List[Dict[str, Any]]: A list of documents matching the query.
        """
        collection = self.db[collection_name]
        return list(collection.find(query or {}))

    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        Updates a single document in a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            query (Dict[str, Any]): The query to match the document to update.
            update (Dict[str, Any]): The update operation to apply.

        Returns:
            int: The number of documents modified.
        """
        collection = self.db[collection_name]
        result = collection.update_one(query, {"$set": update})
        return result.modified_count

    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> int:
        """
        Deletes a single document from a MongoDB collection.

        Args:
            collection_name (str): The name of the collection.
            query (Dict[str, Any]): The query to match the document to delete.

        Returns:
            int: The number of documents deleted (1 if successful, 0 if not found).
        """
        collection = self.db[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count

    def add_new_index_key(self, collection_name: str, key_name: str) -> str:
        collection = self.db[collection_name]
        result = collection.create_index([(key_name, ASCENDING)], unique=True)
        return result

    def find_by_range(self, collection_name: str,
                      field_name: str,
                      start_value: Union[int, datetime],
                      end_value: Union[int, datetime]) -> List[Dict[str, Any]]:
        """
        Finds documents where a field value is between two values (supports both integers and timestamps).

        Args:
            collection_name (str): The name of the collection.
            field_name (str): The name of the field to query (can be an integer or datetime field).
            start_value (Union[int, datetime]): The start of the value range.
            end_value (Union[int, datetime]): The end of the value range.

        Returns:
            List[Dict[str, Any]]: A list of documents that match the query.
        """
        collection = self.db[collection_name]
        query = {
            field_name: {
                "$gte": start_value,
                "$lte": end_value
            }
        }
        return list(collection.find(query))

    def close_connection(self) -> None:
        """
        Closes the MongoDB connection.
        """
        self.client.close()

    @staticmethod
    def build_connection_uri(
            base_url: str = "mongodb",
            host: str = "localhost",
            port: int = 27017,
            ssl: bool = False,
            read_preference: str = "primary",
            app_name: Optional[str] = None,
            direct_connection: bool = True
    ) -> str:
        """
        Builds a MongoDB connection URI string from individual parameters.

        Args:
            base_url (str): The base address of the url (default: mongodb)
            host (str): The hostname or IP address of the MongoDB server (default: localhost).
            port (int): The port number of the MongoDB server (default: 27017).
            ssl (bool): Whether to use SSL for the connection (default: False).
            read_preference (str): The read preference for the connection (default: primary).
            app_name (Optional[str]): The application name for MongoDB logging (default: None).
            direct_connection (bool): Whether to directly connect to the MongoDB instance (default: True).

        Returns:
            str: The constructed MongoDB URI string.
        """
        uri = f"{base_url}://{host}:{port}/"
        options = []

        if read_preference:
            options.append(f"readPreference={read_preference}")

        if app_name:
            options.append(f"appname={app_name}")

        options.append(f"directConnection={'true' if direct_connection else 'false'}")
        options.append(f"ssl={'true' if ssl else 'false'}")

        if options:
            uri += "?" + "&".join(options)

        return uri
