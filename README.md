# WSPR.live Home Assistant Integration

Track your WSPR (Weak Signal Propagation Reporter) activity live from [https://wspr.live](https://wspr.live) within Home Assistant. This custom integration provides real-time RX and TX spot data including distance, band, SNR, and country.

> **Disclaimer**: This project was generated and optimized with the assistance of AI tools. While tested and functional, it is not developed or maintained by a professional software developer. Use at your own risk.

![Screenshot](https://github.com/user-attachments/assets/9e779a75-6a25-47ac-9a92-a4e5591c5ad4)

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
```

## 🏆 Creating Records with Template Sensors

You can create template sensors to track your personal records based on the WSPR data:

```yaml
template:
  - sensor:
      - name: WSPR Furthest RX Distance
        unit_of_measurement: "km"
        state: >
          {% set spots = state_attr('sensor.wspr_live_rx_spots', 'spots') %}
          {% if spots %}
            {{ spots | map(attribute='distance') | max }}
          {% else %} 0 {% endif %}

      - name: WSPR Furthest RX Callsign
        state: >
          {% set spots = state_attr('sensor.wspr_live_rx_spots', 'spots') %}
          {% if spots %}
            {{ (spots | sort(attribute='distance') | last).tx }}
          {% else %} Unknown {% endif %}
```

ℹ️ Similar templates can be created for TX records.

## 📊 Dashboard Example

Here's a sample card you can add to your dashboard:

```yaml
type: entities
title: WSPR Spots
entities:
  - entity: sensor.wspr_live_rx_spots
    name: Received Spots
    secondary_info: last-updated
  - entity: sensor.wspr_live_tx_spots 
    name: Transmitted Spots
    secondary_info: last-updated
  - entity: sensor.wspr_furthest_rx_distance
    name: Max RX Distance
  - entity: sensor.wspr_furthest_tx_distance
    name: Max TX Distance
```

## 🧠 Long-term Record Tracking

For tracking long-term WSPR records across Home Assistant restarts, you can use `input_number` and `input_text` helpers with automations:

### ➕ Add input helpers

```yaml
input_number:
  wspr_rx_record_distance:
    name: RX Record Distance
    min: 0
    max: 20000
    step: 1
    unit_of_measurement: km

input_text:
  wspr_rx_record_callsign:
    name: RX Record Callsign
```

### 🔁 Create automation to update when a new record is set

```yaml
automation:
  - alias: Update WSPR RX Record
    trigger:
      - platform: state
        entity_id: sensor.wspr_furthest_rx_distance
    condition:
      - condition: template
        value_template: >
          {{ 
            trigger.to_state.state | float(0) > 0 and
            trigger.to_state.state | float(0) > states('input_number.wspr_rx_record_distance') | float(0)
          }}
    action:
      - service: input_number.set_value
        data:
          value: "{{ trigger.to_state.state }}"
        target:
          entity_id: input_number.wspr_rx_record_distance
      - service: input_text.set_value
        data:
          value: "{{ states('sensor.wspr_furthest_rx_callsign') }}"
        target:
          entity_id: input_text.wspr_rx_record_callsign
```

### 🔄 Add a reset script

```yaml
script:
  reset_wspr_records:
    alias: Reset WSPR Records
    sequence:
      - service: input_number.set_value
        data:
          value: 0
        target:
          entity_id: 
            - input_number.wspr_rx_record_distance
            - input_number.wspr_tx_record_distance
```

## ⚠️ Limitations

- Data is limited to the past 24 hours
- Update interval should be 30+ minutes to avoid excessive API usage
- Country determination uses prefix logic, not guaranteed to be 100% accurate

## 🛠️ Troubleshooting

- Check Home Assistant logs for error messages
- Make sure your callsign is entered correctly
- Confirm internet access is working
- Try a longer update interval if data fails to load

## 🔗 Additional Resources

- [WSPR.live](https://wspr.live)
- [WSPR Info - Wikipedia](https://en.wikipedia.org/wiki/WSPR_(amateur_radio_software))
- [Home Assistant Docs](https://www.home-assistant.io/integrations/)
