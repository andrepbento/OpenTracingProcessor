"""
    Author: André Bento
    Date last modified: 04-03-2019
"""
import sys

import potsdb
import requests

from graphy.utils import config
from graphy.utils import logger as my_logger

try:
    import simplejson as json
except ImportError:
    import json

logger = my_logger.setup_logging(__name__)

opentsdb_config = config.get('OPENTSDB')

opentsdb_address = '{}://{}:{}/'.format(opentsdb_config['PROTOCOL'], opentsdb_config['HOST'], opentsdb_config['PORT'])
api_query = 'api/query'


def format_metric_name(naming_list):
    """
    Format the metric name.

    :param naming_list: List of names to append to the metric_name.
    :return: The metric name.
    """
    metric_name = '{}'.format(opentsdb_config['STORE_NAME'])
    for name in naming_list:
        metric_name += '.{}'.format(name)
    return metric_name


def erase_metrics(name: str, start_timestamp: int, end_timestamp: int) -> object:
    """
    Erases metrics from OpenTSDB.

    :param name: Metric name.
    :param start_timestamp: Start unix timestamp value.
    :param end_timestamp: End unix timestamp value.
    :return: The erased metrics if success, None otherwise.
    """
    if end_timestamp < start_timestamp:
        return False

    data = None
    try:
        params = {'start': start_timestamp, 'end': end_timestamp, 'm': 'avg:1m-avg:{}'.format(name)}
        response = requests.delete(opentsdb_address + api_query, params=params)
        if response.status_code == 200:
            response_text = json.loads(response.text)
            if response_text:
                data = response_text[0].get('dps', None)
        return data
    except ConnectionError as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        return None


def get_metrics(name: str, start_timestamp: int, end_timestamp: int) -> object:
    """
    Gets the metrics from OpenTSDB.

    :param name: The name of the metrics.
    :param start_timestamp: The start unix timestamp of the metric.
    :param end_timestamp: The end unix timestamp of the metric.
    :return: The metrics as a dictionary if success, None otherwise.
    """
    json_body = {
        "start": start_timestamp,
        "end": end_timestamp,
        "queries": [{"aggregator": "sum", "metric": name},
                    {"aggregator": "sum", "tsuids": ["000001000002000042", "000001000002000043"]}]
    }

    data = None
    try:
        response = requests.post(opentsdb_address + api_query, data=json.dumps(json_body),
                                 headers={'content-type': 'application/json'})
        if response.status_code == 200:
            response_text = json.loads(response.text)
            if response_text:
                data = response_text[0].get('dps', None)
        return data
    except ConnectionError as ex:
        logger.error('{}: {}'.format(type(ex), ex))
        sys.exit(status=1)


def send_numeric_metrics(label: str, metrics, metric_timestamp: int) -> list:
    """
    Sends a collection of metrics to the Time-Series database.

    :param label: The pre label of the metric in string format. Ex.: degree or status_code
    :param metrics: The list of the metrics. Each metric must be a tuple. Ex.: service: value.
    :param metric_timestamp: The metric unix timestamp.
    :return: Metric names if success, Empty list otherwise.
    """
    metric_names = []
    if isinstance(metrics, list):
        for tuple_item in metrics:
            x, y = tuple_item
            send_numeric_metric([label, x], y, metric_timestamp)
    elif isinstance(metrics, dict):
        for k, v in metrics.items():
            send_numeric_metric([label, k], v, metric_timestamp)
    return metric_names


def send_numeric_metric(metric_naming_list: list, metric_value, metric_timestamp: int) -> bool:
    """
    Sends a single metric to the Time-Series database.

    :param metric_naming_list: The metric naming list.
    :param metric_value: The metric value in float, integer, or string (convertible to float or integer) format.
    :param metric_timestamp: The metric unix timestamp.
    :return: True if success, False otherwise.
    """
    metric_name = format_metric_name(metric_naming_list)
    try:
        client = potsdb.Client(host=opentsdb_config['HOST'], port=opentsdb_config['PORT'], check_host=True)
        client.log(name=metric_name, val=metric_value, timestamp=metric_timestamp)
        client.close()
        return True
    except Exception as e:
        logger.error(e)
        return False
