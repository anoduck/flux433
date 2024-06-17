#!/usr/bine/env python3
# -*- coding: utf-8 -*-
# MIT License = 'Copyright (c) 2024 Anoduck'
# This software is released under the MIT License.
# https: //opensource.org/licenses/MIT
from subprocess import Popen
from flux import FluxFile
from time import sleep
import os
import sys

class Run_RTL_433:
    
    def run(self, config, path, log):
        self.log = log
        self.log.info('Running rtl_433')
        process = Popen(["rtl_433", "-c", "rtl_433.conf"], stdout=sys.stdout, stderr=sys.stderr)
        while process.poll() is None:
            dir_list = os.listdir(path[0])
            if len(dir_list) >= 1:
                path_list = []
                for file in dir_list:
                    if file.endswith(".json"):
                        path_list.append(os.path.join(path, file))
                if len(path_list) >= 1:
                    FF = FluxFile()
                    FF.load_files(config, path=path_list, watch=False, remove=True, log=self.log)
            self.log.info('Waiting for files')
            sleep(30)
            

