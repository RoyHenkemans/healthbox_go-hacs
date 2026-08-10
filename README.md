# Renson Healthbox Go for Home Assistant

Unofficial Home Assistant custom integration for the local HTTP API of the
Renson Healthbox Go. It does not use the Renson cloud and does not require an
API key.

> This project is based on observed Healthbox Go firmware behaviour. It is not
> affiliated with or supported by Renson.

## Features

- Multiple Healthbox Go units, each identified by its serial number
- UI config flow using a local hostname or IP address
- Reconfigure flow for a changed address
- Temperature, relative/absolute humidity, CO2, VOC, current ventilation and
  ventilation reason
- Wi-Fi signal/status, uptime, firmware and CO2 diagnostics
- Normal ventilation level (10–50%)
- Eco, Health and Intensive profiles
- Manual ventilation with percentage and duration up to 10 hours
- CO2 threshold (500–2000 ppm) and humidity sensitivity
- Breeze mode and temperature threshold
- Extra quiet mode, reduction and daily start/end times

## Installation

### HACS custom repository

HACS installs from a **public GitHub repository**, not directly from a local
zip file. Publish this package as a repository while keeping the included
directory structure unchanged. The integration uses the separate
`renson-healthbox-go` communication library. Publish version 0.1.0 of the
included `library/` project to PyPI first (or use its TestPyPI release while
developing), because Home Assistant installs manifest dependencies from a
package index. Then:

1. Open HACS in Home Assistant.
2. Open the menu (three dots) and choose **Custom repositories**.
3. Enter the GitHub repository URL and select **Integration**.
4. Add the repository and install **Renson Healthbox Go**.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration** and search for
   **Renson Healthbox Go**.
7. Enter the local IP address or hostname. Repeat this step for every unit.

### Manual installation

1. Extract the release zip.
2. Copy `custom_components/healthbox_go` into the `custom_components` folder
   inside the Home Assistant configuration directory. The final path must be:
   `/config/custom_components/healthbox_go/manifest.json`.
3. Restart Home Assistant.
4. Add **Renson Healthbox Go** under **Settings → Devices & services**.

## Manual ventilation actions

The `fan` entity starts a manual override using the Healthbox's configured
default duration. For an exact duration, use the integration action:

```yaml
action: healthbox_go.set_manual_override
data:
  device_id: YOUR_DEVICE_ID
  percentage: 50
  duration: 600
```

Stop it with the **Stop manual override** button or:

```yaml
action: healthbox_go.stop_manual_override
data:
  device_id: YOUR_DEVICE_ID
```

`duration` is measured in seconds and accepts 60–36000 (up to 10 hours).

## Local API endpoints used

The integration polls these endpoints and tolerates optional endpoints that a
firmware version does not expose:

- `GET /v1/constellation`
- `GET /v1/constellation/global`
- `GET /v1/decision/room`
- `GET /v1/decision/breeze`
- `GET /v1/decision/silent`
- `GET /v1/global/uptime`
- `GET /v1/wifi/client/status`
- `GET /v1/decision/room/sensor_presets`

Writes use the matching decision endpoints. The normal ventilation value is
converted against the unit's `nominal` calibrated base specification. Manual
override percentages are sent directly, and the CO2 lower threshold is kept at
250 ppm below the selected upper threshold, matching the Renson app.

## Notes

- Give each Healthbox Go a DHCP reservation so its address stays stable.
- Home Assistant must be able to reach TCP port 80 on the Healthbox VLAN.
- The first release targets the observed local API schema (`schema_version: 2`)
  and firmware 1.3.3. Unknown optional fields are ignored.
- If the address changes, use **Reconfigure** on the integration entry. The
  serial number is checked so an entry cannot silently switch to another unit.

## Development checks

The repository includes workflows for Hassfest and HACS validation. Before
publishing, update `codeowners`, documentation and issue-tracker URLs in
`manifest.json` if the GitHub account or repository name differs.

## Home Assistant Core path

All product communication lives in the standalone asynchronous Python library
under `library/`; the integration injects Home Assistant's shared aiohttp
session. This separation is required for a future Home Assistant Core proposal.
See `CORE_PROPOSAL.md` for the deliberately smaller first-PR scope and remaining
publication/branding work.

