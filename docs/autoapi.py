"""
    adapted from sphinxcontrib.autohttp.tornado

    The sphinx.ext.autodoc-style HTTP API reference builder (from Tornado)
    for sphinxcontrib.httpdomain.

    :copyright: Copyright 2013 by Rodrigo Machado
    :license: BSD, see LICENSE for details.

"""

from docutils import nodes
from docutils.statemachine import ViewList

from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.util.docstrings import prepare_docstring

from sphinxcontrib import httpdomain
from sphinxcontrib.autohttp.common import http_directive

from nthuion.introspect import r1
from nthuion.views.base import not_allowed


class AutoAPIDirective(Directive):

    has_content = True
    required_arguments = 0

    def make_rst(self):
        for name, path, vcallable in r1():

            yield name.capitalize()
            yield '-' * len(name)
            yield vcallable.__doc__ or ''

            for method in ('get', 'post', 'put', 'delete'):

                if getattr(vcallable, method) is not_allowed:
                    continue

                docstring = getattr(vcallable, method).__doc__ or ''
                # if not docstring and 'include-empty-docstring' not in self.options:  # noqa
                #     continue
                docstring = prepare_docstring(docstring)
                for line in http_directive(method, path, docstring):
                    yield line

    def run(self):
        node = nodes.section()
        node.document = self.state.document
        result = ViewList()
        for line in self.make_rst():
            result.append(line, '<autoapi>')
        nested_parse_with_titles(self.state, result, node)
        return node.children


def setup(app):
    if 'http' not in app.domains:
        httpdomain.setup(app)
    app.add_directive('autoapi', AutoAPIDirective)
