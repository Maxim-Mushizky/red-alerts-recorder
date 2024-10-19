import socket
import os
import platform
import getpass
import uuid
from datetime import datetime
import pytz
from geopy import Photon
from typing import Optional
import functools
import time
import random


def get_machine_info():
    # Get the machine's hostname
    hostname = socket.gethostname()

    # Get the machine's IP address (IPv4)
    ip_address = socket.gethostbyname(hostname)

    # Get the machine's username
    username = getpass.getuser()

    # Get platform details
    os_name = os.name  # e.g., 'nt' for Windows, 'posix' for Linux/macOS
    system = platform.system()  # e.g., 'Windows', 'Linux', 'Darwin' (for macOS)
    release = platform.release()  # e.g., '10' for Windows 10, version number for others
    version = platform.version()  # OS version details
    machine = platform.machine()  # e.g., 'x86_64', 'AMD64', 'arm64'
    processor = platform.processor()  # Processor info (e.g., 'Intel64 Family 6 Model 158')
    uuid_value = uuid.UUID(int=uuid.getnode()).hex[-12:]  # Get hardware address (MAC address)

    # Gather all details into a dictionary
    machine_details = {
        "Hostname": hostname,
        "IP Address (IPv4)": ip_address,
        "Username": username,
        "OS Name": os_name,
        "System": system,
        "Release": release,
        "Version": version,
        "Machine": machine,
        "Processor": processor,
        "MAC Address": ':'.join(uuid_value[i:i + 2] for i in range(0, 12, 2))  # Format MAC
    }

    return machine_details


def convert_unix_to_datetime(unix_time: int,
                             datetime_format: str = "%Y-%m-%d %H:%M:%S"
                             , timezone_str: str = "UTC") -> str:
    """
    Converts a Unix timestamp to a formatted datetime string in the specified timezone.

    Args:
        unix_time (int): The Unix timestamp (seconds since epoch).
        datetime_format (str): The desired datetime format (e.g., "%Y-%m-%d %H:%M:%S").
        timezone_str (str): The timezone as a string (e.g., "Asia/Jerusalem"). Default is "UTC".

    Returns:
        str: The formatted datetime string in the specified timezone.
    """
    # Create a timezone object
    target_timezone = pytz.timezone(timezone_str)

    # Convert the Unix timestamp to a datetime object in UTC
    utc_dt = datetime.utcfromtimestamp(unix_time).replace(tzinfo=pytz.utc)

    # Convert the UTC datetime to the target timezone
    local_dt = utc_dt.astimezone(target_timezone)

    # Format the datetime in the specified format
    return local_dt.strftime(datetime_format)


def geolocate_place(place_name: str) -> Optional[dict[str, float]]:
    geolocator = Photon(user_agent="geoapiExercises")  # You can use any app name
    location = geolocator.geocode(place_name)
    if location:
        return {"lat": location.latitude, "lon": location.longitude}
    else:
        return None


def exponential_backoff(max_retries=5, base_delay=1, max_delay=32, jitter=True):
    """
    Exponential backoff decorator for retrying a caller function.

    Args:
        max_retries (int): Maximum number of retries.
        base_delay (int): Initial delay between retries in seconds.
        max_delay (int): Maximum delay between retries in seconds.
        jitter (bool): Whether to add randomness to the delay.

    Returns:
        function: The decorated function with exponential backoff.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = base_delay

            while retries < max_retries:
                try:
                    # Attempt the caller function
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise e  # Max retries exceeded, raise the exception
                    else:
                        # Apply exponential backoff and jitter if needed
                        if jitter:
                            delay = min(max_delay, delay * 2) + random.uniform(0, 1)
                        else:
                            delay = min(max_delay, delay * 2)

                        print(f"Retry {retries}/{max_retries} failed: {e}. Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)

        return wrapper

    return decorator
