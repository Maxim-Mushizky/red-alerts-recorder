import abc
from typing import Type, Any, Optional

from red_alerts_listener.backend.mongo_adapter import MongoDBAdapter


class AbstractLocationsCollection(abc.ABC):
    BASE_URI = 'mongodb'

    def __init__(self, adapter: Type[MongoDBAdapter],
                 host: str,
                 port: int,
                 collection: str,
                 db_name: str,
                 set_new_index_key: Optional[str] = None
                 ) -> None:
        self._uri = adapter.build_connection_uri(self.BASE_URI, host, port)
        self._db_name = db_name
        self.adapter = adapter(self._uri, self._db_name)
        self.collection = collection
        if set_new_index_key:
            self.adapter.add_new_index_key(collection, set_new_index_key)

    @abc.abstractmethod
    def find_location(self, location: str) -> Optional[dict[str, Any]]:
        ...

    @abc.abstractmethod
    def add_new_location(self, location: str) -> Optional[str]:
        ...


class AbstractRedAlertCollection(abc.ABC):
    BASE_URI = 'mongodb'

    def __init__(self, adapter: Type[MongoDBAdapter],
                 host: str,
                 port: int,
                 collection: str,
                 db_name: str,
                 set_new_index_key: Optional[str] = None
                 ) -> None:
        self._uri = adapter.build_connection_uri(self.BASE_URI, host, port)
        self._db_name = db_name
        self.adapter = adapter(self._uri, self._db_name)
        self.collection = collection
        if set_new_index_key:
            self.adapter.add_new_index_key(collection, set_new_index_key)

    @abc.abstractmethod
    def get_all_notifications(self) -> list[dict]:
        ...

    @abc.abstractmethod
    def add_new_notification(self, notification: Any) -> Optional[str]:
        ...

    @abc.abstractmethod
    def find_notification_by_id(self, notification_id: str) -> Optional[dict[str, Any]]:
        ...
