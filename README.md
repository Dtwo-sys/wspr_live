# WSPR.live Integration for Home Assistant

This is a custom integration that adds sensors to Home Assistant showing WSPR RX and TX spots retrieved from [WSPR.live](https://wspr.live).

## Features

- Adds two sensors:
  - `sensor.wspr_live_rx_spots`
  - `sensor.wspr_live_tx_spots`
- Fully usable in dashboards and automations

## Installation

1. Place the `wspr_live` folder into `/config/custom_components/`
2. Restart Home Assistant

## HACS

Add this repo as a custom repository in HACS under "Integrations".

## Disclaimer

This project was primarily built using generative AI assistance and is provided as-is.
I am not a professional coder. Use at your own risk.

## License

[MIT](LICENSE)
