#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024  anoduck

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Much of the source code of this project was taken from:
# https://github.com/azrdev/rtl433_influx/.

from simple_parsing import parse
from dataclasses import dataclass
from alive_progress import alive_it
from configobj import ConfigObj
from configobj.validate import Validator
import uuid
import chardet
import json
from ast import literal_eval
from json.decoder import JSONDecodeError
from influxdb import InfluxDBClient
import os
import sys
from datetime import datetime


cfg = """
## Configuration file for myflux
## https://github.com/anoduck/myflux
## MIT License = 'Copyright (c) 2024 Anoduck'
## This software is released under the MIT License.
## https: //opensource.org/licenses/MIT
## ----------------------------------------------------------------------------
## Please do not leave username and password unmodified and without quotes.
## --------------------------------------------------------------------------------
## *L00k* -- WARNING: ALL VALUES MUST BE CONTAINED IN SINGLE QUOTES -- *L00k*
## --------------------------------------------------------------------------------

# user for influxdb
user = string(default='replace with influxdb user')

# passord for user with influxdb
pass = string(default='replace with influxdb password')

# influxdb database name
db = string(default='replace with db name')

# Drop entries that contain these words in the word cloud
badwords = list(default=list('opiods', 'pain', 'case', 'class', 'opiates', 'fuckers', 'assholes', 'fuck'))
"""


@dataclass
class options:
    path: str = '~/Sandbox/ISM-Research'  # Path to Dir of JSON files or Json File


Options = parse(options, dest="Options")


mappings = {
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


def detect_encoding(file): 
    with open(file, 'rb') as encfile: 
        detector = chardet.universaldetector.UniversalDetector() 
        for line in encfile: 
            detector.feed(line) 
            if detector.done: 
                break
        detector.close() 
    return detector.result['encoding'] 


def sanitize(raw_name):
    text = str(raw_name)
    model_name = text.replace("-", "_").replace(" ", "_").replace("/", "_").replace(".", "_").replace("&", "")
    return model_name

def load_files(config, path):
    client = InfluxDBClient('localhost', 8086, config['user'], config['pass'], config['db'])
    for file in path:
        encoding = detect_encoding(file)
        with open(file, 'r', encoding=encoding, errors='ignore') as f:
            contents = f.readlines()
            for line in alive_it(contents):
                if not 'model' in line:
                    continue
                try:
                    json_dict = json.loads(line)
                except JSONDecodeError as e:
                    print("error {} decoding {}".format(e, f), file=sys.stderr)
                    print("Error encountered while processing: {}".format(file))
                    continue
                test_name = json_dict.get('model')
                print(type(test_name))
                if test_name != 'name':
                    raw_name = test_name
                else:
                    raw_name = uuid.uuid4()
                model_name = sanitize(raw_name)
                print(model_name)
                print(type(model_name))
                mtime = json_dict.get('time')
                stptime = mtime.strip("@").strip("'").strip("s")
                nstime = literal_eval(stptime)
                unixtime = nstime * 10**10
                date_time = datetime.fromtimestamp(unixtime)
                jtime = date_time.isoformat()
                print(jtime)
                json_out = {
                        'measurement': model_name,
                        'time': str(jtime), # TODO: timezone?
                        'tags': {},
                        'fields': {},
                }
                for n, mapping in mappings.items():
                    if n in json_dict:
                        mapping = mapping or (lambda x : x)
                        try:
                            value = json_dict.get(n)
                            json_out['fields'][n] = mapping(value)
                        except Exception as e:
                            value = json_dict.get(n)
                            print('error {} mapping {}'.format(e, value))
                            continue
                        json_out['tags'] = json_dict # the remainder

                        if not len(json_out['fields']):
                            continue # invalid: we have no data #TODO: notify about error

                        try:
                            client.write_points([json_out])
                        except Exception as e:
                            print("error {} writing {}".format(e, json_out), file=sys.stderr)


def pathfinder(path):
    pathlist = []
    if os.path.isfile(path):
        pathlist.append(os.path.abspath(path))
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith('.json'):
                    pathlist.append(os.path.join(root, name))
    return pathlist


def main():
    conf_file = "config.ini"
    conf_path = os.path.realpath(conf_file)
    config = ConfigObj()
    spec = cfg.split("\n")
    if not os.path.isfile(conf_file):
        config = ConfigObj(conf_file, configspec=spec)
        config.filename = conf_file
        vader = Validator()
        config.validate(vader, copy=True)
        config.write()
        print("Configuration file written to " + conf_path)
        sys.exit()
    else:
        config = ConfigObj(conf_file, configspec=spec)
    path = pathfinder(Options.path)
    load_files(config, path)


if __name__ == '__main__':
    main()
