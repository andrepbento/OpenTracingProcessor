"""
    Author: André Bento
    Date last modified: 04-03-2019
"""
import time
from unittest import TestCase

from graphy.db import opentsdb
from graphy.utils import config as my_config

TIME_WAIT = 3


class TestOpenTSDB(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.__metric_name = 'test_metric'

        self.__metric_1 = {'ts': 1546304400, 'name': self.__metric_name, 'value': 100}  # ts: 2019.1.1 - 01:00:00
        self.__metric_2 = {'ts': 1546390800, 'name': self.__metric_name, 'value': 200}  # ts: 2019.1.2 - 01:00:00

        self.__start_timestamp = 1546300800  # 2019.1.1 - 00:00:00
        self.__end_timestamp = 1546473600  # 2019.1.3 - 00:00:00

        opentsdb.erase_metrics(self.__metric_name, self.__start_timestamp, self.__end_timestamp)

        time.sleep(TIME_WAIT)

    def tearDown(self) -> None:
        super().tearDown()

        opentsdb.erase_metrics(self.__metric_name, self.__start_timestamp, self.__end_timestamp)

    def test_format_metric_name(self):
        """ Tests format_metric_name function. """
        naming_list = ['test', 'name']
        expected_result = '{}.{}.{}'.format(my_config.get('OPENTSDB').get('STORE_NAME'), naming_list[0], naming_list[1])

        self.assertEqual(opentsdb.format_metric_name(naming_list), expected_result)

    def test_erase_metrics(self):
        """ Tests erase_metrics function. """

        self.assertTrue(opentsdb.send_numeric_metric([self.__metric_1.get('name')], self.__metric_1.get('value'),
                                                     self.__metric_1.get('ts')))
        time.sleep(TIME_WAIT)

        self.assertTrue(opentsdb.send_numeric_metric([self.__metric_2.get('name')], self.__metric_2.get('value'),
                                                     self.__metric_2.get('ts')))
        time.sleep(TIME_WAIT)

        self.assertEqual(opentsdb.erase_metrics(self.__metric_name, self.__start_timestamp, self.__end_timestamp),
                         {'1546304400': 100.0, '1546390800': 200.0})

        time.sleep(TIME_WAIT)

        self.assertEqual(opentsdb.erase_metrics(self.__metric_name, self.__start_timestamp, self.__end_timestamp), None)

        time.sleep(TIME_WAIT)

    def test_get_metrics(self):
        """ Tests get_metrics function. """
        self.assertEqual(opentsdb.get_metrics(self.__metric_name, self.__start_timestamp, self.__end_timestamp), None)

        time.sleep(TIME_WAIT)

        self.assertTrue(opentsdb.send_numeric_metric([self.__metric_1.get('name')], self.__metric_1.get('value'),
                                                     self.__metric_1.get('ts')))

        time.sleep(TIME_WAIT)

        self.assertTrue(opentsdb.send_numeric_metric([self.__metric_2.get('name')], self.__metric_2.get('value'),
                                                     self.__metric_2.get('ts')))

        time.sleep(TIME_WAIT)

        self.assertEqual(opentsdb.get_metrics(self.__metric_name, self.__start_timestamp, self.__end_timestamp),
                         {'1546304400': 100.0, '1546390800': 200.0})

        time.sleep(TIME_WAIT)

    def test_send_numeric_metrics(self):
        """ Tests send_numeric_metrics function. """
        list_of_metrics = [('service_1', 3), ('service_2', 5)]

        metric_names = opentsdb.send_numeric_metrics(self.__metric_name, list_of_metrics, 1546304400)

        time.sleep(TIME_WAIT)

        name_1 = '{}.{}'.format(self.__metric_name, 'service_1')
        name_2 = '{}.{}'.format(self.__metric_name, 'service_2')

        self.assertListEqual(metric_names, [name_1, name_2])

    def test_send_numeric_metric(self):
        """ Tests send_numeric_metric function. """
        self.assertTrue(opentsdb.send_numeric_metric([self.__metric_name], 100, 1546304400))  # 2019.1.1 01:00:00

        time.sleep(TIME_WAIT)
