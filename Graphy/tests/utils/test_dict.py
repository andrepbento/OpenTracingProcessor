"""
    Author: André Bento
    Date last modified: 01-03-2019
"""

from unittest import TestCase

from graphy.utils import dict as my_dict


class TestDict(TestCase):

    def test_calc_percentage(self):
        """ Tests calc_percentage function. """
        test_dict = {'0': 1, '1': 1, '2': 2}
        right_result_dict = {'0': 0.25, '1': 0.25, '2': 0.5}
        wrong_result_dict = {'0': 0.3, '1': 0.1, '2': 0.6}

        self.assertIsInstance(my_dict.calc_percentage(test_dict), dict)

        self.assertEqual(my_dict.calc_percentage(test_dict), right_result_dict)

        self.assertNotEqual(my_dict.calc_percentage(test_dict), wrong_result_dict)

    def test_filter(self):
        """ Tests filter function. """
        test_dict = {'0': 1, '1': 1, '2': {'0': 3}}
        right_filtered_dict = {'0': 1, '2': 3}
        wrong_filtered_dict = {'0': 1, '1': 1}

        self.assertIsInstance(my_dict.filter(test_dict, '0'), dict)

        self.assertEqual(my_dict.filter(test_dict, '0'), right_filtered_dict)

        self.assertNotEqual(my_dict.filter(test_dict, '0'), wrong_filtered_dict)

    def test_sort(self):
        """ Tests sort function. """
        test_dict = {'0': 1, '1': 1, '2': 2}
        right_sorted_list = {'2': 2, '0': 1, '1': 1}
        wrong_sorted_list = {'1': 1, '2': 2, '3': 1}

        self.assertIsInstance(my_dict.sort(test_dict), dict)

        self.assertEqual(my_dict.sort(test_dict), right_sorted_list)

        self.assertNotEqual(my_dict.sort(test_dict), wrong_sorted_list)

    def test_update(self):
        """ Test update function. """
        test_dict = {'0': 1, '1': 1, '2': 2}
        right_updated_dict = {'0': 1, '1': 1, '2': 20}
        wrong_updated_dict = {'0': 1, '1': 1, '2': 2}

        def update_func(value):
            return value * 10

        my_dict.update(test_dict, '2', update_func)

        self.assertEqual(test_dict, right_updated_dict)
        self.assertNotEqual(test_dict, wrong_updated_dict)
