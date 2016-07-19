from docutils.parsers.rst import Directive
from sphinx.directives.code import CodeBlock
from sqlalchemy.dialects import postgresql
from nthuion.models.meta import Base
from sqlalchemy.schema import CreateTable, CreateIndex

import itertools


class SchemaDirective(Directive):

    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def run(self):
        dialect = postgresql.dialect()
        res = []
        for table in Base.metadata.sorted_tables:
            cb = CodeBlock(*self.args, **self.kwargs)
            cb.arguments = ['postgresql']
            cb.content = itertools.chain(
                [str(CreateTable(table).compile(dialect=dialect))],
                (
                    str(CreateIndex(index).compile(dialect=dialect))
                    for index in table.indexes
                )
            )
            res.extend(cb.run())
        return res


def setup(app):
    app.add_directive('schema', SchemaDirective)
