from multiprocessing import Process
from datetime import datetime

from red_alerts_listener.backend.config_reader import config
from red_alerts_listener.backend.logger import logger
from red_alerts_listener.backend.listening_handlers import RedAlertNotificationsListener
from red_alerts_listener.backend import database_collection_handlers as db_handlers


def start_listening():
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

    notifications_listener = RedAlertNotificationsListener(raw_alerts_collection_handler,
                                                           parsed_alerts_collection_handler,
                                                           locations_collection_handler)
    notifications_listener.poll_alerts()
    p = Process(target=notifications_listener.poll_alerts)
    p.start()


if __name__ == '__main__':
    start_listening()
