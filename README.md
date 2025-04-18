WSPR.live Integration for Home Assistant
Overview
The WSPR.live integration allows amateur radio operators to access and display WSPR (Weak Signal Propagation Reporter) data within Home Assistant. WSPR is a protocol used by ham radio operators to test radio wave propagation across the globe using low-power transmissions. This integration connects to the WSPR.live database to retrieve information about stations that have received your transmissions (TX spots) and stations you have received (RX spots).
What is WSPR?
WSPR (pronounced "whisper") stands for Weak Signal Propagation Reporter. It is a digital mode designed to send and receive low-power transmissions to test propagation paths on the amateur radio bands. The protocol uses a compressed data format to transmit a callsign, grid locator, and power level, allowing other stations to receive and report these signals even when they are extremely weak, sometimes below the noise floor.
Features
Real-time TX Data: View stations that have received your transmissions
Real-time RX Data: View stations you have received
Detailed Information: For each spot, see:
Station callsigns
Signal-to-noise ratio (SNR)
Distance in kilometers
Band information
Country information (derived from callsigns)
Timestamp of reception
Automatic Updates: Data refreshes at configurable intervals
Installation
Copy the wspr_live folder to your Home Assistant custom_components directory
Restart Home Assistant
Configure the integration in your configuration.yaml file
Configuration
Add the following to your configuration.yaml:
yaml


sensor:
  - platform: wspr_live
    callsign: YOUR_CALLSIGN  # Your amateur radio callsign
    interval: 30             # Update interval in minutes (default is 60)
Configuration Options
Option	Description	Required	Default
callsign	Your amateur radio callsign	Yes	None
interval	Update interval in minutes	No	60

Export as CSV
Usage
After installation and configuration, two sensors will be created:
sensor.wspr_live_rx_spots: Shows spots you've received
sensor.wspr_live_tx_spots: Shows spots where your signal was received
Sensor Attributes
Each sensor provides the following attributes:
state: Number of spots received/transmitted in the last 24 hours
spots: A list of spot details including:
tx: Transmitting station callsign
rx: Receiving station callsign
band: Frequency band in MHz
band_label: Band name (e.g., "20M", "40M")
snr: Signal-to-noise ratio in dB
distance: Distance in kilometers
time: Timestamp of reception
country: Country derived from callsign
updated: Timestamp of last update
Creating Records with Template Sensors
You can create template sensors to track your personal records based on the WSPR data:
yaml


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

      # Similar templates for TX records
Dashboard Example
Here's a sample card you can add to your dashboard:
yaml


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
Long-term Record Tracking
For tracking long-term WSPR records across Home Assistant restarts, you can use input helpers and automations:
Add input helpers to store your records:
yaml


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
Create automations to update these when new records are found:
yaml


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
Add a reset script:
yaml


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
Limitations
The integration retrieves data from the past 24 hours only
Update interval should be kept reasonable (30+ minutes recommended) to avoid excessive API calls
Country determination is based on callsign prefixes and may not be 100% accurate
Troubleshooting
If you experience issues:
Check your Home Assistant logs for error messages
Verify your callsign is entered correctly
Confirm your internet connection is working
Try increasing the update interval if you see connection timeouts
Additional Resources
WSPR.live Website
WSPR Information
Home Assistant Documentation
License
This integration is available under the MIT license. Feel free to modify and distribute according to your needs.
