"""
    Author: André Bento
    Date last modified: 26-02-2019
"""
import os
from os.path import join

from graphy.models import span

try:
    import simplejson as json
except ImportError:
    import json


def is_json(file_path):
    """
    Checks if a certain file path is JSON.

    :param file_path: The file path.
    :return: True if it is JSON, False otherwise.
    """
    return file_path.endswith('.json')


def to_json(file_path, limit=None):
    """
    Converts a file to JSON.

    :param file_path: The file path.
    :param limit: Limit the number of entries to convert to the new file.
    :return: The file path of the created file.
    """
    if is_json(file_path):
        return file_path

    with open(file_path) as fp:
        lines = fp.readlines()

    lines = list(
        map(
            lambda x: json.loads(x.strip()),
            lines
        )
    )

    if limit:
        lines = lines[:limit]

    span.fix_timestamps(lines)

    json_array = json.dumps(lines)

    dir_path = os.path.dirname(os.path.realpath(file_path))
    file_name = os.path.splitext(file_path)[0]
    new_abs_file_path = join(dir_path, file_name + '.json')

    with open(new_abs_file_path, 'w') as f:
        f.write(json_array)

    return new_abs_file_path
