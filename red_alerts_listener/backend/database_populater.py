from red_alerts_listener.backend.logger import logger
from red_alerts_listener.backend.database_collection_handlers import LocationsCollectionHandler, RawAlertsLocationHandler, \
    ParsedAlertsCollectionHandler
from red_alerts_listener.backend import schemas


def populate_all_collections_from_raw_notifications_collection():
    """
    Populates the location and parsed_alerts collections with data collected by the listener from the Tzevaadom API.

    This function retrieves all raw alert notifications from the raw_notifications collection, parses them,
    and inserts data into two other collections:
    1. `parsed_alerts`: Contains processed versions of raw alert notifications.
    2. `locations`: Stores unique location information (cities) related to the alert notifications.

    For each raw notification:
    - It adds a parsed notification to the `parsed_alerts` collection.
    - It extracts the cities from the notification and adds them to the `locations` collection.

    If there is an error during the population process, the function logs a warning but continues processing
    the remaining notifications.

    Returns:
        tuple: A tuple of two lists:
            - List of IDs for the documents added to the `parsed_alerts` collection.
            - List of IDs for the documents added to the `locations` collection.
    """
    # initiate handlers
    raw_notifications_handler = RawAlertsLocationHandler()
    parsed_notifications_handler = ParsedAlertsCollectionHandler()
    locations_handler = LocationsCollectionHandler()

    # all database ids arrays
    all_parsed_collection_ids = []
    all_loc_collection_ids = []

    all_raw_notifications = raw_notifications_handler.get_all_notifications()
    raw_notifications = [schemas.RedAlertNotification.parse_obj(report) for report in all_raw_notifications]

    for raw_notification in raw_notifications:
        try:
            id_for_parsed_collection = parsed_notifications_handler.add_new_notification_from_raw(raw_notification)
            ids_for_loc_collection = [locations_handler.add_new_city_location(city) for city in raw_notification.cities]
        except Exception as e:
            logger.warning(f"Couldn't finished populating one of the collections. reason: {e}")
        else:
            if id_for_parsed_collection:
                all_parsed_collection_ids.append(id_for_parsed_collection)
            if any(ids_for_loc_collection):
                all_loc_collection_ids.extend([_id for _id in ids_for_loc_collection if _id])
    return all_parsed_collection_ids, all_loc_collection_ids


if __name__ == '__main__':
    parsed_ids, loc_ids = populate_all_collections_from_raw_notifications_collection()
    print(f"{len(parsed_ids)} new entries added to the parsed_notifications collection")
    print(f"{len(loc_ids)} new entries added to the locations collection")
