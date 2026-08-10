"""Constants for the Renson Healthbox Go integration."""

from datetime import timedelta

DOMAIN = "healthbox_go"
CONF_HOST = "host"

PLATFORMS = [
    "binary_sensor",
    "button",
    "fan",
    "number",
    "select",
    "sensor",
    "switch",
    "time",
]

DEFAULT_SCAN_INTERVAL = timedelta(seconds=15)
REQUEST_TIMEOUT = 10

PROFILE_TO_API = {"Eco": 0, "Health": 1, "Intensive": 2}
API_TO_PROFILE = {value: key for key, value in PROFILE_TO_API.items()}
RH_TO_API = {"Low": 1, "Standard": 3, "High": 5}
API_TO_RH = {value: key for key, value in RH_TO_API.items()}

SCHEDULE_DAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

