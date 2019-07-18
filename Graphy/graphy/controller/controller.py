"""
    Author: André Bento
    Date last modified: 08-04-2019
"""
import os
import sys
import time

from graphy.controller import controller_logic as cl
from graphy.models import trace as my_trace
from graphy.utils import config, files
from graphy.utils import json as my_json
from graphy.utils import list as my_list
from graphy.utils import logger as my_logger
from graphy.utils import time as my_time
from graphy.utils import zipkin

logger = my_logger.setup_logging(__name__)

graphy_config = config.get('GRAPHY')


class Controller(object):
    def __init__(self, view, model=None):
        self.model = model
        self.view = view

        self.__start_date_time_str = graphy_config.get('DEFAULT_START_TIME')
        self.__end_date_time_str = graphy_config.get('DEFAULT_END_TIME')

        self.__is_zipkin = graphy_config.get('ACTIVATE_ZIPKIN')

    def start(self):
        """ Starts the controller. """
        self.view.start_view()

        while True:
            switcher = {
                'Show service neighbours':
                    self.show_service_neighbours,
                'Show service neighbours in time (EXPERIMENTAL)':
                    self.show_service_neighbours_in_time,
                'Show most popular service [degree]':
                    self.show_most_popular_service,
                'Show most popular service [degree] in time (EXPERIMENTAL)':
                    self.show_most_popular_service_degree_in_time,
                'Show most popular service [call count]':
                    self.show_most_popular_service_call_count,
                'Show most popular service [call count] in time (EXPERIMENTAL)':
                    self.show_most_popular_service_call_count_in_time,
                'Show service status code analysis':
                    self.show_service_status_codes_analysis,
                'Show service status code analysis in time (EXPERIMENTAL)':
                    self.show_service_status_code_analysis_in_time,
                'Gather and show tracing quality analysis [Time coverability and structural testing] (EXPERIMENTAL)':
                    self.show_trace_quality_analysis,
                'Show response time analysis (NOT IMPLEMENTED)':
                    self.show_response_time_analysis,
                'Show morphology analysis (EXPERIMENTAL)':
                    self.show_morphology_analysis_in_time,
                'Show request work-flow analysis (NOT IMPLEMENTED)':
                    self.show_request_work_flow_analysis,
                'Show service order distribution analysis (NOT IMPLEMENTED)':
                    self.show_service_order_distribution_analysis,
                'Show load analysis (NOT IMPLEMENTED)':
                    self.show_load_analysis,
                'Show clients request analysis (NOT IMPLEMENTED)':
                    self.show_clients_request_analysis,
                'Gather and show all metrics in time (EXPERIMENTAL) [neighbours, degree, call count, status codes]':
                    self.show_all_metrics,
                'Exit':
                    self.__end
            }

            self.__show_options('Graphy options', switcher)
            user_input = input('>>> ')

            if user_input in range(1, len(switcher)):
                self.view.display_message('Invalid option!', 'Option not valid, please try again.')
                continue
            else:
                try:
                    execute_selected = list(switcher.items())[int(user_input) - 1]
                    execute_selected[1]()
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    logger.error(e)
                    self.view.display_exception('{} {} {}'.format(exc_type, file_name, exc_tb.tb_lineno))

    def __end(self):
        """ Terminates the controller. """
        self.view.end_view()
        exit(1)

    def __show_options(self, title: str, options: dict) -> None:
        """
        Shows options using the view.

        :param title: The title of the options menu.
        :param options: The list of options.
        """
        self.view.show_number_point_list(title, options)

    def setup_zipkin(self, trace_file: str):
        """
        Setup Zipkin with a certain trace file, if data is not already in it.

        :param trace_file: The trace file absolute path.
        """
        trace_file_path = files.get_absolute_path(trace_file, graphy_config.get('TRACE_FILE_FROM_PROJECT'))

        if not my_json.is_json(trace_file_path):
            self.view.display_message('Converting file to JSON', 'file: {}'.format(trace_file_path))
            trace_file_path = my_json.to_json(trace_file_path)
            self.view.display_message('File converted to JSON', 'file: {}'.format(trace_file_path))

        if trace_file_path:
            logger.debug('Using file: {}'.format(trace_file_path))
            print('Posting file: {} to Zipkin -> {}'.format(trace_file_path, zipkin.base_address))

            if not zipkin.post_spans(trace_file_path):
                logger.error('error posting data to zipkin')
                exit(1)

    def show_service_neighbours(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time', my_time.from_str_to_datetime(self.__start_date_time_str),
                                   start_timestamp)
            self.view.display_time('end_time', my_time.from_str_to_datetime(self.__end_date_time_str),
                                   end_timestamp)

            dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)

            message = cl.service_neighbours(dependencies, start_timestamp, end_timestamp)
            self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_service_neighbours_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time', my_time.from_str_to_datetime(self.__start_date_time_str),
                                   start_timestamp)
            self.view.display_time('end_time', my_time.from_str_to_datetime(self.__end_date_time_str),
                                   end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)
            timestamps = my_list.tuple_list(timestamps)

            for timestamp_1, timestamp_2 in timestamps:
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2)

                message = cl.service_neighbours(dependencies, timestamp_1, timestamp_2)
                self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_most_popular_service(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)

            message = cl.service_degree(dependencies, start_timestamp, end_timestamp)
            self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_most_popular_service_degree_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)
            timestamps = my_list.tuple_list(timestamps)

            for timestamp_1, timestamp_2 in timestamps:
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)

                message = cl.service_degree(dependencies, timestamp_1, timestamp_2)
                self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_most_popular_service_call_count(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            dependencies = zipkin.get_dependencies(end_ts=end_timestamp, lookback=end_timestamp - start_timestamp)

            message = cl.service_call_count(dependencies, start_timestamp, end_timestamp)
            self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_most_popular_service_call_count_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)
            timestamps = my_list.tuple_list(timestamps)

            print(len(timestamps))

            for timestamp_1, timestamp_2 in timestamps:
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)

                message = cl.service_call_count(dependencies, timestamp_1, timestamp_2)
                self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_service_status_codes_analysis(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            service_names = zipkin.get_services()

            for service_name in service_names:
                traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                           lookback=end_timestamp - start_timestamp)

                message = cl.service_status_codes(service_name, traces, start_timestamp, end_timestamp)
                self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_service_status_code_analysis_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            service_names = zipkin.get_services()

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)
            timestamps = my_list.tuple_list(timestamps)

            for timestamp_1, timestamp_2 in timestamps:
                for service_name in service_names:
                    traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                               lookback=end_timestamp - start_timestamp)

                    message = cl.service_status_codes(service_name, traces, timestamp_1, timestamp_2)
                    self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_trace_quality_analysis(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            service_names = zipkin.get_services()

            for service_name in service_names:
                traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                           lookback=end_timestamp - start_timestamp)

                message = cl.trace_quality_analysis(traces, service_name, start_timestamp, end_timestamp)
                self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_response_time_analysis(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            service_names = zipkin.get_services()

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)
            timestamps = my_list.tuple_list(timestamps)

            for timestamp_1, timestamp_2 in timestamps:
                # TODO: IMPROVE DATA USAGE.
                for service_name in service_names:
                    traces = zipkin.get_traces(service_name=service_name, end_ts=end_timestamp,
                                               lookback=end_timestamp - start_timestamp)

                    span_trees = my_trace.generate_span_trees(traces)
                    trace_metrics_data = my_trace.extract_metrics(span_trees)

                    message = cl.service_response_time_analysis(service_name, trace_metrics_data, timestamp_1,
                                                                timestamp_2)
                    self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_morphology_analysis_in_time(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)
            timestamps = my_list.tuple_list(timestamps)

            for timestamp_1, timestamp_2 in timestamps:
                dependencies = zipkin.get_dependencies(end_ts=timestamp_2, lookback=timestamp_2 - timestamp_1)

                message = cl.service_morphology(dependencies, timestamp_1, timestamp_2)
                self.view.display_message(message[0], message[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))

    def show_request_work_flow_analysis(self):
        # TODO: Analise the requests from the graphs || spans (How?)
        return NotImplemented

    def show_service_order_distribution_analysis(self):
        return NotImplemented

    def show_load_analysis(self):
        return NotImplemented

    def show_clients_request_analysis(self):
        return NotImplemented

    def show_all_metrics(self):
        if self.__is_zipkin:
            start_time = time.time()

            start_timestamp = my_time.to_unix_time_millis(self.__start_date_time_str)
            end_timestamp = my_time.to_unix_time_millis(self.__end_date_time_str)

            self.view.display_time('start_time:', my_time.from_timestamp_to_datetime(start_timestamp),
                                   start_timestamp)
            self.view.display_time('end_time:', my_time.from_timestamp_to_datetime(end_timestamp), end_timestamp)

            timestamps = my_time.timestamp_millis_split(start_timestamp, end_timestamp)

            service_names = zipkin.get_services()

            timestamps = my_list.tuple_list(timestamps)

            print(len(timestamps))

            for timestamp_tuple in timestamps:
                cl.process_all_metrics_in_time(service_names, timestamp_tuple[0], timestamp_tuple[1])

            self.view.display_message('Time processing', 'finish in {} seconds'.format(time.time() - start_time))
