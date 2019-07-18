"""
    Author: André Bento
    Date last modified: 05/04/19
"""
import os

from graphy.db import opentsdb
from graphy.db.arangodb import ArangoDB
from graphy.graph.graph_processor import GraphProcessor
from graphy.models import trace as my_trace
from graphy.utils import dict as my_dict, zipkin
from graphy.utils import files as my_files
from graphy.utils import time as my_time

graph_processor = GraphProcessor()
graph_db = ArangoDB()
time_series_db = opentsdb


def service_neighbours(dependencies, start_timestamp, end_timestamp):
    graph_processor.generate_graph_from_zipkin(dependencies, start_timestamp, end_timestamp)
    return ['All service neighbors from {} to {}'.format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                         my_time.from_timestamp_to_datetime(end_timestamp)),
            graph_processor.neighbors()]


def service_degree(dependencies, start_timestamp, end_timestamp):
    graph_processor.generate_graph_from_zipkin(dependencies, start_timestamp, end_timestamp)
    service_degrees = graph_processor.degrees()
    service_in_degrees = graph_processor.degrees('in')
    service_out_degrees = graph_processor.degrees('out')

    time_series_db.send_numeric_metrics('degree', service_degrees,
                                        int((start_timestamp + end_timestamp) / 2))
    time_series_db.send_numeric_metrics('degree_in', service_in_degrees,
                                        int((start_timestamp + end_timestamp) / 2))
    time_series_db.send_numeric_metrics('degree_out', service_out_degrees,
                                        int((start_timestamp + end_timestamp) / 2))

    most_popular_service = service_degrees[0]
    return [
        'Most popular service from {} to {} (Degrees)'.format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                              my_time.from_timestamp_to_datetime(end_timestamp)),
        most_popular_service]


def service_call_count(dependencies, start_timestamp, end_timestamp):
    graph_processor.generate_graph_from_zipkin(dependencies, start_timestamp, end_timestamp)
    service_in_edge_call_count = graph_processor.in_edges_call_count()

    time_series_db.send_numeric_metrics('call_count_in', service_in_edge_call_count,
                                        int((start_timestamp + end_timestamp) / 2))

    service_out_edge_call_count = graph_processor.out_edges_call_count()

    time_series_db.send_numeric_metrics('call_count_out', service_out_edge_call_count,
                                        int((start_timestamp + end_timestamp) / 2))

    service_edge_call_count = my_dict.merge_dicts(service_in_edge_call_count, service_out_edge_call_count)

    time_series_db.send_numeric_metrics('call_count', service_edge_call_count,
                                        int((start_timestamp + end_timestamp) / 2))

    sorted_service_edge_call_count = my_dict.sort(service_edge_call_count)
    most_popular_service = list(sorted_service_edge_call_count.keys())[0]
    return ['Most popular service from {} to {} (Call Count)'.format(
        my_time.from_timestamp_to_datetime(start_timestamp),
        my_time.from_timestamp_to_datetime(end_timestamp)),
        most_popular_service]


def service_status_codes(service_name, traces, start_timestamp, end_timestamp):
    status_codes = my_trace.get_status_codes(traces)
    status_codes_percentage = my_dict.calc_percentage(status_codes)

    time_series_db.send_numeric_metrics('status_code.{}'.format(service_name),
                                        status_codes_percentage,
                                        int((start_timestamp + end_timestamp) / 2))

    return ['Status Codes from {} to {}'.format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                my_time.from_timestamp_to_datetime(end_timestamp)),
            '\nservice_name: {}'
            '\nstatus_codes: {}'
            '\nstatus_codes_percentage: {}'.format(service_name, my_dict.sort(status_codes),
                                                   my_dict.sort(status_codes_percentage))]


def trace_quality_analysis(traces, service_name: str, timestamp_1, timestamp_2):
    span_trees = my_trace.generate_span_trees(traces)
    trace_metrics_data = my_trace.extract_metrics(span_trees)

    x_values = list(trace_metrics_data.coverability_count.keys())
    y_values = my_dict.filter(trace_metrics_data.coverability_count, 'value').values()

    my_files.save_dict(os.path.join(my_files.TRACE_COV_PROJECT_DIRECTORY, service_name + '.csv'),
                       dict(zip(x_values, y_values)))

    return [
        'Trace quality analysis from {} to {} for service {} completed.'.format(
            my_time.from_timestamp_to_datetime(timestamp_1), my_time.from_timestamp_to_datetime(timestamp_2),
            service_name),
        'OK!']


def service_response_time_analysis(service_name: str, trace_metrics_data, start_timestamp, end_timestamp):
    if trace_metrics_data.response_time_avg is not -1:
        response_time_avg = trace_metrics_data.response_time_avg

        time_series_db.send_numeric_metric(['response_time_avg', service_name], response_time_avg,
                                           int((start_timestamp + end_timestamp) / 2))

        return ['Response time analysis from {} to {} for service {}\nAVG: {}'.format(
            my_time.from_timestamp_to_datetime(start_timestamp),
            my_time.from_timestamp_to_datetime(end_timestamp),
            service_name,
            response_time_avg),
            'Analysis completed!']
    else:
        return ['No data found from {} to {} for service {}'.format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                                    my_time.from_timestamp_to_datetime(end_timestamp),
                                                                    service_name),
                '\nCan\'t perform response time analysis']


def service_morphology(dependencies, start_timestamp, end_timestamp, previous_graph):
    current_graph = graph_processor.generate_graph_from_zipkin(dependencies, start_timestamp, end_timestamp)
    current_graph.name = '{}_{}'.format(start_timestamp, end_timestamp)

    graph_db.insert_graph(start_timestamp, end_timestamp, list(current_graph.edges(data=True)), graph_db.graph_db)

    if previous_graph:
        graph_diff = graph_processor.graphs_difference(previous_graph, current_graph)

        graph_db.insert_graph(start_timestamp, end_timestamp, list(graph_diff.edges(data=True)),
                              graph_db.graph_diff_db)

        graph_variance = graph_processor.graphs_variance(previous_graph, current_graph)

        time_series_db.send_numeric_metric(['graph_gain_variance'], graph_variance.get('gain'),
                                           int((start_timestamp + end_timestamp) / 2))
        time_series_db.send_numeric_metric(['graph_loss_variance'], graph_variance.get('loss'),
                                           int((start_timestamp + end_timestamp) / 2))
        time_series_db.send_numeric_metric(['graph_variance'],
                                           graph_variance.get('gain') - graph_variance.get('loss'),
                                           int((start_timestamp + end_timestamp) / 2))

        message = ['System Morphology from {} to {}'.format(my_time.from_timestamp_to_datetime(start_timestamp),
                                                            my_time.from_timestamp_to_datetime(end_timestamp)),
                   '\nprevious_graph.Nodes:{}\nprevious_graph.Edges:{}'
                   '\nprevious_graph.NodesLen:{}\nprevious_graph.EdgesLen:{}'
                   '\ncurrent_graph.Nodes:{}\ncurrent_graph.Edges:{}'
                   '\ncurrent_graph.NodesLen:{}\ncurrent_graph.EdgesLen:{}'
                   '\ngraph_diff.Nodes:{}\ngraph_diff.Edges:{}'
                   '\ngraph_diff.NodesLen:{}\ngraph_diff.EdgesLen:{}'.format(previous_graph.nodes,
                                                                             previous_graph.edges(data=True),
                                                                             len(previous_graph.nodes),
                                                                             len(previous_graph.edges),
                                                                             current_graph.nodes,
                                                                             current_graph.edges(data=True),
                                                                             len(current_graph.nodes),
                                                                             len(current_graph.edges),
                                                                             graph_diff.nodes,
                                                                             graph_diff.edges(data=True),
                                                                             len(graph_diff.nodes),
                                                                             len(graph_diff.edges))]
    else:
        previous_graph = current_graph.copy()
        message = ['NO PREVIOUS GRAPH!', '']

    return message, previous_graph


g_previous_graph = None


def process_all_metrics_in_time(service_names, timestamp_1, timestamp_2):
    global g_previous_graph

    message = list()

    dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)

    if not dependencies:
        message.append(['No services from {} to {}'.format(my_time.from_timestamp_to_datetime(timestamp_1),
                                                           my_time.from_timestamp_to_datetime(timestamp_2)),
                        'Can\'t perform calculation!'])
    else:
        message.append(service_neighbours(dependencies, timestamp_1, timestamp_2))
        message.append(service_degree(dependencies, timestamp_1, timestamp_2))
        message.append(service_call_count(dependencies, timestamp_1, timestamp_2))
        message, g_previous_graph = service_morphology(dependencies, timestamp_1, timestamp_2, g_previous_graph)
        message.append(message)

    for service_name in service_names:
        traces = zipkin.get_traces(service_name=service_name, end_ts=timestamp_2,
                                   lookback=timestamp_2 - timestamp_1)

        if not traces:
            message.append(['No traces found from {} to {} for service {}'.format(
                my_time.from_timestamp_to_datetime(timestamp_1),
                my_time.from_timestamp_to_datetime(timestamp_2),
                service_name),
                '\nCan\'t calculate service status codes'])
        else:
            span_trees = my_trace.generate_span_trees(traces)
            trace_metrics_data = my_trace.extract_metrics(span_trees)

            message.append(service_status_codes(service_name, traces, timestamp_1, timestamp_2))
            # trace_quality_analysis(service_name, trace_metrics_data)
            message.append(service_response_time_analysis(service_name, trace_metrics_data, timestamp_1, timestamp_2))

    print(message)
