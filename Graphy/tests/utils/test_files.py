"""
    Author: André Bento
    Date last modified: 26-02-2019
"""
import os
from unittest import TestCase

from graphy.utils import files as my_files


class TestFiles(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.__file_path = os.path.realpath(__file__)

    def test_get_absolute_path(self) -> None:
        """ Tests get_absolute_path function. """
        with self.assertRaises(FileNotFoundError):
            my_files.get_absolute_path('not/found/file.txt')

    def test_read_file(self) -> None:
        """ Tests read_file function. """
        self.assertIsNotNone(my_files.read_file(self.__file_path))
