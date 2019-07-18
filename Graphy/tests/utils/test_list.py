"""
    Author: André Bento
    Date last modified: 25-02-2019
"""
import unittest

from graphy.utils import list as my_list


class TestList(unittest.TestCase):

    def test_diff(self):
        """ Test diff function. """
        list_1 = list([1, 2, 3])
        list_2 = list([1, 2])
        list_3 = list([1, 2, 4])

        self.assertEqual(my_list.diff(list_1, list_1), list())

        self.assertEqual(my_list.diff(list_1, list_2), list([3]))

        self.assertEqual(my_list.diff(list_2, list_1), list([]))

        self.assertEqual(my_list.diff(list_1, list_3), list([3]))

        self.assertEqual(my_list.diff(list_3, list_1), list([4]))

    def test_symmetric_diff(self):
        """ Test diff function. """
        list_1 = list([1, 2, 3])
        list_2 = list([1, 2])
        list_3 = list([1, 2, 4])

        self.assertEqual(my_list.symmetric_diff(list_1, list_1), list())

        self.assertEqual(my_list.symmetric_diff(list_1, list_2), list([3]))

        self.assertEqual(my_list.symmetric_diff(list_2, list_1), list([3]))

        self.assertEqual(my_list.symmetric_diff(list_1, list_3), list([3, 4]))

        self.assertEqual(my_list.symmetric_diff(list_3, list_1), list([3, 4]))
