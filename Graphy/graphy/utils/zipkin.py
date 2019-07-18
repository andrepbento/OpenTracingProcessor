"""
    Author: André Bento
    Date last modified: 07-03-2019
"""
import sys
import time

import requests

from graphy.utils import config
from graphy.utils import files as my_files
from graphy.utils import logger as my_logger

try:
    import simplejson as json
except ImportError:
    import json

logger = my_logger.setup_logging(__name__)

zipkin_config = config.get('ZIPKIN')

zipkin_protocol = zipkin_config['PROTOCOL']
zipkin_address = zipkin_config['ADDRESS']
base_address = '{}://{}'.format(zipkin_protocol, zipkin_address)
api_v1_endpoint = zipkin_config['API_V1']
api_v2_endpoint = zipkin_config['API_V2']

address_v1 = base_address + api_v1_endpoint
address_v2 = base_address + api_v2_endpoint

headers = {'content-type': 'application/json'}


class ZipkinTraceLimit(Exception):
    """ Exception for Zipkin request trace limit. # """

    def __init__(self, trace_len: int) -> None:
        super(ZipkinTraceLimit, self).__init__('trace limit exceeded with {} traces'.format(trace_len))


def get_services():
    """
    Get all the service names from the Zipkin API.

    :return: A list with all services presented in Zipkin.
    """
    try:
        response = requests.get(address_v2 + 'services')
        return json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        sys.exit(status=1)


def get_spans(service_name: str) -> list:
    """
    Get all the span names recorded by a particular service from the Zipkin API.

    :param service_name: Ex api_com (required) - Lower-case label of a node in the service graph. The /services endpoint
    enumerates possible input values.
    :return: the spans data
    """
    try:
        params = {'serviceName': service_name}
        response = requests.get(address_v2 + 'spans', params)
        return json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        sys.exit(status=1)


def post_spans(spans_file):
    """
    Post the spans utils file to the Zipkin API if it's not already there.

    :param spans_file: spans file path.
    :return: True if the operation was successful (equal to HTTP code 202), False otherwise.
    """
    if not zipkin_config['POST_DATA']:
        return True
    try:
        spans_data = my_files.read_file(spans_file)
        response = requests.post(address_v1 + 'spans', data=spans_data, headers=headers)
        return response.status_code == 202
    except Exception as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        sys.exit(status=1)


def get_traces(lookback=365 * 24 * 60 * 60 * 1000, service_name=None, span_name=None, annotation_query=None,
               min_duration=None, max_duration=None, end_ts=None, limit=zipkin_config.get('TRACE_LIMIT')):
    """
    Get all the traces from the Zipkin API.

    :param lookback: Only return traces where all Span.timestamp are at or after (endTs lookback) in milliseconds.
    Defaults to endTs, limited to a system parameter QUERY_LOOKBACK. Default 1 year in milliseconds.
    :param service_name: Ex api_com (required) - Lower-case label of a node in the service graph. The /services endpoint
    enumerates possible input values.
    :param span_name: Ex get - name of a span in a trace. Only return traces that contains spans with this name.
    :param annotation_query: Ex. http.uri=/foo and retried - If key/value (has an =), constrains against Span.tags
    entries. If just a word, constrains against Span.annotations[].value or Span.tags[].key. Any values are AND against
    each other. This means a span in the trace must match all of these.
    :param min_duration: Ex. 100000 (for 100ms). Only return traces whose Span.duration is greater than or equal to
    minDuration microseconds.
    :param max_duration: Only return traces whose Span.duration is less than or equal to maxDuration microseconds. Only
    valid with minDuration.
    :param end_ts: Only return traces where all Span.timestamp are at or before this time in epoch milliseconds.
    Defaults to current time.
    :param limit: Maximum number of traces to return. Defaults to 10
    :return: list of traces with respect to the provided parameters.
    """
    try:
        params = {
            'serviceName': service_name,
            'spanName': span_name,
            'annotationQuery': annotation_query,
            'minDuration': min_duration,
            'maxDuration': max_duration,
            'endTs': int(time.time()) if end_ts is None else end_ts,
            'lookback': lookback,
            'limit': limit
        }
        response = requests.get(address_v2 + 'traces', params)
        return json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        sys.exit(status=1)


def get_trace(trace_id):
    """
    Get the trace with the provided trace id.

    :param trace_id: Trace identifier, set on all spans within it
    :return: the trace data
    """
    response = requests.get(address_v2 + 'trace/{}'.format(trace_id))
    return json.loads(response.text)


def get_dependencies(end_ts, lookback=60 * 60 * 1000):
    """
    Get all the dependencies from the Zipkin API.
    :param end_ts: End timestamp in milliseconds.
    :param lookback: Timestamp in milliseconds of lookback, 1 hour default.
    :return: the dependencies data or None
    """
    try:
        params = {'endTs': end_ts, 'lookback': lookback}
        response = requests.get(address_v2 + 'dependencies', params)
        return None if response.status_code != 200 else json.loads(response.text)
    except ConnectionError as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        sys.exit(status=1)
