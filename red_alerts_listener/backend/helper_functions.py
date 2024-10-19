from datetime import datetime

from red_alerts_listener.backend import database_collection_handlers as db_handlers
from red_alerts_listener.backend.config_reader import config
from red_alerts_listener.backend.listening_handlers import RedAlertNotificationsListener
from red_alerts_listener.backend.logger import logger


def get_red_alert_notification_listener(**kwargs):
    logger.info(f"Begin listening at {datetime.now()}")
    raw_alerts_collection_handler = db_handlers.RawAlertsLocationHandler(
        host=config.mongodb.host,
        port=config.mongodb.port,
        collection=config.mongodb.raw_notifications_collection,
        db_name=config.mongodb.db_name
    )
    parsed_alerts_collection_handler = db_handlers.ParsedAlertsCollectionHandler(
        host=config.mongodb.host,
        port=config.mongodb.port,
        collection=config.mongodb.parsed_notifications_collection,
        db_name=config.mongodb.db_name
    )
    locations_collection_handler = db_handlers.LocationsCollectionHandler(
        host=config.mongodb.host,
        port=config.mongodb.port,
        collection=config.mongodb.locations_collection,
        db_name=config.mongodb.db_name
    )

    return RedAlertNotificationsListener(raw_alerts_collection_handler,
                                         parsed_alerts_collection_handler,
                                         locations_collection_handler,
                                         **kwargs)
