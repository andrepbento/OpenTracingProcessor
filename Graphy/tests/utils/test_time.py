"""
    Author: André Bento
    Date last modified: 26-02-2019
"""
from unittest import TestCase

from graphy.utils import time as my_time


class TestTime(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.__date_time_str = "01/01/2019 00:00:00"
        self.__date_time = "2019-01-01 00:00:00"

        self.__unix_timestamp = 1546300800  # 2019-01-01 00:00:00
        self.__unix_timestamp_millis = 1546300800000  # 2019-01-01 00:00:00

        self.__unix_timestamp_millis_2 = 1546304400000  # 2019-01-01 01:00:00

    def test_to_unix_time(self):
        """ Test to_unix_time function. """
        self.assertEqual(my_time.to_unix_time(self.__date_time_str), self.__unix_timestamp)

    def test_to_unix_time_millis(self):
        """ Test to_unix_time_millis function. """
        self.assertEqual(my_time.to_unix_time_millis(self.__date_time_str), self.__unix_timestamp_millis)

    def test_from_str_to_datetime(self):
        """ Test from_str_to_datetime function. """
        self.assertEqual(str(my_time.from_str_to_datetime(self.__date_time_str)), self.__date_time)

    def test_from_timestamp_to_datetime(self):
        """ Test from_timestamp_to_datetime function. """
        self.assertEqual(my_time.from_timestamp_to_datetime(self.__unix_timestamp, 's')._repr_base, self.__date_time)

        self.assertEqual(my_time.from_timestamp_to_datetime(self.__unix_timestamp_millis)._repr_base, self.__date_time)

    def test_timestamp_millis_split(self):
        """ Test timestamp_millis_split function. """
        self.assertEqual(my_time.timestamp_millis_split(self.__unix_timestamp_millis, self.__unix_timestamp_millis_2),
                         [self.__unix_timestamp_millis, self.__unix_timestamp_millis_2])
