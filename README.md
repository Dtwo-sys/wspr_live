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

Here's a HTML Tempplate Card, add in needed you can add to your dashboard to show Rx Spots:

```yaml
type: custom:html-template-card
title: ""
content: >
  {% set spots = state_attr('sensor.wspr_live_rx_spots', 'spots') %}{% if spots
  and spots[0].time %}{% set dt = as_datetime(spots[0].time) %}{% endif %}<div
  style="font-family: monospace; font-size: 16px; font-weight: bold;
  margin-bottom: 0;">WSPR RX Spots</div><div style="font-family: monospace;
  font-size: 13px; color: #666; margin-top: 0; margin-bottom: 4px;">{% if dt
  %}{{ dt.strftime('%d %B %Y') }} UTC{% endif %}</div><div style="font-family:
  monospace; font-size: 14px;">{% for s in spots %}<div style="display: grid;
  grid-template-columns: 70px 90px 75px 45px 60px auto; grid-gap: 5px; margin:
  1px 0;"><span style="color:#888;">{{ s.time[-8:] }}</span><span
  style="font-weight:bold;">{{ s.tx }}</span><span style="color:#666; font-size:
  12px;">{{ s.country }}</span><span>{{ s.band_label }}</span><span>{{
  '%+3d'|format(s.snr|int) }} dB</span><span style="font-weight:bold;{% if
  s.distance|int > 5000 %}color:red;{% endif %}">{{ (s.distance|float *
  0.621371)|round }}mi</span></div>{% endfor %}</div>

```

And Tx Spots - 

```yaml
type: custom:html-template-card
title: ""
content: >
  {% set spots = state_attr('sensor.wspr_live_tx_spots', 'spots') %}{% if spots
  and spots[0].time %}{% set dt = as_datetime(spots[0].time) %}{% endif %}<div
  style="font-family: monospace; font-size: 16px; font-weight: bold;
  margin-bottom: 0;">WSPR TX Spots</div><div style="font-family: monospace;
  font-size: 13px; color: #666; margin-top: 0; margin-bottom: 4px;">{% if dt
  %}{{ dt.strftime('%d %B %Y') }} UTC{% endif %}</div><div style="font-family:
  monospace; font-size: 14px;">{% for s in spots %}<div style="display: grid;
  grid-template-columns: 70px 90px 75px 45px 60px auto; grid-gap: 5px; margin:
  1px 0;"><span style="color:#888;">{{ s.time[-8:] }}</span><span
  style="font-weight:bold;">{{ s.rx }}</span><span style="color:#666; font-size:
  12px;">{{ s.country }}</span><span>{{ s.band_label }}</span><span>{{
  '%+3d'|format(s.snr|int) }} dB</span><span style="font-weight:bold;{% if
  s.distance|int > 5000 %}color:red;{% endif %}">{{ (s.distance|float *
  0.621371)|round }}mi</span></div>{% endfor %}</div>

...


## 🧠 Long-term Record Tracking

For tracking long-term WSPR records across Home Assistant restarts, you can use `input_number` and `input_text` helpers with automations.


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
