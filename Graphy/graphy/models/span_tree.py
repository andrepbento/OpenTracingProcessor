"""
    Author: André Bento
    Date last modified: 22-03-2019
"""

from treelib import Tree
from treelib.exceptions import NodeIDAbsentError

from graphy.models import span as my_span
from graphy.utils import logger as my_logger

logger = my_logger.setup_logging(__name__)


class SpanTree(object):
    """ SpanTree object is a representation of spans in a tree. """

    def __init__(self):
        """Initiate a new SpanTree. """
        self.trace_id = None
        self.span_tree = None
        self.orphan_spans = list()

    def count_spans(self):
        """
        Counts the number of spans in the span tree.

        :return: The number of spans in the span tree.
        """
        return self.span_tree.size()

    def depth(self) -> int:
        """
        Calculates the maximum depth of the span tree.

        :return: The maximum depth of the span tree.
        """
        return self.span_tree.depth(self.span_tree)

    def generate_span_tree(self, trace: list, show_span_tree: bool = False):
        """
        Generates a span tree from a collection of traces.

        :param trace: A list of spans from a trace.
        :param show_span_tree: Show span tree or not.
        """
        trace_id = None
        span_tree = Tree()

        for span in trace:
            try:
                if trace_id and trace_id != span.get('traceId', None):
                    raise Exception('Multiple trace id')
                else:
                    trace_id = span.get('traceId', None)

                parent_id = span.get('parentId', None)
                span_id = span.get('id', None)

                node = span_tree.get_node(span_id)
                if node:
                    span_obj: my_span.Span = node.data
                    span_obj.spans_data.append(span)
                else:
                    span_obj = my_span.Span(id=span_id, parent_id=parent_id)
                    span_obj.spans_data.append(span)
                    span_tree.create_node(identifier=span_id, parent=parent_id, data=span_obj)
            except NodeIDAbsentError:
                self.orphan_spans.append(span_obj)
            except Exception as ex:
                logger.error('{}: {}'.format(type(ex), ex))

        self.trace_id = trace_id
        self.span_tree = span_tree

        if show_span_tree:
            span_tree.show(idhidden=False)
