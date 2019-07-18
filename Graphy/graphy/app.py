"""
    Author: André Bento
    Date last modified: 26-02-2019
"""
import multiprocessing

from graphy.controller.controller import Controller
from graphy.utils import config
from graphy.view.console_view import ConsoleView


class Graphy(object):

    @staticmethod
    def run():
        graphy_config = config.get('GRAPHY')

        trace_files = graphy_config.get('TRACE_FILES')

        view = ConsoleView()
        controller = Controller(view)

        processes = []
        for trace_file in trace_files:
            p = multiprocessing.Process(target=controller.setup_zipkin, args=(trace_file,))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()

        controller.start()
