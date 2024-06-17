#!/usr/bine/env python3
# -*- coding: utf-8 -*-
# MIT License = 'Copyright (c) 2024 Anoduck'
# This software is released under the MIT License.
# https: //opensource.org/licenses/MIT
import json
from json import JSONDecodeError
import os
import sys
import chardet
from time import sleep
from random import uniform
from magic import Magic
from alive_progress import alive_it
from charset_normalizer import detect
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dicts import ParseDicts
from fields import field_dict
from sane import Sanity


class FluxFile:
    
    def __init__(self):
        self.sanity = Sanity()

    def detect_encoding(self, file):
        with open(file, 'rb') as encfile:
            detector = chardet.universaldetector.UniversalDetector()
            for line in encfile:
                detector.feed(line)
                if detector.done:
                    break
            detector.close()
        return detector.result['encoding']

    def test_mime(self, file):
        mck = Magic(mime=True)
        if 'json' in mck.from_file(file):
            return mck.from_file(file)
        else:
            return False
            
    def watch(self, path, log):
        while len(path) == 0:
            self.log.info('Waiting for files')
            sleep(30)
    
    def load_files(self, config, path, log):
        """
        Completely rewrite this shit.
        After hours of troubleshooting, it finally dawned on me,
        the python library does not follow the influxdb line protocol spec.
        """
        self.log = log
        org = config['org']
        api = config['api']
        bucket = config['bucket']
        watch = config['watch']
        if watch:
            self.watch(path, log)
        self.log.info('Client parameters: Org={}, API={}, Bucket={}'.format(org, api, bucket))
        client = InfluxDBClient(url="http://127.0.0.1:8086",
                                token=api, org=org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        for file in path:
            mime = self.test_mime(file)
            if not mime:
                continue
            else:
                self.log.info("Detected mime type: {}".format(mime))
            encoding = self.detect_encoding(file)
            file_ctime = os.stat(file).st_ctime
            file_name = os.path.basename(file)
            with open(file, 'r', encoding=encoding, errors='ignore') as f:
                contents = f.readlines()
                for line in alive_it(contents):
                    if not 'model' in line:
                        continue
                    try:
                        json_dict = json.loads(line)
                    except JSONDecodeError as e:
                        self.log.info("error {} decoding {}".format(e, f), file=sys.stderr)
                        self.log.info("Error encountered while processing: {}".format(file))
                        continue
                    test_name = json_dict.pop('model')
                    if test_name != 'name':
                        raw_name = test_name
                        model_name = self.sanity.sanitize_text(raw_name)
                    else:
                        model_name = 'unknown' + str(round(uniform(1000, 999999)))
                    time_string = json_dict.pop('time')
                    jtime = self.sanity.sanitize_time(time_string, file_ctime)
                    # --------------------------------------------------------------------
                    # Fields: are not indexed, represent data, and should be unique
                    # Tags: are indexed, represent metadata, and are not unique
                    # --------------------------------------------------------------------
                    pdict = ParseDicts()
                    fieldstr = str(f'seen=1')
                    if 'rows' in json_dict.keys():
                        row_data = json_dict.pop('rows')
                        ld_items = pdict.list_of_dicts(
                            label='row', label_data=row_data, log=self.log)
                        fieldstr += ',' + str(ld_items)
                        self.log.info(f'After rows, fieldstr is {fieldstr}')
                    if 'codes' in json_dict.keys():
                        code_data = json_dict.pop('codes')
                        cd_items = pdict.list_of_dicts(
                            label='code', label_data=code_data, log=self.log)
                        fieldstr += ',' + str(cd_items)
                        self.log.info(f'After codes, fieldstr is {fieldstr}')
                    for key, value in field_dict.items():
                        if key in json_dict:
                            value = value or (lambda x: x)
                            try:
                                value = json_dict.pop(key)
                                set_entry = str(f'{key}="{value}"')
                                fieldstr += ',' + str(set_entry)
                                self.log.info(f'After {key}, fieldstr is {fieldstr}')
                            except Exception as e:
                                value = json_dict.get(key)
                                self.log.info('error {} mapping {}'.format(e, value))
                                continue
                    tag_set = str()
                    file_name = self.sanity.sanitize_text(file_name)
                    tag_set = str(f'source="json",file="{file_name}"')
                    self.log.info(f'Tag string is: {tag_set}')
                    if len(json_dict) > 0:
                        for key, value in json_dict.items():
                            tag_entry = str(f'{key}="{value}"')
                            tag_set += ',' + str(tag_entry)
                    self.log.info(f'Tag string is: {tag_set}')
                    self.log.info(f'Field string is: {fieldstr}')
                    if len(fieldstr) == 0:
                        self.log.info('no fields to write', file=sys.stderr)
                        continue  # invalid: we have no data
                    tag_set = self.sanity.sanitize_sets(tag_set)
                    self.log.info(f'Tag string after sanitization is: {tag_set}')
                    fieldstr = self.sanity.sanitize_sets(fieldstr)
                    self.log.info(f'Field string after sanitization is: {fieldstr}')
                    # LPE = Line Protocol Entry
                    # Example:
                    # write_client.write(
                    # "my-bucket",
                    # "my-org",
                    # [
                    # "h2o_feet,location=coyote_creek water_level=2.0 2",
                    # "h2o_feet,location=coyote_creek water_level=3.0 3"
                    # ])
                    LPE = str(f'{model_name},{tag_set} {fieldstr}')
                    self.log.info(f'Record to write as LPE: {LPE}')
                    self.log.info(f'LPE type is {type(LPE)}')
                    try:
                        write_api.write(bucket=bucket, record=LPE)
                    except Exception as e:
                        self.log.info("error {} writing {}".format(
                            e, LPE), file=sys.stderr)
                        exit(1)
            if config['remove']:
                self.log.info('File removal is enabled')
                self.log.info('Removing: {}'.format(file))
                f.close()
                os.remove(file)
        if watch:
            self.watch(path, log)
        else:
            self.log.info('Processing complete')
            exit(0)
