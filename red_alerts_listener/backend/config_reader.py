from dataclasses import dataclass
import os

from DEFINITIONS import ROOT_DIR
from red_alerts_listener.backend.yaml_parser import YamlFileProcessor


# Define the Python dataclasses to map YAML sections
@dataclass
class AppConfig:
    name: str
    version: str
    log_file: str
    debug: bool


@dataclass
class MongoDatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    db_name: str
    raw_notifications_collection: str
    parsed_notifications_collection: str
    locations_collection: str


@dataclass
class URLS:
    tzevaadom_api: str


class AlertConfig:

    def __init__(self, file_path: str):
        try:
            self.processor = YamlFileProcessor(file_path)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}")

        # Parsing section
        self.app = self.parse_app_section()
        self.mongodb = self.parse_mongodb_section()
        self.urls = self.parse_urls_section()

    def parse_app_section(self, section: str = 'app') -> AppConfig:
        return self.processor.parse_to_object(section=section, obj_class=AppConfig)

    def parse_mongodb_section(self, section: str = 'mongodb') -> MongoDatabaseConfig:
        return self.processor.parse_to_object(section=section, obj_class=MongoDatabaseConfig)

    def parse_urls_section(self, section: str = 'urls') -> URLS:
        return self.processor.parse_to_object(section=section, obj_class=URLS)


config = AlertConfig(os.path.join(ROOT_DIR, "config.yaml"))
