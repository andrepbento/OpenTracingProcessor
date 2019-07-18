"""
    Author: André Bento
    Date last modified: 26-02-2019
"""
from unittest import TestCase

from graphy.utils import config as my_config


class TestConfig(TestCase):

    def test_get(self):
        """ Tests get function. """
        sample_arango_db_dict_conf = {
            'GRAPH_DB_NAME': 'graph_db',
            'GRAPH_DIFF_DB_NAME': 'graph_diff_db'
        }

        self.assertIsInstance(my_config.get('GRAPHY'), dict)

        self.assertEqual(my_config.get('TEST_12345'), dict())

        self.assertEqual(my_config.get('ARANGODB').get('GRAPH_DB_NAME'),
                         sample_arango_db_dict_conf.get('GRAPH_DB_NAME'))
        self.assertEqual(my_config.get('ARANGODB').get('GRAPH_DIFF_DB_NAME'),
                         sample_arango_db_dict_conf.get('GRAPH_DIFF_DB_NAME'))
