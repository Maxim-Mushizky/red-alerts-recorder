from red_alerts_listener.backend.schemas import (
    RedAlertNotification,
    SavedNotification,
    ProcessedRedAlert,
    KnownThreats,
    MetaData,
    GeoLocation
)
from red_alerts_listener.backend import utils


class LocationBuilder:

    @utils.exponential_backoff(max_delay=16)
    @staticmethod
    def try_fetch_city_coordinates(city: str):
        return utils.geolocate_place(city)

    @staticmethod
    def build_location_for_city(city: str) -> GeoLocation:
        coordinates = LocationBuilder.try_fetch_city_coordinates(city)
        if coordinates:
            return GeoLocation(location=city, lon=coordinates.get("lon", 0), lat=coordinates.get("lat", 0))
        return GeoLocation(location=city, lon=0, lat=0)


class ParsedNotificationBuilder:

    @staticmethod
    def build_from_raw_notification(raw_notification: RedAlertNotification) -> SavedNotification:
        machine_info = utils.get_machine_info()
        meta_data = MetaData(recorder=machine_info["Hostname"],
                             receiver_ip=machine_info["IP Address (IPv4)"],
                             machine=machine_info["Machine"]
                             )

        processed_notification = ProcessedRedAlert(
            notificationId=raw_notification.notificationId,
            datetime=utils.convert_unix_to_datetime(raw_notification.time, timezone_str="Asia/Jerusalem"),
            munition=KnownThreats(int(raw_notification.threat)).name,
            locations=raw_notification.cities
        )
        notification_to_db = SavedNotification(raw_notification=raw_notification,
                                               processed_notification=processed_notification,
                                               meta_data=meta_data)
        return notification_to_db


if __name__ == '__main__':
    ret = LocationBuilder.build_location_for_city("כרמיאל")
    print(ret)
