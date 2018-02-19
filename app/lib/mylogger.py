# -*- coding: utf-8 -*-
# @Author: wangwh8
# @Date:   2018-01-19 17:21:14
# @Last Modified by:   wangwh8
# @Last Modified time: 2018-01-22 16:08:54
import logging
from datetime import datetime
import os


def init_logger(entry, log_filename, logs_dir="logs"):
    curdir = os.path.dirname(entry)
    print curdir
    # timestamp = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
    logFmt = "[%(levelname)s] %(asctime)s %(message)s"
    logsdir = os.path.join(curdir, 'logs')
    if not os.path.isdir(logsdir):
        os.makedirs(logsdir)
    logging.basicConfig(level=logging.DEBUG,
              format=logFmt,
              datefmt='%Y-%m-%d %X',
              filename=os.path.join(logsdir, log_filename),
              )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(logFmt, datefmt='%Y-%m-%d %X')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
