#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024  anoduck, The Anonymous Duck

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
# --------------------------------------------------------------------------
# Much of / a bountiful proportionment / a lot / a whole butt load 
#       of the source code of this project was taken from:
#           https://github.com/azrdev/rtl433_influx/.
# For which, I neither claim nor take acclaim of, as that shit is not mine.
# I keep it real.
from simple_parsing import parse
from dataclasses import dataclass
from configobj import ConfigObj
from configobj.validate import Validator
import os
import sys
from flux import FluxFile
from proclog import f433Log

cfg = """
## Configuration file for myflux
## https://github.com/anoduck/myflux
## MIT License = 'Copyright (c) 2024 Anoduck'
## This software is released under the MIT License.
## https: //opensource.org/licenses/MIT
## ----------------------------------------------------------------------------
## You will need to edit this file and add the appropriate values.
## --------------------------------------------------------------------------------
## *L00k* -- WARNING: ALL VALUES MUST BE CHANGED and PRESENT -- *L00k*
## --------------------------------------------------------------------------------

# Organization configured in influxdb
org = string(default='replace with influxdb organization')

# API token generated by influxdb for organization
api = string(default='replace with generated API token')Options = parse(options, dest="Options")

# Bucket name for use in influxdb
bucket = string(default='replace with bucket name')

# Watch for new files?
watch = boolean(default=False)

# Remove files when processed?
remove = boolean(default=False)

# Path to Dir of JSON files or Json File
path = string(default='~/Sandbox/ISM-Research')

# Log level
log_level = string(default='INFO')

# Log file
log_file = string(default='./flux433.log')
"""


@dataclass
class options:
    """_summary_
    This is a simple script to import rtl_433 json files into influxdb.
    Please remember command line arguments are prioritized over config file.
    If the configuration file does not exist, it will be created for you on the first run.
    Args:
        path (str): Path to Dir of JSON files or Json File
    """
    path: str = ''  # Path to Dir of JSON files or Json File


class Flux433:
    
    def __init__(self):
        self.FF = FluxFile()
        self.Options = parse(options, dest="Options")
        
    def pathfinder(self, path):
        pathlist = []
        if os.path.isfile(path):
            pathlist.append(os.path.abspath(path))
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for name in files:
                    if name.endswith('.json'):
                        pathlist.append(os.path.join(root, name))
        return pathlist


    def main(self):
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
            sys.exit()
        else:
            config = ConfigObj(conf_file, configspec=spec)
        Logger = f433Log(config['log_file'], config['log_level'])
        self.log = Logger.get_log()
        self.log.info("Starting flux433")
        if self.Options.path != '':
            path = self.pathfinder(self.Options.path)
        else:
            path = self.pathfinder(config['path'])
        self.FF.load_files(config, path, self.log)


if __name__ == '__main__':
    r4 = Flux433()
    r4.main()