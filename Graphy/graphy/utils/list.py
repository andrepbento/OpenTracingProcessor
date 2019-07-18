"""
    Author: André Bento
    Date last modified: 1-04-2019
"""


def diff(list_1, list_2):
    return list(set(list_1).difference(set(list_2)))


def symmetric_diff(list_1, list_2):
    """
    Performs the difference between two lists. In this context the difference is what is in list_1 but not in list_2,
    and what is in list_2 but not in list_1.

    :param list_1: The first list.
    :param list_2: The second list.
    :return: A list with the difference between the first and second lists.
    """
    return list(set(list_1).symmetric_difference(set(list_2)))


def tuple_list(values: list):
    tuple_list_result = list()
    aux_value = values[0]
    for value in values:
        if aux_value == value:
            continue
        tuple_list_result.append((aux_value, value))
        aux_value = value
    return tuple_list_result
