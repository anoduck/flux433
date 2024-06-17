#!/usr/bine/env python3
# -*- coding: utf-8 -*-
# MIT License = 'Copyright (c) 2024 Anoduck'
# This software is released under the MIT License.
# https: //opensource.org/licenses/MIT

field_dict = {
        'maybetemp': None,
        'temperature': None,
        'temperature_C': None,
        'temperature_C1': None,
        'temperature_C2': None,
        'temperature_2_C': None,
        'temperature_1_C': None,
        'temperature_F': None,
        'ptemperature_C': None,

        'pressure_bar': None,
        'pressure_hPa': None,
        'pressure_PSI': None,

        'humidity': None,
        'phumidity': None,
        'moisture': None,

        'windstrength': None,
        'gust': None,
        'average': None,
        'speed': None,
        'wind_gust': None,
        'wind_speed': None,

        'winddirection': None,
        'direction': None,
        'wind_direction': None,
        'wind_dir_deg': None,
        'wind_dir': None,

        'battery': None,
        'battery_mV': None,

        'rain': None,
        'rain_rate': None,
        'total_rain': None,
        'rain_total': None,
        'rainfall_accumulation': None,
        'raincounter_raw': None,

        'status': None,
        'state': None,
        'tristate': str,
        'button1': None,
        'button2': None,
        'button3': None,
        'button4': None,
        'flags': lambda x: int(str(x), base=16),
        'event': lambda x: int(str(x), base=16),
        'cmd': None,
        'cmd_id': None,
        'code': None,
        'num_rows': None,
        'unit': None,
        'id': None,
        'learn': None,
        'power0': None,
        'power1': None,
        'power2': None,
        'dim_value': None,
        'depth': None,
        'depth_cm': None,
        'energy': None,
        'len': None,
        'data': None,
        'repeat': None,
        'current': None,
        'interval': None,

        'heating': None,
        'heating_temp': None,
        'water': None,
}