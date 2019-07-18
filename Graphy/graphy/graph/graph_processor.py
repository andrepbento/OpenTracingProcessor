"""
    Author: André Bento
    Date last modified: 08-04-2019
"""
from collections import defaultdict

import networkx as nx

from graphy.utils import dict as my_dict
from graphy.utils import list as my_list
from graphy.utils import logger as my_logger

logger = my_logger.setup_logging(__name__)


class GraphProcessor:
    """ GraphProcessor contains a collection of methods to handle Graphs. """

    def __init__(self):
        """ Initiate a new GraphProcessor. """
        self.__graph = nx.MultiDiGraph()

        self.__start_timestamp = None
        self.__end_timestamp = None

        self.span_tree = None

    @property
    def graph(self):
        return self.__graph

    def generate_graph(self, tuple_list):
        """
        Generates the graph using the tuple list.

        :param tuple_list: The tuple list with the from and to nodes.
        :return: Generated graph.
        """
        self.__graph.add_edges_from(tuple_list)
        return self.__graph

    def generate_graph_from_zipkin(self, dependencies, start_timestamp, end_timestamp):
        """
        Generates the graph using the Dependencies from Zipkin.

        :param dependencies: Graph dependencies data in Zipkin format.
        :param start_timestamp: Start unix timestamp of the graph.
        :param end_timestamp: End unix timestamp of the graph.
        :return: Generated graph.
        """
        if start_timestamp == self.__start_timestamp and end_timestamp == self.__end_timestamp:
            return self.__graph

        self.__graph.clear()
        for dependency in dependencies:
            self.__graph.add_edge(dependency['parent'],
                                  dependency['child'],
                                  weight=dependency['callCount'])
        return self.__graph

    @staticmethod
    def graphs_difference(first_graph: nx.MultiDiGraph, second_graph: nx.MultiDiGraph, graph_name: str = None):
        """
        Performs the difference between two graphs.

        :param first_graph: The first named Graph in NetworkX MultiDiGraph format.
        :param second_graph: The second named Graph in NetworkX MultiDiGraph format.
        :param graph_name: The name of the resulting graph.
        :return: The resulting difference between the graphs.
        """
        g_diff = nx.MultiDiGraph()
        graph_1 = first_graph.copy()  # Copy to preserve values.
        graph_2 = second_graph.copy()

        # Cycle through all edges in the first graph.
        for n in graph_1.edges:
            if n not in graph_2.edges:
                edge_weight = graph_1.get_edge_data(n[0], n[1])[0].get('weight')
                edge_weight = str(int(edge_weight) * -1)  # Lost node.
                g_diff.add_edge(n[0], n[1], weight=edge_weight)
            else:
                first_edge_weight = graph_1.get_edge_data(n[0], n[1])[0].get('weight')
                second_edge_weight = graph_2.get_edge_data(n[0], n[1])[0].get('weight')
                if first_edge_weight != second_edge_weight:
                    g_diff.add_edge(n[0], n[1], weight=second_edge_weight - first_edge_weight)
                graph_2.remove_edge(n[0], n[1])  # Remove edge to reduce size.

        # Cycle through all remaining edges in second_graph.
        for n in graph_2.edges:
            if n not in graph_1.edges:
                edge_weight = graph_2.get_edge_data(n[0], n[1])[0].get('weight')
                g_diff.add_edge(n[0], n[1], weight=edge_weight)

        if graph_name is None:
            start_timestamp = graph_1.name.split('_')[1]
            end_timestamp = graph_2.name.split('_')[-1]
            graph_name = 'graph_{}_{}'.format(start_timestamp, end_timestamp)
        g_diff.name = graph_name

        return g_diff

    @staticmethod
    def graphs_variance(previous_graph: nx.MultiDiGraph, current_graph: nx.MultiDiGraph) -> dict:
        """
        TODO: Add doc.

        :param previous_graph:
        :param current_graph:
        :return:
        """
        graph_1 = previous_graph.copy()
        graph_2 = current_graph.copy()

        graph_1_nodes = list(graph_1.nodes)
        graph_2_nodes = list(graph_2.nodes)

        diff_1_2 = my_list.diff(graph_1_nodes, graph_2_nodes)
        diff_2_1 = my_list.diff(graph_2_nodes, graph_1_nodes)

        return {
            'loss': len(diff_1_2),
            'gain': len(diff_2_1),
            'lost_nodes': diff_1_2,
            'gain_nodes': diff_2_1
        }

    def degrees(self, direction: str = None, sort: bool = True) -> list:
        """
        Calculates the degree for all nodes.
        Node degree is the sum of all input and output edges.

        :param direction: The edge direction, 'in' - input, 'out' - output, other - both.
        :param sort: sort the list by degree in reverse order.
        :return: a tuple list containing all the nodes and their corresponding degree.
        """
        # TODO: The following lines of code can be used to get the input or output degree from all nodes
        if direction == 'in':
            in_degrees = self.__graph.in_degree
            return sorted(in_degrees, key=lambda tup: tup[1], reverse=sort)
        elif direction == 'out':
            out_degrees = self.__graph.out_degree
            return sorted(out_degrees, key=lambda tup: tup[1], reverse=sort)
        else:
            return sorted(self.__graph.degree, key=lambda tup: tup[1], reverse=sort)

    def edges_call_count(self, service_name: str = None) -> dict:
        """
        Calculates the number of calls for all nodes or for a specific node.

        :param service_name: The service node name.
        :return: The list of call counts.
        """
        edges = my_dict.merge_dicts(self.in_edges_call_count(service_name),
                                    self.out_edges_call_count(service_name))
        return edges

    def in_edges_call_count(self, service_name: str = None) -> dict:
        """
        Calculates the number of in calls for all nodes or for a specific node.

        :param service_name: The service node name.
        :return: The list of call counts.
        """
        reverse_graph = self.__graph.reverse()

        if service_name:
            edges_in = list(reverse_graph.edges(service_name, data=True))
        else:
            edges_in = list(reverse_graph.edges(data=True))

        return self.__count_edges(edges_in)

    def out_edges_call_count(self, service_name: str = None) -> dict:
        """
        Calculates the number of out calls for all nodes or for a specific node.

        :param service_name: The service node name.
        :return: The list of call counts.
        """
        if service_name:
            edges_out = list(self.__graph.edges(service_name, data=True))
        else:
            edges_out = list(self.__graph.edges(data=True))

        return self.__count_edges(edges_out)

    @staticmethod
    def __count_edges(edges: list) -> dict:
        """
        Counts the edges from a certain list of edges.

        :param edges: The edge list with weight values.
        :return: The list of call counts.
        """
        edges_call_count = dict()

        for edge in edges:
            service_from = edge[0]
            call_count = edge[2].get('weight')
            if service_from in edges_call_count:
                edges_call_count[service_from] += call_count
            else:
                edges_call_count[service_from] = call_count

        return edges_call_count

    def neighbors(self, service_name: str = None) -> dict:
        """
        Calculates the out neighbors for all nodes or for a specific node.

        :param service_name: the service node name.
        :return: a dictionary containing all the nodes and their corresponding list of neighbors.
        """
        debug_message = ''
        neighbors = defaultdict(list)

        service_nodes = self.__graph.nodes
        if service_name:
            service_nodes = [service_name]

        for node in service_nodes:
            debug_message += '\nNode: {}'.format(node)
            for i, neighbor in enumerate(self.__graph.neighbors(node)):
                debug_message += '\n\t{}: {}'.format(i, neighbor)
                neighbors[node].append(neighbor)
        logger.debug(debug_message)
        return neighbors
