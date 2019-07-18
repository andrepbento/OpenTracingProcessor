"""
    Author: André Bento
    Date last modified: 21-03-2019
"""
import os
from os.path import dirname

ROOT_PROJECT_DIRECTORY = os.path.join(dirname(dirname(dirname(__file__))))
DATA_PROJECT_DIRECTORY = os.path.join(ROOT_PROJECT_DIRECTORY, 'data')

TRACE_COV_PROJECT_DIRECTORY = os.path.join(DATA_PROJECT_DIRECTORY, 'trace_cov_analysis')


def get_absolute_path(relative_path, from_project=False):
    if from_project:
        relative_path = os.path.join(ROOT_PROJECT_DIRECTORY, relative_path)

    abs_path = os.path.abspath(relative_path)

    if os.path.isfile(abs_path) is True and os.path.exists(abs_path):
        return abs_path
    raise FileNotFoundError(abs_path)


def read_file(path):
    with open(path) as fp:
        file_data = fp.read()
    return file_data


def save_dict(file_path: str, my_dict: dict):
    with open(file_path, 'w') as f:
        for key in my_dict.keys():
            f.write("%s,%s\n" % (key, my_dict[key]))
