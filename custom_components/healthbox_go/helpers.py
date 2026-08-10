"""Value extraction helpers for Healthbox Go entities."""

from __future__ import annotations

from datetime import time
from typing import Any

from .api import find_first, parameter_value


def nested(data: dict[str, Any], *path: str, default=None):
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return default
        value = value.get(key)
    return default if value is None else value


def constellation_value(data: dict[str, Any], parameter: str):
    return parameter_value(data.get("constellation", {}), parameter)


def constellation_index_value(data: dict[str, Any], collection: str, index: str, parameter: str):
    record = nested(data.get("constellation", {}), collection, index, "parameter", parameter)
    if isinstance(record, dict):
        return record.get("value")
    return record


def room_value(data: dict[str, Any], *path: str, default=None):
    return nested(data.get("room", {}), *path, default=default)


def current_ventilation(data: dict[str, Any]) -> float | None:
    flow = constellation_value(data, "flow_rate")
    nominal = room_value(data, "nominal")
    try:
        if nominal and float(nominal) > 0:
            return round(float(flow) / float(nominal) * 100, 1)
        return float(flow)
    except (TypeError, ValueError):
        return None


def normal_ventilation(data: dict[str, Any]) -> float | None:
    minimum = room_value(data, "minimum")
    nominal = room_value(data, "nominal")
    try:
        if nominal and float(nominal) > 0:
            return round(float(minimum) / float(nominal) * 100, 1)
    except (TypeError, ValueError):
        pass
    return None


def first_schedule_time(data: dict[str, Any], silent: bool) -> time | None:
    schedule_data = data.get("silent", {})
    for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
        schedule = schedule_data.get(day, [])
        if not isinstance(schedule, list):
            continue
        for event in schedule:
            if isinstance(event, dict) and event.get("silent") is silent:
                value = event.get("time")
                try:
                    hour, minute = str(value).split(":", 1)
                    return time(int(hour), int(minute))
                except (TypeError, ValueError):
                    continue
    return None


def global_value(data: dict[str, Any], *keys: str):
    return find_first(data.get("global", {}), *keys)
