"""
    Author: André Bento
    Date last modified: 08-03-2019
"""
from arango import ArangoClient

from graphy.utils import config

arango_db_config = config.get('ARANGODB')


class ArangoDB(object):
    def __init__(self, purge_database=False):
        """
        Initializes the ArangoDB entity.

        :param purge_database: True to purge all existing database, False otherwise.
        """
        self.__ip = arango_db_config.get('HOST')
        self.__port = arango_db_config.get('PORT')

        self.__username = arango_db_config.get('USERNAME')
        self.__password = arango_db_config.get('PASSWORD')

        self.__graph_db = arango_db_config.get('GRAPH_DB_NAME')
        self.__graph_diff_db = arango_db_config.get('GRAPH_DIFF_DB_NAME')

        self.__client = ArangoClient(host=self.__ip, port=self.__port)

        self.__db = self.__sys_db()

        if purge_database:
            self.__delete_database(self.__graph_db)
            self.__delete_database(self.__graph_diff_db)

        self.__connect_database()

    def __sys_db(self):
        """ Obtain the system database. """
        return self.__client.db(name='_system', username=self.__username, password=self.__password)

    def __create_database(self, db_name=arango_db_config.get('DB_NAME')):
        """
        Creates a new database.

        :param db_name: The name of the database.
        :return:
        """
        if not self.__sys_db().has_database(db_name):
            self.__sys_db().create_database(db_name)

    def __delete_database(self, db_name=arango_db_config.get('DB_NAME')):
        """
        Deletes a certain database database.

        :param db_name: The name of the database.
        :return: True if success, False otherwise.
        """
        if self.__sys_db().has_database(db_name):
            return self.__sys_db().delete_database(db_name)
        return False

    def __connect_database(self, name=arango_db_config.get('GRAPH_DB_NAME')):
        """
        Connects to a database.

        :param name: The name of the database.
        """
        self.__db = self.__client.db(name, self.__username, self.__password)

    @property
    def graph_db(self):
        return self.__graph_db

    @property
    def graph_diff_db(self):
        return self.__graph_diff_db

    def get_graph(self, name):
        """
        Gets a certain graph.

        :param name: The name of the graph.
        :return: The graph or None if it hasn't been found.
        """
        return self.__db.graph(name)

    def get_graphs(self, db=arango_db_config.get('GRAPH_DB_NAME')):
        """
        Gets all graph names stored in the database.

        :return: A list of graph names.
        """
        self.__create_database(db)
        self.__connect_database(db)

        graph_names_list = list()
        for graph_dict in self.__db.graphs():
            if isinstance(graph_dict, dict):
                graph_names_list.append(graph_dict.get('name'))
        return graph_names_list

    def delete_graph(self, name):
        """
         Deletes a certain graph.

         :param name: The graph name.
         :return: True if graph was deleted or false if not.
         """
        return self.__db.delete_graph(name)

    def insert_graph(self, timestamp_start, timestamp_end, node_links, db=arango_db_config.get('GRAPH_DB_NAME')):
        """
        Inserts a new graph.

        :param timestamp_end: The start timestamp, in unix timestamp format, of the graph.
        :param timestamp_start: The end timestamp, in unix timestamp format, of the graph.
        :param node_links: The links in dict data format.
        :param db: The database name.
        :return: The created graph.
        """
        self.__create_database(db)
        self.__connect_database(db)

        graph_name = 'graph_{}_{}'.format(timestamp_start, timestamp_end)
        if self.__db.has_graph(graph_name):
            graph = self.__db.graph(graph_name)
        else:
            graph = self.__db.create_graph(graph_name)

        vertex_collection_name = 'Services'  # TODO: Remove hard coded string
        if graph.has_vertex_collection(vertex_collection_name):
            vertex_collection = graph.vertex_collection(vertex_collection_name)
        else:
            vertex_collection = graph.create_vertex_collection(vertex_collection_name)

        edge_collection = self.__edge_collection(graph, vertex_collection, timestamp_start, timestamp_end)

        for node_link in node_links:
            node_from_name = node_link[0]
            node_to_name = node_link[1]
            links = node_link[2].get('weight')

            vertex_1 = self.__vertex(vertex_collection, node_from_name, {'name': node_from_name})
            vertex_2 = self.__vertex(vertex_collection, node_to_name, {'name': node_to_name})

            collection_name = vertex_collection.name
            edge_collection.insert({'_from': '{}/{}'.format(collection_name, vertex_1.get('_key')),
                                    '_to': '{}/{}'.format(collection_name, vertex_2.get('_key')),
                                    'links': links})

        return graph

    def get_graph_edges(self, graph_name):
        """
        Gets the graph edges.

        :param graph_name: The graph name.
        :return: A list of graph edges.
        """
        edge_list = list()
        graph = self.get_graph(graph_name)

        graph_vertex_collections = graph.vertex_collections()
        graph_vertex_collection_name = graph_vertex_collections[0]  # TODO: Try to remove hard coded integer.

        graph_edge_collection = graph.edge_definitions()
        graph_edge_collection_name = graph_edge_collection[0] \
            .get('edge_collection')  # TODO: Try to remove hard coded string and integer.

        for vertex_item in self.__db.collection(graph_vertex_collection_name):
            if graph.has_vertex(vertex_item.get('_id')):
                edges = graph.edges(graph_edge_collection_name, vertex_item.get('_id'), direction='out').get('edges')
                edge_list.extend(edges)

        return edge_list

    @staticmethod
    def __edge_collection(graph, vertex_collection, start_timestamp, end_timestamp):
        """
        Gets or creates a edge collection.

        :param graph: The graph where the edge collection might be or should be.
        :param vertex_collection: The vertex collection
        :param start_timestamp: The start timestamp of the collection, in unix timestamp format.
        :param end_timestamp: The end timestamp of the collection, in unix timestamp format.
        :return: The edge collection.
        """
        service_links_edge_collection_name = 'ServiceLinks_{}_{}'.format(start_timestamp, end_timestamp)
        if graph.has_edge_collection(service_links_edge_collection_name):
            return graph.edge_collection(service_links_edge_collection_name)
        else:
            return graph.create_edge_definition(
                edge_collection=service_links_edge_collection_name,
                from_vertex_collections=[vertex_collection.name],
                to_vertex_collections=[vertex_collection.name]
            )

    @staticmethod
    def __vertex(vertex_collection, vertex_key, vertex_attributes):
        """
        Gets or creates a vertex in a certain vertex collection.

        :param vertex_collection: The vertex collection.
        :param vertex_key: The vertex key identifier.
        :param vertex_attributes: The vertex attributes.
        :return:
        """
        if vertex_collection.has({'_key': vertex_key}):
            return vertex_collection.get({'_key': vertex_key})
        else:
            vertex = {'_key': vertex_key}
            vertex.update(vertex_attributes)
            return vertex_collection.insert(vertex)
