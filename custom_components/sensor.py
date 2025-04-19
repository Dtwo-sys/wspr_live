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

# Band map for converting MHz to band labels
BAND_MAP = {
    1.8: "160M",
    3.5: "80M",
    5.3: "60M",
    7.0: "40M",
    10.1: "30M",
    14.0: "20M",
    18.1: "17M",
    21.0: "15M",
    24.9: "12M",
    28.0: "10M",
    50.0: "6M",
    70.0: "4M",
    144.0: "2M"
}

def determine_band_label(band_mhz):
    """Convert band frequency to band label."""
    if not band_mhz:
        return ""
    
    # Try to find an exact match
    if band_mhz in BAND_MAP:
        return BAND_MAP[band_mhz]
    
    # Try to find the closest match
    band_float = float(band_mhz)
    for band, label in BAND_MAP.items():
        if abs(band_float - band) < 0.5:  # Close enough
            return label
    
    # Default to frequency + m
    return f"{band_mhz}m"

def determine_country(callsign):
    """Determine the country based on callsign prefix."""
    if not callsign:
        return "Unknown"
    
    callsign = callsign.upper()
    
    # Special case for 1-character prefixes
    if len(callsign) < 2:
        return "Unknown"
    
    # Prefix detection by first digit/letter combination
    first_two = callsign[:2]
    first_three = callsign[:3] if len(callsign) >= 3 else ""
    first_four = callsign[:4] if len(callsign) >= 4 else ""
    first_char = callsign[0]
    second_char = callsign[1] if len(callsign) >= 2 else ""
    third_char = callsign[2] if len(callsign) >= 3 else ""
    
    # Special case: callsigns with /
    if "/" in callsign:
        parts = callsign.split("/")
        base_call = parts[0]
        # For callsigns like TA4/G8SCU, use the first part
        return determine_country(base_call)
    
    # 1 character + digit callsigns
    # Spratly Islands
    if first_two == "1S":
        return "Spratly Islands"
    
    # United Kingdom & territories (2-prefixes)
    if first_char == "2":
        if second_char == "D":
            return "Isle of Man"
        elif second_char == "E":
            return "England"
        elif second_char == "I":
            return "Northern Ireland"
        elif second_char == "J":
            return "Jersey"
        elif second_char == "M" or second_char == "S":
            return "Scotland"
        elif second_char == "U":
            return "Guernsey"
        elif second_char == "W":
            return "Wales"
    
    # 3-prefixes
    if first_char == "3":
        if second_char == "A":
            return "Monaco"
        elif first_two == "3B" and third_char == "8":
            return "Mauritius"
        elif first_two == "3B" and third_char == "9":
            return "Rodriguez Island"
        elif second_char in ["E", "F"]:
            return "Panama"
        elif second_char == "G":
            return "Chile"
        elif second_char in ["H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U"]:
            return "China"
        elif second_char == "W":
            return "Vietnam"
        elif second_char == "Z":
            return "Poland"
    
    # 4-prefixes
    if first_char == "4":
        if second_char in ["A", "B", "C"]:
            return "Mexico"
        elif second_char in ["D", "E", "F", "G", "H", "I"]:
            return "Philippines"
        elif second_char in ["J", "K"]:
            return "Azerbaijan"
        elif second_char == "L":
            return "Georgia"
        elif second_char == "M":
            return "Venezuela"
        elif second_char == "O":
            return "Montenegro"
        elif second_char in ["P", "Q", "R", "S"]:
            return "Sri Lanka"
        elif second_char == "T":
            return "Peru"
        elif second_char == "V":
            return "Haiti"
        elif second_char in ["X", "Z"]:
            return "Israel"
    
    # 5-prefixes
    if first_char == "5":
        if second_char == "A":
            return "Libya"
        elif second_char == "B":
            return "Cyprus"
        elif second_char in ["C", "D", "E", "F", "G"]:
            return "Morocco"
        elif second_char in ["H", "I"]:
            return "Tanzania"
        elif second_char in ["J", "K"]:
            return "Colombia"
        elif second_char == "N":
            return "Nigeria"
        elif second_char in ["P", "Q"]:
            return "Denmark"
        elif second_char == "R":
            return "Madagascar"
        elif second_char == "U":
            return "Niger"
        elif second_char == "V":
            return "Togo"
        elif second_char == "X":
            return "Uganda"
        elif second_char == "Z":
            return "Kenya"
    
    # 6-prefixes
    if first_char == "6":
        if second_char in ["A", "B"]:
            return "Egypt"
        elif second_char == "C":
            return "Syria"
        elif second_char in ["D", "E", "F", "G", "H", "I", "J"]:
            return "Mexico"
        elif second_char in ["K", "L", "M", "N"]:
            return "South Korea"
        elif second_char in ["P", "Q", "R", "S"]:
            return "Pakistan"
        elif second_char == "W":
            return "Senegal"
        elif second_char == "Y":
            return "Jamaica"
    
    # 7-prefixes
    if first_char == "7":
        if second_char in ["A", "B", "C", "D", "G", "H", "I"]:
            return "Indonesia"
        elif second_char in ["J", "K", "L", "M", "N"]:
            return "Japan"
        elif second_char == "O":
            return "Yemen"
        elif second_char == "P":
            return "Lesotho"
        elif second_char == "Q":
            return "Malawi"
        elif second_char == "S":
            return "Sweden"
        elif second_char == "X":
            return "Algeria"
        elif second_char == "Z":
            return "Saudi Arabia"
    
    # 8-prefixes
    if first_char == "8":
        if second_char in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
            return "Indonesia"
        elif second_char in ["J", "K", "L", "M", "N"]:
            return "Japan"
        elif second_char == "P":
            return "Barbados"
        elif second_char == "Q":
            return "Maldives"
        elif second_char == "R":
            return "Guyana"
        elif second_char == "S":
            return "Sweden"
        elif second_char == "Z":
            return "Saudi Arabia"
    
    # 9-prefixes
    if first_char == "9":
        if second_char == "A":
            return "Croatia"
        elif second_char == "D":
            return "Iran"
        elif second_char == "G":
            return "Ghana"
        elif second_char == "H":
            return "Malta"
        elif second_char == "J":
            return "Zambia"
        elif second_char == "K":
            return "Kuwait"
        elif second_char == "L":
            return "Sierra Leone"
        elif first_two == "9M":
            if third_char == "0":
                return "Spratly Islands"
            elif third_char in ["2", "4"]:
                return "West Malaysia"
            elif third_char in ["6", "8"]:
                return "East Malaysia"
            return "Malaysia"  # Generic fallback
        elif second_char == "N":
            return "Nepal"
        elif second_char == "Q":
            return "Democratic Republic of the Congo"
        elif second_char == "U":
            return "Burundi"
        elif second_char == "V":
            if third_char == "1":
                return "Singapore"
            return "Singapore"
        elif second_char == "X":
            return "Rwanda"
    
    # A-prefixes
    if first_char == "A":
        if second_char == "4":
            return "Oman"
        elif second_char == "5":
            return "Bhutan"
        elif second_char == "6":
            return "United Arab Emirates"
        elif second_char == "7":
            return "Qatar"
        elif second_char == "8":
            return "Liberia"
        elif second_char == "9":
            return "Bahrain"
        elif second_char in ["M", "N", "O"]:
            return "Spain"
        elif second_char in ["P", "Q", "R"]:
            return "Pakistan"
        elif second_char == "T":
            return "India"
        elif second_char in ["Y", "Z"]:
            return "Argentina"
    
    # B-prefixes
    if first_char == "B":
        if second_char in ["A", "D", "G", "T", "Y", "Z"]:
            return "China"
        elif second_char == "O":
            return "Taiwan (Quemoy Matsu)"
        elif first_two == "BS" and third_char == "7":
            return "Scarborough Reef"
        elif second_char in ["V", "X"]:
            return "Taiwan"
        elif first_three == "BV9" and first_four == "BV9P":
            return "Pratas Island"
        elif first_three == "BV9" and first_four == "BV9S":
            return "Spratly Islands"
    
    # C-prefixes
    if first_char == "C":
        if second_char == "4":
            return "Cyprus"
        elif second_char == "5":
            return "Gambia"
        elif second_char == "6":
            return "Bahamas"
        elif second_char in ["8", "9"]:
            return "Mozambique"
        elif second_char in ["A", "B", "C", "D", "E"]:
            if first_four == "CE0A":
                return "Easter Island"
            elif first_four == "CE0X":
                return "San Felix"
            elif first_four == "CE0Z":
                return "Juan Fernandez Is."
            else:
                return "Chile"
        elif second_char in ["F", "G", "H", "I", "J", "K", "Y", "Z"]:
            return "Canada"
        elif second_char in ["L", "M", "O"]:
            return "Cuba"
        elif second_char == "N":
            return "Morocco"
        elif second_char == "P":
            return "Bolivia"
        elif second_char in ["Q", "R", "S", "T"]:
            if third_char == "3" or first_three == "CT9":
                return "Madeira"
            else:
                return "Portugal"
        elif second_char == "U":
            return "Azores"
        elif second_char in ["V", "W", "X"]:
            return "Uruguay"
    
    # D-prefixes
    if first_char == "D":
        if second_char in ["2", "3"]:
            return "Angola"
        elif second_char == "4":
            return "Cape Verde"
        elif second_char == "6":
            return "Comoros"
        elif second_char in ["7", "8", "9", "S", "T"]:
            return "South Korea"
        elif second_char in ["A", "B", "C", "D", "F", "G", "H", "J", "K", "L", "M", "N", "O", "P", "Q", "R"]:
            return "Germany"
        elif second_char == "U":
            return "Philippines"
    
    # E-prefixes
    if first_char == "E":
        if second_char == "2":
            return "Thailand"
        elif second_char == "3":
            return "Eritrea"
        elif second_char in ["A", "B", "C", "D", "E", "F", "G", "H"]:
            if third_char == "6":
                return "Balearic Islands"
            elif third_char == "8":
                return "Canary Islands"
            elif third_char == "9":
                return "Ceuta and Melilla"
            else:
                return "Spain"
        elif second_char in ["I", "J"]:
            return "Ireland"
        elif second_char == "K":
            return "Armenia"
        elif second_char == "L":
            return "Liberia"
        elif second_char in ["M", "N", "O"]:
            return "Ukraine"
        elif second_char == "P":
            return "Iran"
        elif second_char == "R":
            return "Moldova"
        elif second_char == "S":
            return "Estonia"
        elif second_char == "T":
            return "Ethiopia"
        elif second_char in ["U", "V", "W"]:
            return "Belarus"
        elif second_char == "X":
            return "Kyrgyzstan"
        elif second_char == "Y":
            return "Tajikistan"
        elif second_char == "Z":
            return "Turkmenistan"
    
    # F-prefixes
    if first_char == "F":
        if second_char == "G":
            return "Guadeloupe"
        elif second_char == "M":
            return "Martinique"
        elif second_char == "S":
            return "Saint Martin"
        elif second_char == "Y":
            return "French Guiana"
        else:
            return "France"
    
    # G-prefixes
    if first_char == "G":
        if second_char == "C":
            return "Wales"
        elif second_char == "D":
            return "Isle of Man"
        elif second_char in ["H", "J"]:
            return "Jersey"
        elif second_char == "I":
            return "Northern Ireland"
        elif second_char == "M":
            return "Scotland"
        elif second_char == "N":
            return "Northern Ireland"
        elif second_char == "P":
            return "Guernsey"
        elif second_char == "S":
            return "Scotland"
        elif second_char == "T":
            return "Isle of Man"
        elif second_char == "U":
            return "Guernsey"
        elif second_char == "W":
            return "Wales"
        else:
            return "United Kingdom"
    
    # H-prefixes
    if first_char == "H":
        if second_char == "2":
            return "Cyprus"
        elif second_char == "3":
            return "Panama"
        elif second_char in ["6", "7"]:
            return "Nicaragua"
        elif second_char in ["8", "9", "O", "P"]:
            return "Panama"
        elif second_char == "A":
            return "Hungary"
        elif second_char == "B":
            if third_char == "0":
                return "Liechtenstein"
            else:
                return "Switzerland"
        elif second_char in ["C", "D"]:
            return "Ecuador"
        elif second_char == "E":
            if third_char == "0":
                return "Liechtenstein"
            else:
                return "Switzerland"
        elif second_char == "F":
            return "Poland"
        elif second_char == "G":
            return "Hungary"
        elif second_char == "H":
            return "Haiti"
        elif second_char == "I":
            return "Dominican Republic"
        elif second_char == "K":
            return "Colombia"
        elif second_char == "L":
            return "South Korea"
        elif second_char == "N":
            return "Iraq"
        elif second_char == "Q":
            return "Honduras"
        elif second_char == "R":
            return "Honduras"
        elif second_char == "S":
            return "Thailand"
        elif second_char == "U":
            return "El Salvador"
        elif second_char == "V":
            return "Vatican City"
        elif second_char == "Z":
            return "Saudi Arabia"
    
    # I-prefixes
    if first_char == "I":
        if first_three == "IM0" or first_three == "IS0":
            return "Sardinia"
        elif first_three == "IT9":
            return "Sicily"
        elif first_two in ["IK", "IN", "IW", "IZ"]:
            return "Italy"
        else:
            return "Italy"
    
    # J-prefixes
    if first_char == "J":
        if second_char == "2" or first_three == "J28":
            return "Djibouti"
        elif second_char == "3":
            return "Grenada"
        elif second_char == "4":
            if third_char == "5":
                return "Dodecanese"
            elif third_char == "9":
                return "Crete"
            else:
                return "Greece"
        elif second_char == "6":
            return "St. Lucia"
        elif second_char == "7":
            return "Dominica"
        elif second_char == "8":
            return "St. Vincent and the Grenadines"
        elif second_char in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S"]:
            if first_three == "JD1" and len(callsign) >= 5 and callsign[3:5] == "/M":
                return "Minami Torishima"
            elif first_three == "JD1" and len(callsign) >= 5 and callsign[3:5] == "/O":
                return "Ogasawara"
            else:
                return "Japan"
        elif second_char in ["T", "U", "V"]:
            return "Mongolia"
        elif second_char == "W":
            return "Svalbard"
        elif second_char == "X":
            return "Jan Mayen"
        elif second_char == "Y":
            return "Jordan"
    
    # K-prefixes
    if first_char == "K":
        # K is for USA, but there are special regions
        if first_two == "KH":
            if third_char == "0":
                return "Mariana Islands (USA)"
            elif third_char == "1":
                return "Baker & Howland Islands (USA)"
            elif third_char == "2":
                return "Guam (USA)"
            elif third_char == "3":
                return "Johnston Island (USA)"
            elif third_char == "4":
                return "Midway Island (USA)"
            elif third_char == "5":
                return "Palmyra & Jarvis Islands (USA)"
            elif third_char in ["6", "7"]:
                return "Hawaii (USA)"
            elif third_char == "8":
                return "American Samoa (USA)"
            elif third_char == "9":
                return "Wake Island (USA)"
            return "USA"  # Fallback for other KH
        elif first_two == "KL":
            return "Alaska (USA)"
        elif first_two == "KP":
            if third_char == "1":
                return "Navassa Island (USA)"
            elif third_char == "2":
                return "US Virgin Islands"
            elif third_char in ["3", "4"]:
                return "Puerto Rico"
            elif third_char == "5":
                return "Desecheo Island (USA)"
            return "USA"  # Fallback for other KP
        
        # Default K prefix is USA
        return "USA"
    
    # L-prefixes
    if first_char == "L":
        if second_char in ["2", "3", "4", "5", "6", "7", "8", "9", "U"]:
            return "Argentina"
        elif second_char in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N"]:
            return "Norway"
        elif second_char == "X":
            return "Luxembourg"
        elif second_char == "Y":
            return "Lithuania"
        elif second_char == "Z":
            return "Bulgaria"
    
    # M-prefix is United Kingdom
    if first_char == "M":
        return "United Kingdom"
    
    # N-prefix is USA
    if first_char == "N":
        return "USA"
    
    # O-prefixes
    if first_char == "O":
        if second_char in ["A", "B", "C"]:
            return "Peru"
        elif second_char == "D":
            return "Lebanon"
        elif second_char == "E":
            return "Austria"
        elif second_char in ["F", "G", "H", "I", "J"]:
            return "Finland"
        elif second_char in ["K", "L"]:
            return "Czech Republic"
        elif second_char == "M":
            return "Slovak Republic"
        elif second_char == "N":
            return "Belgium"
        elif second_char in ["O", "P", "Q", "R", "S", "T"]:
            return "Belgium"
        elif second_char in ["U", "V", "W"]:
            return "Denmark"
        elif second_char == "Y":
            return "Faroe Islands"
        elif second_char == "Z":
            return "Denmark"
    
    # P-prefixes
    if first_char == "P":
        if second_char == "3":
            return "Cyprus"
        elif second_char == "5":
            return "North Korea"
        elif second_char in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
            return "Netherlands"
        elif second_char in ["P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y"]:
            return "Brazil"
        elif second_char == "Z":
            return "Suriname"
    
    # R-prefixes (Russia)
    if first_char == "R":
        if first_two in ["R0", "R8", "R9"]:
            return "Russia (Asiatic part)"
        elif first_four == "R1FJ":
            return "Franz Josef Land"
        elif first_two == "RA":
            if third_char in ["0", "9"]:
                return "Russia (Asiatic part)"
            else:
                return "Russia (European part)"
        elif first_three == "RC0":
            return "Russia (Asiatic part)"
        elif first_two == "RK":
            if third_char in ["0", "9"]:
                return "Russia (Asiatic part)"
            else:
                return "Russia (European part)"
        elif first_two == "RN":
            return "Russia (European part)"
        elif first_two in ["RU", "RV", "RZ"]:
            return "Russia (European part)"
        elif first_two == "RW":
            if third_char == "0":
                return "Russia (Asiatic part)"
            else:
                return "Russia (European part)"
        else:
            return "Russia (European part)"
    
    # S-prefixes
    if first_char == "S":
        if second_char == "2":
            return "Bangladesh"
        elif second_char == "5":
            return "Slovenia"
        elif second_char == "7":
            return "Seychelles"
        elif second_char == "9":
            return "Sao Tome and Principe"
        elif second_char in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]:
            return "Sweden"
        elif second_char in ["N", "O", "P", "Q", "R"]:
            return "Poland"
        elif second_char == "T":
            if third_char == "0":
                return "South Sudan"
            else:
                return "Sudan"
        elif second_char == "U":
            return "Egypt"
        elif second_char in ["V", "W", "X", "Z"]:
            if third_char == "5":
                return "Dodecanese"
            elif third_char == "9":
                return "Crete"
            else:
                return "Greece"
    
    # T-prefixes
    if first_char == "T":
        if second_char == "3":
            return "Cuba"
        elif second_char == "6":
            return "Afghanistan"
        elif second_char in ["A", "B", "C"]:
            return "Turkey"
        elif second_char == "D":
            return "Guatemala"
        elif second_char == "E":
            return "Costa Rica"
        elif second_char == "F":
            return "Iceland"
        elif second_char == "G":
            return "Guatemala"
        elif second_char == "I":
            return "Costa Rica"
        elif second_char == "J":
            return "Cameroon"
        elif second_char == "K":
            return "Corsica"
        elif second_char == "L":
            return "Central African Republic"
        elif second_char == "N":
            return "Congo"
        elif second_char == "R":
            return "Gabon"
        elif second_char == "T":
            return "Chad"
        elif second_char == "U":
            return "Ivory Coast"
        elif second_char == "Y":
            return "Benin"
        elif second_char == "Z":
            return "Mali"
    
    # U-prefixes
    if first_char == "U":
        if second_char == "A":
            if third_char == "0":
                return "Russia (Asiatic part)"
            elif third_char == "2":
                return "Kaliningrad"
            elif third_char in ["3", "4", "5", "6"]:
                return "Russia (European part)"
            elif third_char == "9":
                return "Russia (Asiatic part)"
            else:
                return "Russia (European part)"
        elif first_two == "UB" and third_char == "0":
            return "Russia (Asiatic part)"
        elif second_char in ["J", "K"]:
            return "Uzbekistan"
        elif second_char in ["N", "P", "Q"]:
            return "Kazakhstan"
        elif second_char in ["R", "T", "U", "V", "W", "X", "Y", "Z"]:
            return "Ukraine"
    
    # V-prefixes
    if first_char == "V":
        if second_char == "2":
            return "Antigua and Barbuda"
        elif second_char == "3":
            return "Belize"
        elif second_char == "4":
            return "St. Kitts and Nevis"
        elif second_char == "5":
            return "Namibia"
        elif second_char == "8":
            return "Brunei"
        elif second_char in ["A", "E", "O", "Y"]:
            return "Canada"
        elif first_two == "VK" or first_two == "VL" or first_two == "AX":
            return "Australia"
        elif first_four == "VP2E":
            return "Anguilla"
        elif first_four == "VP2M":
            return "Montserrat"
        elif first_four == "VP2V":
            return "British Virgin Islands"
        elif second_char == "R" or first_three == "VR2":
            return "Hong Kong"
        elif second_char == "U":
            if first_three == "VU4":
                return "Andaman & Nicobar Islands"
            elif first_three == "VU7":
                return "Laccadive Islands"
            else:
                return "India"
    
    # W-prefix is USA
    if first_char == "W":
        return "USA"
    
    # X-prefixes
    if first_char == "X":
        if second_char in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
            return "Mexico"
        elif second_char == "P":
            return "Denmark"
        elif second_char in ["Q", "R"]:
            return "Chile"
        elif second_char == "S":
            return "China"
        elif second_char == "U":
            return "Cambodia"
        elif second_char == "V":
            return "Vietnam"
        elif second_char == "W":
            return "Laos"
        elif first_three == "XX9":
            return "Macau"
        elif second_char in ["Y", "Z"]:
            return "Myanmar"
    
    # Y-prefixes
    if first_char == "Y":
        if second_char == "A":
            return "Afghanistan"
        elif second_char in ["B", "C", "D", "E", "F", "G", "H"]:
            return "Indonesia"
        elif second_char == "I":
            return "Iraq"
        elif second_char == "K":
            return "Syria"
        elif second_char == "L":
            return "Latvia"
        elif second_char == "M":
            return "Turkey"
        elif second_char == "N":
            return "Nicaragua"
        elif second_char in ["O", "P", "Q", "R"]:
            return "Romania"
        elif second_char == "S":
            return "El Salvador"
        elif second_char in ["T", "U"]:
            return "Serbia"
        elif second_char in ["V", "W", "X", "Y"]:
            return "Venezuela"
    
    # Z-prefixes
    if first_char == "Z":
        if second_char == "2":
            return "Zimbabwe"
        elif second_char == "3":
            return "North Macedonia"
        elif second_char == "A":
            return "Albania"
        elif first_three == "ZB2":
            return "Gibraltar"
        elif first_three == "ZD7":
            return "St. Helena"
        elif first_three == "ZD8":
            return "Ascension Island"
        elif first_three == "ZD9":
            return "Tristan da Cunha & Gough Island"
        elif second_char == "L" or second_char == "M":
            return "New Zealand"
        elif second_char == "P":
            return "Paraguay"
        elif second_char in ["R", "S", "T", "U"]:
            return "South Africa"
        elif second_char in ["V", "W", "X", "Y", "Z"]:
            return "Brazil"
    
    return "Unknown"

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the WSPR.live sensor platform."""
    callsign = config.get("callsign", "G0IKV").upper()
    interval_minutes = config.get("interval", 60)
    add_entities([
        WSPRLiveSensor(callsign, "tx", interval_minutes),
        WSPRLiveSensor(callsign, "rx", interval_minutes)
    ])

class WSPRLiveSensor(Entity):
    """Representation of a WSPR.live sensor."""

    def __init__(self, callsign, mode, interval_minutes):
        """Initialize the sensor."""
        self._callsign = callsign
        self._mode = mode
        self._state = None
        self._attributes = {}
        self._name = f"WSPR Live {mode.upper()} Spots"
        self._interval = timedelta(minutes=interval_minutes)
        self._last_updated = datetime.min

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def should_poll(self):
        """Polling is required."""
        return True

    def update(self):
        """Fetch new state data for the sensor."""
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
                tx_sign = entry.get("tx_sign")
                rx_sign = entry.get("rx_sign")
                band_mhz = entry.get("band")
                
                # For TX spots, get the country of the receiver
                # For RX spots, get the country of the transmitter
                relevant_callsign = rx_sign if self._mode == "tx" else tx_sign
                country = determine_country(relevant_callsign)
                
                # Get band label
                band_label = determine_band_label(band_mhz)
                
                spots.append({
                    "tx": tx_sign,
                    "rx": rx_sign,
                    "band": band_mhz,
                    "band_label": band_label,  # Add the band label
                    "snr": entry.get("snr"),
                    "distance": entry.get("distance"),
                    "time": entry.get("time"),
                    "country": country
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
