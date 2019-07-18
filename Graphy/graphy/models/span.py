"""
    Author: André Bento
    Date last modified: 20-03-2019

Fields:
-------
* traceId - unique id of a trace, 128-bit string
* name - human-readable title of instrumented function
* timestamp - UNIX epoch in milliseconds
* id - unique id of a span, 64-bit string
* parentId - reference to id of parent span
* duration - span duration in microseconds
* binaryAnnotations:
  ** protocol - `HTTP` or `function` for RPC calls
  ** http.url - HTTP endpoint
  ** http.status_code - result of HTTP operation
* annotations:
  ** value - describes the position in trace (based on Zipkin format):
     `cs` - client send
     `cr` - client receive
     `ss` - server send
     `sr` - server receive
  ** timestamp - UNIX epoch in microseconds
  ** endpoint - which endpoint generated a trace event

Notes:
1. Time units are not consistent, some fields are in milliseconds and some are in microseconds
2. Trace spans may contain more fields, except those mentioned here
"""

from graphy.utils import dict as my_dict
from graphy.utils import logger as my_logger

try:
    import simplejson as json
except ImportError:
    import json

logger = my_logger.setup_logging(__name__)


class Span(object):
    def __init__(self, id: str, parent_id: str = None, spans_data: list = None):
        if spans_data is None:
            spans_data = list()

        self.parent_id = parent_id
        self.id = id
        self.spans_data = spans_data

    def get_durations(self):
        durations = list()
        for span_data in self.spans_data:
            durations.append(span_data.get('duration', 0))
        return durations


def fix_timestamps(spans: list):
    """
    Fixes multiple timestamp values in a span list.

    :param spans: The span list.
    """
    timestamp = 'timestamp'

    for span in spans:
        my_dict.update(span, timestamp, fix_timestamp)


def fix_timestamp(timestamp):
    """
    Fix timestamp values, due to a len issue when posting them to Zipkin.

    :param timestamp: The unix timestamp format.
    """
    default_timestamp_len = 16
    if len(str(timestamp)) < default_timestamp_len:
        miss_len = default_timestamp_len - len(str(timestamp))
        timestamp = str(timestamp) + ''.join(['0' for _ in range(miss_len)])
        return int(timestamp)
    return timestamp


def get_status_code(span):
    try:
        tags = span.get('tags', False)
        if tags:
            http_status_code = tags.get('http.status_code', False)
            return http_status_code
        return tags
    except Exception as e:
        logger.error(e)
        return False
