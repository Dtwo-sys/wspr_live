import logging
import requests
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

WSPR_LIVE_URL = "https://db1.wspr.live/?query={query}"

TX_QUERY = (
    "SELECT time, tx_sign, rx_sign, band, snr, distance "
    "FROM wspr.rx "
    "WHERE tx_sign = '{callsign}' AND time >= now() - INTERVAL 1 DAY "
    "ORDER BY time DESC LIMIT 100 FORMAT JSON"
)

RX_QUERY = (
    "SELECT time, tx_sign, rx_sign, band, snr, distance "
    "FROM wspr.rx "
    "WHERE rx_sign = '{callsign}' AND time >= now() - INTERVAL 1 DAY "
    "ORDER BY time DESC LIMIT 100 FORMAT JSON"
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    callsign = config.get("callsign", "G0IKV").upper()
    interval_minutes = config.get("interval", 60)
    add_entities([
        WSPRLiveSensor(callsign, "tx", interval_minutes),
        WSPRLiveSensor(callsign, "rx", interval_minutes)
    ])

class WSPRLiveSensor(Entity):
    def __init__(self, callsign, mode, interval_minutes):
        self._callsign = callsign
        self._mode = mode
        self._state = None
        self._attributes = {}
        self._name = f"WSPR Live {mode.upper()} Spots"
        self._interval = timedelta(minutes=interval_minutes)
        self._last_updated = datetime.min

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    @property
    def should_poll(self):
        return True

    def update(self):
        if datetime.utcnow() - self._last_updated < self._interval:
            return

        _LOGGER.debug("Updating WSPR Live %s spots for %s", self._mode.upper(), self._callsign)
        try:
            if self._mode == "tx":
                query = TX_QUERY.format(callsign=self._callsign)
            else:
                query = RX_QUERY.format(callsign=self._callsign)

            full_url = WSPR_LIVE_URL.format(query=requests.utils.quote(query))
            response = requests.get(full_url, timeout=20)
            response.raise_for_status()
            data = response.json()
            spots = []

            for entry in data.get("data", []):
                spots.append({
                    "tx": entry.get("tx_sign"),
                    "rx": entry.get("rx_sign"),
                    "band": entry.get("band"),
                    "snr": entry.get("snr"),
                    "distance": entry.get("distance"),
                    "time": entry.get("time")
                })

            self._state = len(spots)
            self._attributes = {
                "spots": spots,
                "updated": datetime.utcnow().isoformat()
            }
            self._last_updated = datetime.utcnow()
            _LOGGER.debug("%s updated with %d spots", self._name, self._state)

        except Exception as e:
            _LOGGER.error("Failed to fetch WSPR.live data: %s", e)
            self._state = "error"
            self._attributes = {}