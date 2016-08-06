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

from functools import singledispatch
from voluptuous import (
    Required, Optional, All, Any, Length, Range, Coerce, UNDEFINED
)

from nthuion.introspect import r1
from nthuion.views.base import not_allowed


@singledispatch
def parse_left(obj):
    raise NotImplementedError(obj)


@parse_left.register(Required)
def _parse_left_required(obj):
    return obj.schema, True, obj.default


@parse_left.register(Optional)
def _parse_left_optional(obj):
    return obj.schema, False, obj.default


@singledispatch
def parse_right(obj):
    raise NotImplementedError(obj)


@parse_right.register(Coerce)
def _parse_right_coerce(obj):
    return parse_right(obj.type)


@parse_right.register(type)
def _parse_right_type(obj):
    return {
        int: 'integer',
        str: 'string',
        bool: 'boolean'
    }[obj]


@parse_right.register(type(None))
def _parse_right_null(obj):
    return '``null``'


@parse_right.register(Length)
def _parse_right_length(obj):
    if obj.min is None:
        return 'length ≤ {}'.format(obj.max)
    elif obj.max is None:
        return '{} ≤ length'.format(obj.min)
    else:
        return '{} ≤ length ≤ {}'.format(obj.min, obj.max)


@parse_right.register(Range)
def _parse_right_range(obj):
    if obj.min is None:
        return 'x ≤ {}'.format(obj.max)
    elif obj.max is None:
        return '{} ≤ x'.format(obj.min)
    else:
        return '{} ≤ x ≤ {}'.format(obj.min, obj.max)


@parse_right.register(int)
def _parse_right_int(obj):
    return '``{}``'.format(obj)


@parse_right.register(All)
def _parse_right_all(obj):
    return ', '.join(parse_right(validator) for validator in obj.validators)


@parse_right.register(Any)
def _parse_right_any(obj):
    return ' or '.join(parse_right(validator) for validator in obj.validators)


@parse_right.register(list)
def _parse_right_list(obj):
    assert len(obj) == 1
    return 'array of [{}]'.format(parse_right(obj[0]))


def schema_to_docstring(schema, directive='reqjson'):
    for l, r in sorted(schema.items()):
        key, required, default = parse_left(l)
        desc = parse_right(r)
        if default is UNDEFINED:
            default_desc = ''
        else:
            default_desc = ', default = ``{}``'.format(
                {None: 'null'}.get(default(), repr(default()))
            )
        required_desc = '' if required else 'optional '
        yield ':{} {}{}: {}{}'.format(
            directive, required_desc, key, desc, default_desc)


class AutoAPIDirective(Directive):

    has_content = True
    required_arguments = 1

    def make_rst(self):
        for name, path, vcallable in r1():

            if not path.startswith(self.arguments[0]):
                continue

            yield name.capitalize()
            yield '-' * len(name)
            yield vcallable.__doc__ or ''

            for method in ('get', 'post', 'put', 'delete'):

                implementation = getattr(vcallable, method)

                if implementation is not_allowed:
                    continue

                docstring = getattr(vcallable, method).__doc__ or ''
                # if not docstring and 'include-empty-docstring' not in self.options:  # noqa
                #     continue
                docstring = prepare_docstring(docstring)

                schema = getattr(implementation, 'schema', None)
                if schema is not None:
                    docstring += ['']
                    docstring += list(schema_to_docstring(schema))

                qs_schema = getattr(implementation, 'qs_schema', None)
                if qs_schema is not None:
                    docstring += ['']
                    docstring += list(schema_to_docstring(qs_schema, 'query'))

                reqp = getattr(implementation, 'requires_permission', None)
                if reqp is not None:
                    docstring = [
                        'requires permission: ``{}``'.format(reqp),
                        ''
                    ] + docstring

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
