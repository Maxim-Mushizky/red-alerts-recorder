import abc
from datetime import datetime
from typing import Type, Optional, Any, Union

from red_alerts_listener.backend.config_reader import config
from red_alerts_listener.backend.logger import logger

from red_alerts_listener.backend.mongo_adapter import MongoDBAdapter
from red_alerts_listener.backend.object_builders import LocationBuilder, ParsedNotificationBuilder
from red_alerts_listener.backend.schemas import RedAlertNotification, SavedNotification


class AbcAlertsDataBaseHandlers(abc.ABC):
    BASE_URI = 'mongodb'

    def __init__(self, adapter: Type[MongoDBAdapter],
                 host: str,
                 port: int,
                 alerts_collection: str,
                 db_name: str) -> None:
        self._uri = adapter.build_connection_uri(self.BASE_URI, host, port)
        self._db_name = db_name
        self.adapter = adapter(self._uri, self._db_name)
        self.raw_alerts_collection = alerts_collection

    @abc.abstractmethod
    def add_new_notification(self):
        ...

    @abc.abstractmethod
    def add_multiple_new_notifications(self):
        ...


class LocationsCollectionHandler:
    BASE_URI = 'mongodb'

    def __init__(self, adapter: Type[MongoDBAdapter] = MongoDBAdapter,
                 host: str = config.mongodb.host,
                 port: int = config.mongodb.port,
                 collection: str = config.mongodb.locations_collection,
                 db_name: str = config.mongodb.db_name,
                 set_new_index_key: Optional[str] = None) -> None:
        self._uri = adapter.build_connection_uri(self.BASE_URI, host, port)
        self._db_name = db_name
        self.adapter = adapter(self._uri, self._db_name)
        self.collection = collection
        if set_new_index_key:
            self.adapter.add_new_index_key(collection, set_new_index_key)

    def find_location_by_city(self, city: str) -> Optional[dict[str, Any]]:
        query = {"location": city}
        return self.adapter.find_one(self.collection, query)

    def add_new_city_location(self, city: str) -> Optional[str]:
        if not self.find_location_by_city(city):
            geo_location = LocationBuilder.build_location_for_city(city)
            if geo_location.lon and geo_location.lat:
                logger.info(f"Added location: {geo_location}")
                return self.adapter.insert_one(self.collection, geo_location.dict())
        logger.info(f"city {city} already exists in the collection")
        return None


class RawAlertsLocationHandler:
    BASE_URI = 'mongodb'

    def __init__(self, adapter: Type[MongoDBAdapter] = MongoDBAdapter,
                 host: str = config.mongodb.host,
                 port: int = config.mongodb.port,
                 collection: str = config.mongodb.raw_notifications_collection,
                 db_name: str = config.mongodb.db_name,
                 set_new_index_key: Optional[str] = None) -> None:
        self._uri = adapter.build_connection_uri(self.BASE_URI, host, port)
        self._db_name = db_name
        self.adapter = adapter(self._uri, self._db_name)
        self.collection = collection
        if set_new_index_key:
            self.adapter.add_new_index_key(collection, set_new_index_key)

    def get_all_notifications(self) -> list[dict]:
        query = {}
        results = self.adapter.find_all(self.collection, query=query)
        return results

    # Read only queries
    def find_notification_by_id(self, notification_id: str) -> Optional[dict[str, Any]]:
        query = {"notificationId": notification_id}
        return self.adapter.find_one(self.collection, query)

    def find_notifications_by_city(self, city: str):
        query = {"cities": {"$in": [city]}}
        return self.adapter.find_all(self.collection, query)

    def find_notification_by_datetime_range(self, start: Union[int, datetime],
                                            end: Union[int, datetime]) -> list[dict]:
        results = self.adapter.find_by_range(self.collection, "time", start, end)
        return results

    # Crud
    def add_new_notification(self, notification: RedAlertNotification) -> Optional[str]:
        if not self.find_notification_by_id(notification.notificationId):
            return self.adapter.insert_one(self.collection, notification.dict())
        return None


class ParsedAlertsCollectionHandler:
    BASE_URI = 'mongodb'

    def __init__(self, adapter: Type[MongoDBAdapter] = MongoDBAdapter,
                 host: str = config.mongodb.host,
                 port: int = config.mongodb.port,
                 collection: str = config.mongodb.parsed_notifications_collection,
                 db_name: str = config.mongodb.db_name,
                 set_new_index_key: Optional[str] = None) -> None:
        self._uri = adapter.build_connection_uri(self.BASE_URI, host, port)
        self._db_name = db_name
        self.adapter = adapter(self._uri, self._db_name)
        self.collection = collection
        if set_new_index_key:
            self.adapter.add_new_index_key(collection, set_new_index_key)

    def find_notification_by_id(self, notification_id: str) -> Optional[dict[str, Any]]:
        query = {"raw_notification.notificationId": notification_id}
        return self.adapter.find_one(self.collection, query)

    def add_new_notification(self, notification_to_db: SavedNotification) -> Optional[str]:
        if not self.find_notification_by_id(notification_to_db.raw_notification.notificationId):
            return self.adapter.insert_one(self.collection, notification_to_db.dict())
        logger.info(f"Notification with {notification_to_db.raw_notification.notificationId} already exists")
        return None

    def add_new_notification_from_raw(self, raw_notification: RedAlertNotification) -> Optional[str]:
        if not self.find_notification_by_id(raw_notification.notificationId):
            notification_to_db = ParsedNotificationBuilder.build_from_raw_notification(raw_notification)
            logger.info(f"Adding {notification_to_db} to the collection")
            return self.adapter.insert_one(self.collection, notification_to_db.dict())
        logger.info(f"Notification with {raw_notification.notificationId} already exists in collection")
        return None
