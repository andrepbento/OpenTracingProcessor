"""
    Author: André Bento
    Date last modified: 22-03-2019
"""
from datetime import datetime, timezone

from graphy.utils import config as my_config

graphy_config = my_config.get('GRAPHY')

date_format = '%d/%m/%Y %H:%M:%S'


def to_unix_time(date_time_str):
    """
    :param date_time_str: time in @date_format string format.
    :return: unix time in seconds.
    """
    date_time = datetime.strptime(date_time_str, date_format)
    dt = datetime(date_time.year, date_time.month, date_time.day,
                  date_time.hour, date_time.minute, date_time.second)
    unix_time = dt.replace(tzinfo=timezone.utc).timestamp()
    return int(round(unix_time))


def to_unix_time_millis(date_time_str):
    """
    :param date_time_str: time in @date_format string format.
    :return: unix time in milliseconds.
    """
    return to_unix_time(date_time_str) * 1000


def from_str_to_datetime(date_time_str):
    """
    :param date_time_str: time in @date_format string format.
    :return: date time object.
    """
    return datetime.strptime(date_time_str, date_format)


def from_timestamp_to_datetime(timestamp, unit='ms'):
    """
    :param timestamp: timestamp in unix format.
    :param unit: measurement unit used in the timestamp.
    :return: the timestamp in date_time format.
    """
    import pandas
    return pandas.to_datetime(timestamp, unit=unit)


def timestamp_millis_split(init_timestamp, end_timestamp,
                           interval_time=graphy_config.get('TIMESTAMP_RESOLUTION', 60 * 60 * 1000)):
    """
    Creates a list of timestamps in milliseconds from a given initial timestamp to a given end timestamp.

    :param init_timestamp: the initial timestamp in milliseconds.
    :param end_timestamp: the end timestamp in milliseconds.
    :param interval_time: the interval timestamp in milliseconds.
    :return: a list of every timestamp in the interval.
    """
    timestamp_list = list([init_timestamp])
    while init_timestamp < end_timestamp:
        init_timestamp += interval_time
        timestamp_list.append(init_timestamp)
    return timestamp_list
