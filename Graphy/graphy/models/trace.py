"""
    Author: André Bento
    Date last modified: 08-04-2019
"""
from graphy.models import span as my_span
from graphy.models.span_tree import SpanTree
from graphy.utils import logger as my_logger

logger = my_logger.setup_logging(__name__)


class TraceMetricsData(object):
    def __init__(self):
        self.__coverability_count = {
            '<1%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '1-10%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '11-20%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '21-30%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '31-40%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '41-50%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '51-60%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '61-70%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '71-80%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '81-90%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            '91-100%': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            },
            'error': {
                'value': 0,
                'trace_ids': set(),
                'span_ids': set()
            }
        }
        self.__response_times = {}
        self.__structural_issues = {
            "count": 0,
            "issue_list": list()
        }

    @property
    def coverability_count(self) -> dict:
        return self.__coverability_count

    @property
    def response_times(self) -> dict:
        return self.__response_times

    @property
    def response_time_avg(self) -> float:
        if not self.__response_times:
            return -1
        return sum(self.__response_times.values()) / len(self.__response_times)

    def update_coverability(self, trace_times: dict) -> None:
        """
        Counts the trace coverability for each trace.

        :param trace_times: A dictionary with the trace coverability data.
        :return: A dictionary with the interval trace coverability counting.
        """

        # TODO: Improve method [If else].
        for key in trace_times.keys():
            percentage = trace_times[key].get('%')
            span_ids = trace_times[key]['span_ids']
            if percentage < 1.0:
                trace_coverability_item = self.__coverability_count['<1%']
            elif 1.0 <= percentage < 10.0:
                trace_coverability_item = self.__coverability_count['1-10%']
            elif 11.0 <= percentage < 20.0:
                trace_coverability_item = self.__coverability_count['11-20%']
            elif 21.0 <= percentage < 30.0:
                trace_coverability_item = self.__coverability_count['21-30%']
            elif 31.0 <= percentage < 40.0:
                trace_coverability_item = self.__coverability_count['31-40%']
            elif 41.0 <= percentage < 50.0:
                trace_coverability_item = self.__coverability_count['41-50%']
            elif 51.0 <= percentage < 60.0:
                trace_coverability_item = self.__coverability_count['51-60%']
            elif 61.0 <= percentage < 70.0:
                trace_coverability_item = self.__coverability_count['61-70%']
            elif 71.0 <= percentage < 80.0:
                trace_coverability_item = self.__coverability_count['71-80%']
            elif 81.0 <= percentage < 90.0:
                trace_coverability_item = self.__coverability_count['81-90%']
            elif 91.0 <= percentage < 100.0:
                trace_coverability_item = self.__coverability_count['91-100%']
            else:
                trace_coverability_item = self.__coverability_count['error']

            if trace_coverability_item:
                trace_coverability_item['value'] += 1
                trace_coverability_item['trace_ids'].add(key)
                trace_coverability_item['span_ids'].update(span_ids)

    def update_response_time(self, trace_id: str, response_time: float) -> None:
        self.__response_times[trace_id] = response_time

    def update_structural_issues(self, issue: Exception):
        self.__structural_issues["count"] += 1
        self.__structural_issues["issue_list"].append(issue)


def get_status_codes(trace_list):
    """
    Gets the status codes presented in a trace list.

    :param trace_list: The trace list in Zipkin format.
    :return: A dictionary containing the grouped status codes counting.
    """

    status_codes_dict = dict()
    for trace in trace_list:
        for span in trace:
            status_code = my_span.get_status_code(span)
            if status_code and len(status_code) > 1:
                status_code_group = status_code[0]
                status_code = status_code_group + 'XX'
                if status_code in status_codes_dict:
                    status_codes_dict[status_code] += 1
                else:
                    status_codes_dict[status_code] = 1
    return status_codes_dict


def __calculate_trace_metrics_data(trace_metrics_data: TraceMetricsData, span_tree_obj: SpanTree) -> None:
    """
    Calculates the trace metrics data for a certain SpanTree.

    :param trace_metrics_data: A TraceMetricsData object.
    :param span_tree_obj: A SpanTree object.
    """
    trace_id = span_tree_obj.trace_id
    span_tree = span_tree_obj.span_tree

    response_times = list()

    trace_times = dict()
    trace_times[trace_id] = {
        't_parent': 0,
        't_child': 0,
        '%': -1.0,
        'span_ids': set()
    }

    parent_node = span_tree.get_node(span_tree.root)  # TODO: Change to accept multiple levels.

    try:
        parent_duration = max(parent_node.data.get_durations())
        trace_times[trace_id]['t_parent'] = parent_duration
    except Exception as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        return

    for child in span_tree.children(span_tree.root):  # TODO: Change to accept multiple levels.
        child_span_data: my_span.Span = child.data

        span_id = child_span_data.id
        trace_times[trace_id]['span_ids'].add(span_id)

        duration = max(child_span_data.get_durations())
        trace_times[trace_id]['t_child'] += duration

        response_times.append(duration)

    t_child = trace_times[trace_id]['t_child']
    t_parent = trace_times[trace_id]['t_parent']
    try:
        t_percentage = (t_child / t_parent) * 100  # microseconds to milliseconds
        if t_percentage < 0 or t_percentage > 100:
            raise Exception('trace time percentage error; t_percentage={}'.format(t_percentage))
        trace_times[trace_id]['%'] = t_percentage
    except Exception as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        trace_times[trace_id]['%'] = -1

    trace_metrics_data.update_coverability(trace_times)
    trace_metrics_data.update_response_time(trace_id, float(sum(response_times)) / max(len(response_times), 1))


def generate_span_trees(traces: list) -> list:
    """
    Generates a list of SpanTree's from a list of traces.

    :param traces: The list of traces.
    :return: The list of SpanTree's.
    """
    span_trees = list()

    for trace in traces:
        span_tree_obj = SpanTree()
        span_tree_obj.generate_span_tree(trace)
        span_trees.append(span_tree_obj)

    return span_trees


def extract_metrics(span_trees) -> TraceMetricsData:
    """
    Extracts all metrics needed from a list of SpanTree's.

    :param span_trees: The list of SpanTree's.
    :return: The TraceMetricsData object.
    """
    trace_metrics_data = TraceMetricsData()

    for span_tree_obj in span_trees:
        __calculate_trace_metrics_data(trace_metrics_data, span_tree_obj)

    return trace_metrics_data
