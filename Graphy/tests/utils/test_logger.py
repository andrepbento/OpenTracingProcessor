"""
    Author: André Bento
    Date last modified: 27-02-2019
"""
import os
from logging import Logger
from unittest import TestCase

from graphy.utils import files as my_files
from graphy.utils import logger as my_logger


class TestLogger(TestCase):

    def test_setup_logging(self):
        """ Test setup_logging function. """
        self.assertIsInstance(my_logger.setup_logging('test_logger'), Logger)

        logging_error_file = os.path.abspath(
            os.path.join(my_files.ROOT_PROJECT_DIRECTORY, 'tests', 'utils', 'logging_error.yaml'))
        my_logger.setup_logging('test_logger', logging_error_file)
