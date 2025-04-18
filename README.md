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
