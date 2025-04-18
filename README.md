# WSPR.live Home Assistant Integration

Track your WSPR (Weak Signal Propagation Reporter) activity live from [https://wspr.live](https://wspr.live) within Home Assistant. This custom integration provides real-time RX and TX spot data including distance, band, SNR, and country.

![Screenshot](https://your-screenshot-url-here.png)

## Features

- Two custom sensors: `sensor.wspr_live_tx_spots` and `sensor.wspr_live_rx_spots`
- Pulls live WSPR data from [https://wspr.live](https://wspr.live)
- Country detection based on callsign prefix
- Band label mapping (e.g., 14.0 → 20M)
- Updated regularly (configurable)

## Installation

> **Note**: This project is not yet listed in HACS. Manual installation is required.

### Manual Install

1. Copy the `wspr_live` directory into your Home Assistant `custom_components/` folder.

    ```bash
    custom_components/
    └── wspr_live/
        ├── __init__.py  (optional placeholder)
        ├── manifest.json
        └── sensor.py
    ```

2. Restart Home Assistant.

3. Add the sensor to your `configuration.yaml`:

    ```yaml
    sensor:
      - platform: wspr_live
        callsign: G0IKV
        interval: 60  # in minutes
    ```

4. Check your Home Assistant logs to verify it's working.

## Configuration Options

| Option     | Required | Description                                      |
|------------|----------|--------------------------------------------------|
| `callsign` | Yes      | Your amateur radio callsign (e.g. `G0IKV`)       |
| `interval` | No       | Polling interval in minutes (default: `60`)     |

## Sensor Entities

This integration will create two sensors:

- `sensor.wspr_live_rx_spots`: Spots **received by** your station
- `sensor.wspr_live_tx_spots`: Spots **received by others** from your transmission

Each sensor has attributes:

```yaml
- tx: transmitting station callsign
- rx: receiving station callsign
- band: frequency in MHz
- band_label: e.g. "20M"
- snr: signal-to-noise ratio
- distance: in kilometers
- country: resolved from callsign
- time: UTC timestamp
