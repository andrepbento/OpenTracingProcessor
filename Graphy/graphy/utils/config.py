"""
    Author: André Bento
    Date last modified: 21-02-2019
"""
import yaml

from graphy.utils import files


def get(module, file_path='graphy/config.yaml'):
    """
    Gets the configuration settings.

    :param module: The module to filter the configuration.
    :param file_path: The relative path of the configuration file inside the project.
    :return: The configuration of the corresponding module as a dict.
    """
    with open(files.get_absolute_path(file_path, True)) as f:
        config = yaml.safe_load(f.read())
        return config.get(module, dict())
