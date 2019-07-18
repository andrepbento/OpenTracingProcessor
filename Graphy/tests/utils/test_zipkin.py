"""
    Author: André Bento
    Date last modified: 06-03-2019
"""

from unittest import TestCase

from graphy.utils import zipkin


class TestZipkin(TestCase):

    def test_ZipkinTraceLimit(self):
        """ Test ZipkinTraceLimit exception. """
        with self.assertRaises(zipkin.ZipkinTraceLimit):
            raise zipkin.ZipkinTraceLimit(1000)

    def test_get_services(self):
        """ Test get_services function. """
        # TODO: Write tests.
        pass

    def test_get_spans(self):
        """ Test get_spans function. """
        # TODO: Write tests.
        pass

    def test_post_spans(self):
        """ Test post_spans function. """
        # TODO: Write tests.
        pass

    def test_get_traces(self):
        """ Test get_traces function. """
        # TODO: Write tests.
        pass

    def test_get_trace(self):
        """ Test get_trace function. """
        # TODO: Write tests.
        pass

    def test_get_dependencies(self):
        """ Test get_dependencies function. """
        # TODO: Write tests.
        pass
