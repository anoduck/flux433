#!/usr/bine/env python3
# -*- coding: utf-8 -*-
# MIT License = 'Copyright (c) 2024 Anoduck'
# This software is released under the MIT License.
# https: //opensource.org/licenses/MIT
import json
from time import sleep
from alive_progress import alive_it
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

class DeDupe:
    
    def __init__(self, config, log):
        self.log = log
        self.config = config
        self.api = config['api']
        self.org = config['org']
        self.bucket = config['bucket']
        self.client = InfluxDBClient(url="http://127.0.0.1:8086",
                            token=self.api, org=self.org)
        self.query_api = self.client.query_api()
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def query(self):
        all_val = str(f'from(bucket:"{self.bucket}") |> range(start: -30d)')
        self.log.info("Running query: {}".format(all_val))
        uniq = str(f'from(bucket:"{self.bucket}") |> range(start: -30d) |> unique("_value")')
        self.log.info("Running query: {}".format(uniq))
        alltables = self.query_api.query(query=all_val, org=self.org)
        uniqtables = self.query_api.query(query=uniq, org=self.org)
        fluxentries = alltables.to_json(indent=4)
        uniqentries = uniqtables.to_json(indent=4)
        fluxdata = json.loads(str(fluxentries))
        total_flux = len(fluxdata)
        self.log.debug('{}'.format(fluxdata))
        uniqdata = json.loads(str(uniqentries))
        self.log.debug('{}'.format(uniqdata))
        while True:
            for entry in alive_it(uniqdata, bar='text'):
                self.log.info(entry)
                entvalue = entry.get('_value')
                entcount = entry.get('count')
                ttot = [x for x in fluxdata if entvalue in x.values()]
                count = len(ttot)+entcount
                entry.update({'count': count})
                self.log.info(entry)
                self.write_api.write(bucket=self.bucket, record=entry)
                uniqdata.remove(entry)
                for i in ttot:
                    fluxdata.remove(i)
            sleep(3)
        