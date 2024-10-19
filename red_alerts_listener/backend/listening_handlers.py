import requests
import json
import time
from typing import Optional
import aiohttp
import asyncio

from red_alerts_listener.backend.config_reader import config
from red_alerts_listener.backend.database_collection_handlers import LocationsCollectionHandler, \
    RawAlertsLocationHandler, \
    ParsedAlertsCollectionHandler
from red_alerts_listener.backend.logger import logger
from red_alerts_listener.backend.schemas import (
    RedAlertNotification,
)


class RedAlertNotificationsListener:
    URL = config.urls.tzevaadom_api

    def __init__(self,
                 raw_alerts_collection_handler: RawAlertsLocationHandler,
                 parsed_alerts_collection_handler: ParsedAlertsCollectionHandler,
                 locations_collection_handler: LocationsCollectionHandler,
                 interval_in_sec: float = 0.5):
        self.raw_alerts_collection_handler = raw_alerts_collection_handler
        self.locations_collection_handler = locations_collection_handler
        self.parsed_alerts_collection_handler = parsed_alerts_collection_handler
        self.interval_in_sec = interval_in_sec
        self._notification_ids: list[str] = []

    @property
    def notification_ids(self) -> list[str]:
        return self._notification_ids

    def _get_red_alert_notifications(self) -> Optional[list[dict]]:
        response = requests.get(self.URL)
        if response.status_code == 200:
            message = response.text.strip()
            parsed_message = json.loads(message)
            if parsed_message:
                logger.info(f"Got an alert!: {parsed_message}")
                return parsed_message
        return None

    def _add_to_collections(self, notification: RedAlertNotification
                            ) -> tuple[Optional[str], Optional[str], list[str]]:
        """
        Helper functions that populates collections used by the RedAlertNotificationsListener class
        Args:
            notification: RedAlertNotification valid object

        Returns:
             A tuple containing the new ids (_id) for collections raw_alerts, parsed_alerts and list of location ids

        """
        # Initiate returning objects
        location_ids = []

        if raw_id := self.raw_alerts_collection_handler.add_new_notification(notification):
            self._notification_ids.append(raw_id)
            logger.info(f"Added notification to raw_alerts collection. id: {raw_id}")
        if parsed_id := self.parsed_alerts_collection_handler.add_new_notification_from_raw(notification):
            logger.info(f"Added notification to parsed_alerts collection. id: {parsed_id}")
        for city in notification.cities:
            if location_id := self.locations_collection_handler.add_new_location(city):
                location_ids.append(location_id)
                logger.info(f"Added new city location to locations collection. id: {location_id}")

        return raw_id, parsed_id, location_ids

    def poll_alerts(self):
        logger.info(f"Begin polling alerts from {self.URL}")
        while True:
            try:
                alerts = self._get_red_alert_notifications()  # poll for alerts from the frontend
                if alerts:
                    raw_notifications = [RedAlertNotification.parse_obj(alert) for alert in alerts]
                    for raw_notification in raw_notifications:
                        self._add_to_collections(raw_notification)
            except requests.RequestException as e:
                logger.warning(f"Error: {e}")
            except Exception as e:
                logger.error(f"Encountered an error during polling alerts. {e}")
            time.sleep(self.interval_in_sec)

    async def _async_get_red_alert_notifications(self) -> Optional[list[dict]]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.URL) as response:
                    if response.status == 200:
                        message = await response.text()
                        parsed_message = json.loads(message.strip())
                        if parsed_message:
                            logger.info(f"Got an alert!: {parsed_message}")
                            return parsed_message
            except aiohttp.ClientError as e:
                logger.warning(f"Error: {e}")
            except Exception as e:
                logger.error(f"Encountered an error during fetching alerts. {e}")
        return None

    async def async_poll_alerts(self):
        logger.info(f"Begin polling alerts from {self.URL} asynchronously")
        while True:
            try:
                alerts = await self._async_get_red_alert_notifications()
                if alerts:
                    raw_notifications = [RedAlertNotification.parse_obj(alert) for alert in alerts]
                    for raw_notification in raw_notifications:
                        self._add_to_collections(raw_notification)
            except Exception as e:
                logger.error(f"Encountered an error during polling alerts. {e}")
            await asyncio.sleep(self.interval_in_sec)
