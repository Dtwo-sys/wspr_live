type: markdown
content: >+
  # WSPR Distance Records 📡


  ### 🏆 All-Time Records

  | Type | Station | Distance |

  |:----:|:-------:|:---------:|

  | 📥 RX | {{ states('input_text.wspr_rx_record_callsign') or 'None' }} | {% if
  states('input_number.wspr_rx_record_distance') | float > 0 %}{{
  (states('input_number.wspr_rx_record_distance') | float * 0.621371) | round(0)
  }} mi ({{ states('input_number.wspr_rx_record_distance') }} km){% else %}No
  record{% endif %} |

  | 📤 TX | {{ states('input_text.wspr_tx_record_callsign') or 'None' }} | {% if
  states('input_number.wspr_tx_record_distance') | float > 0 %}{{
  (states('input_number.wspr_tx_record_distance') | float * 0.621371) | round(0)
  }} mi ({{ states('input_number.wspr_tx_record_distance') }} km){% else %}No
  record{% endif %} |


  ### 📊 Current Session

  | Type | Station | Distance |

  |:----:|:-------:|:---------:|

  | 📥 RX | {{ states('sensor.wspr_furthest_rx_callsign') }} | {% if
  states('sensor.wspr_furthest_rx_distance') != '0' %}{{
  (states('sensor.wspr_furthest_rx_distance') | float * 0.621371) | round(0) }}
  mi ({{ states('sensor.wspr_furthest_rx_distance') }} km){% else %}No spots{%
  endif %} |

  | 📤 TX | {{ states('sensor.wspr_furthest_tx_callsign') }} | {% if
  states('sensor.wspr_furthest_tx_distance') != '0' %}{{
  (states('sensor.wspr_furthest_tx_distance') | float * 0.621371) | round(0) }}
  mi ({{ states('sensor.wspr_furthest_tx_distance') }} km){% else %}No spots{%
  endif %} |


  ### 📶 Spot Counts

  | Type | Count |

  |:----:|:-----:|

  | 📥 RX | {{ states('sensor.wspr_live_rx_spots') }} spots |

  | 📤 TX | {{ states('sensor.wspr_live_tx_spots') }} spots |

