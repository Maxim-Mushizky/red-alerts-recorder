from pydantic import BaseModel, Field
import datetime
import enum


class KnownThreats(enum.Enum):
    ROCKET = 0
    UAV = 5
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class RedAlertNotification(BaseModel):
    notificationId: str
    time: int
    threat: int
    isDrill: bool
    cities: list[str]


class GeoLocation(BaseModel):
    location: str
    lon: float
    lat: float


class ProcessedRedAlert(BaseModel):
    notificationId: str
    datetime: str
    munition: str
    locations: list[str]


class MetaData(BaseModel):
    recorder: str  # username
    machine: str  # machine used
    receiver_ip: str


class SavedNotification(BaseModel):
    raw_notification: RedAlertNotification
    processed_notification: ProcessedRedAlert
    meta_data: MetaData
