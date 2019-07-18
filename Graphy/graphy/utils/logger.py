"""
    Author: André Bento
    Date last modified: 26-02-2019
"""
import logging
import logging.config
import os
import sys

import coloredlogs
import yaml

from graphy.utils import files


def setup_logging(name, default_path='graphy/logging.yaml', default_level=logging.INFO):
    """ Setup logging configuration """
    path = files.get_absolute_path(default_path, from_project=True)
    try:
        with open(path, 'r') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
            coloredlogs.install()
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, file_name, exc_tb.tb_lineno)
        logging.basicConfig(level=default_level)
        coloredlogs.install(level=default_level)
    return logging.getLogger(name)
