"""
    Author: André Bento
    Date last modified: 06-03-2019
"""
from unittest import TestCase

from graphy.db import arangodb
from graphy.utils import config


class TestArangoDB(TestCase):

    def setUp(self) -> None:
        super().setUp()

        arango_db_config = config.get('ARANGODB')

        self.__graph_db = arango_db_config.get('GRAPH_DB_NAME')
        self.__graph_diff_db = arango_db_config.get('GRAPH_DIFF_DB_NAME')

        self.__arango = arangodb.ArangoDB()

    def tearDown(self) -> None:
        super().tearDown()

    def test_graph_db(self):
        """ Test graph_db property. """
        self.assertEqual(self.__arango.graph_db, self.__graph_db)

    def test_graph_diff_db(self):
        """ Test graph_diff_db property. """
        self.assertEqual(self.__arango.graph_diff_db, self.__graph_diff_db)

    def test_get_graph(self):
        """ Test get_graph function. """
        # TODO: Write tests.
        # self.assertIsNotNone(self.__arango.get_graph('test_graph'))

        self.assertIsNone(self.__arango.get_graph('not_a_graph'))

        pass

    def test_delete_graph(self):
        """ Test delete_graph function. """
        # TODO: Write tests.
        pass

    def test_insert_graph(self):
        """ Test inset_graph function. """
        # TODO: Write tests.
        pass

    def test_get_graph_edges(self):
        """ Test get_graph_edges function. """
        # TODO: Write tests.
        pass
