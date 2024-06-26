# Copyright (c) 2024 Anoduck
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import logging
import threading
from logging import handlers
from warnings import warn
import os


class f433Log(threading.Thread):

    def __init__(self, log_file=None, lev=None, systemd=False):
        super().__init__()
        self.log_file = log_file
        self.lev = lev
        self.systemd = systemd
        self.daemon = True
        self.log = None
        self.start()

    def get_log(self, Options) -> logging.Logger:
        dup = Options.dupebuster
        if self.systemd and not dup:
            if self.lev is None:
                self.lev = 'INFO'
            log = logging.getLogger(__name__)
            if log.hasHandlers():
                log.handlers.clear()
            log_levels = {'INFO': logging.INFO,
                          'DEBUG': logging.DEBUG,
                          'ERROR': logging.ERROR}
            if self.lev in log_levels.keys():
                set_level = log_levels[self.lev]
                log.setLevel(set_level)
            else:
                warn('Invalid level. Defaulting to debug')
                log.setLevel(logging.DEBUG)
            handler = handlers.SysLogHandler(address='/dev/log')
            ormatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            log.addHandler(handler)
            log.info('## ========================================= ##')
            log.info('You have now Started flux433.py')
            log.info('## ========================================= ##')
            log.info('Acquired Logger')
            return log
        if self.log is not None:
            return self.log
        else:
            if self.log_file is None:
                self.log_file = 'flux433.log'
            if self.lev is None:
                self.lev = 'DEBUG'
            if not os.path.exists(self.log_file):
                open(self.log_file, 'a').close()
            log = logging.getLogger(__name__)
            if log.hasHandlers():
                log.handlers.clear()
            log_levels = {'INFO': logging.INFO,
                          'DEBUG': logging.DEBUG,
                          'ERROR': logging.ERROR}
            if self.lev in log_levels.keys():
                set_level = log_levels[self.lev]
                log.setLevel(set_level)
            else:
                warn('Invalid level. Defaulting to debug')
                log.setLevel(logging.DEBUG)
            handler = handlers.RotatingFileHandler(
                filename=self.log_file,
                mode='a', maxBytes=10 * 1024 * 1024,
                backupCount=2,
                encoding='utf-8',
                delay=True)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            log.addHandler(handler)
            log.info('## ========================================= ##')
            log.info('You have now Started flux433.py')
            log.info('## ========================================= ##')
            log.info('Acquired Logger')
            return log