"""Protocol mapping tests for the Healthbox Go API client."""

from unittest.mock import AsyncMock

import pytest

from renson_healthbox_go import HealthboxGoApi, parameter_value


@pytest.mark.asyncio
async def test_write_mappings() -> None:
    api = HealthboxGoApi("192.0.2.1", AsyncMock())
    api.put = AsyncMock()

    await api.set_normal_level(30, 60)
    api.put.assert_awaited_with("/v1/decision/room", {"minimum": 18.0})

    await api.set_co2_threshold(950)
    api.put.assert_awaited_with(
        "/v1/decision/room/demand",
        {"CO2": {"static": {"minimum": 700.0, "maximum": 950.0}}},
    )

    await api.set_manual_override(50, 600)
    api.put.assert_awaited_with(
        "/v1/decision/room/boost",
        {"enable": True, "level": 50.0, "timeout": 600, "remaining": 0},
    )

    await api.set_rh_sensitivity(5)
    api.put.assert_awaited_with(
        "/v1/decision/room/sensor_presets",
        [{"sensor_type": "rh", "sensitivity": 5}],
    )


def test_parameter_value_handles_indexed_constellation() -> None:
    data = {
        "sensor": {
            "3": {"parameter": {"concentration": {"value": 567}}},
        },
        "actuator": {
            "0": {"parameter": {"flow_rate": {"value": 18.0}}},
        },
    }
    assert parameter_value(data, "concentration") == 567
    assert parameter_value(data, "flow_rate") == 18.0
