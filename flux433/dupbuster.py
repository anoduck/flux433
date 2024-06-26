#!/usr/bine/env python3
# -*- coding: utf-8 -*-
# MIT License = 'Copyright (c) 2024 Anoduck'
# This software is released under the MIT License.
# https: //opensource.org/licenses/MIT
import sys
import warnings
import pandas as pd
from rich_dataframe import prettify
from rich.console import Console
from alive_progress import alive_it
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.delete_api import DeleteApi

warnings.simplefilter(action='ignore', category=FutureWarning)


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
        self.delete = DeleteApi(self.client).delete

    def quoted_strings_can_suckit(self, le_bastard, de_type=int):
        self.log.info(f'Le Bastard is of type: {type(le_bastard)}')
        le_bastard = int(le_bastard.replace('"', ''))
        if isinstance(le_bastard, de_type):
            return le_bastard
        else:
            self.log.error(f'Le Bastard is not an int: {le_bastard}')
            sys.exit(1)

    def write_bucket(self, qdf):
        self.log.info("Writing bucket")
        # self.delete(bucket=self.bucket, start='-30d', st\op='now()', predicate='(r) => r._measurement =~ /^unknown.*/')
        self.write_api.write(bucket=self.bucket, record=qdf,
                             data_frame_measurement_name='_measurement',
                             data_frame_tag_columns=['start', 'stop', 'count', 'file', 'source'],
                             data_frame_field_columns=['code', 'data', 'len', 'num_rows']
                             )
        return True
   
    def query(self):
        all_val = str(f'''from(bucket:"{self.bucket}")|> range(start: -30d, stop: now())
                      |> filter(fn: (r) => r._measurement =~ /^unknown.*/) 
                      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
                      |> limit(n: 109)''')  #<-- Remove this when testing is completed!
        self.log.info("Running query: {}".format(all_val))
        qdf_list = self.query_api.query_data_frame(query=all_val, org=self.org, data_frame_index=['table'])
        new_list = []
        for df in alive_it(qdf_list):
            self.log.debug('Columns pre processing: {}'.format(df.columns.to_list()))
            cnt_int = {'count': 1}
            df = df.fillna(cnt_int)
            # ['result', '_start', '_stop', '_time', '_measurement', 'count', 'file', 'source', 'code', 'data', 'len', 'num_rows', 'seen']
            df.rename(mapper={'result':'result', '_start':'start', '_stop':'stop', '_time':'time', '_measurement':'measurement',
                              'count':'count', 'file':'file', 'source':'source', 'code':'code', 'data':'data', 'len':'len',
                              'num_rows':'num_rows', '\'row_id':'row_id'}, axis=1, inplace=True)
            #https://stackoverflow.com/questions/49791246/drop-columns-with-more-than-60-percent-of-empty-values-in-pandas
            df = df.loc[:, (df.isin([' ','NULL',0]) | df.isnull()).mean() <= .6]
            self.log.debug('Columns post processing: {}'.format(df.columns.to_list()))
            new_list.append(df)
        qdf = pd.concat(new_list)
        qdf = qdf.drop(["['row_id", 'count'], axis=1)
        qdf = qdf.groupby(qdf.columns.tolist()).size().reset_index().rename(columns={0:'count'})
        qdf = qdf.drop_duplicates(subset=['code', 'data', 'len'], keep='first', inplace=False)
        col_list = qdf.columns.to_list()
        col_len = len(col_list)
        table = prettify(qdf, row_limit=5, first_rows=True, col_limit=col_len)
        console = Console()
        console.print(col_list)
        console.print(table)
        self.write_bucket(qdf)
        self.log.info("Done!")