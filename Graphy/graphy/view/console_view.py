"""
    Author: André Bento
    Date last modified: 26-02-2019
"""


class ConsoleView(object):

    @staticmethod
    def start_view():
        print('\nGraphy started')

    @staticmethod
    def end_view():
        print('\nGraphy exited!\nGoodbye!')

    @staticmethod
    def show_number_point_list(item_type: str, items: dict):
        print('\n--- {} list ---'.format(item_type.upper()))
        for i, item in enumerate(items):
            print('{}. {}'.format(i + 1, item))

    @staticmethod
    def show_select_time_interval():
        return NotImplemented

    @staticmethod
    def display_dictionary(label, dictionary):
        print('\n--- {} ---'.format(label))
        for key in dictionary:
            print(key)
            values = dictionary[key]
            if isinstance(values, int):
                print(values)
            elif isinstance(values, dict):
                for i, y in enumerate(values):
                    print((i + 1), ':', y)

    @staticmethod
    def display_exception(exception):
        print('\n--- Exception ---')
        print('{}'.format(exception))

    @staticmethod
    def display_message(label, message):
        print('\n--- {} ---'.format(label))
        print('{}'.format(message))

    @staticmethod
    def display_tuple(label, tuple_item):
        print('\n--- {} ---'.format(label))
        x, y = tuple_item
        print('{}: {}'.format(x, y))

    @staticmethod
    def display_tuple_list(label, tuple_list):
        print('\n--- {} ---'.format(label))
        for tuple_item in tuple_list:
            x, y = tuple_item
            print('{}: {}'.format(x, y))

    @staticmethod
    def display_time(label, date_time=None, timestamp=None):
        if date_time is None or timestamp is None:
            print('\n{}: {}'.format(label, date_time))
        else:
            print('\n{}: {} --> Timestamp: {}'.format(label, date_time, timestamp))
