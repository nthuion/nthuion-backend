from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.schema import MetaData
from sqlalchemy.orm import object_session

# Recommended naming convention used by Alembic, as various different database
# providers will autogenerate vastly different names making migrations more
# difficult. See: http://alembic.readthedocs.org/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


@as_declarative(metadata=metadata)
class Base:

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def object_session(self):
        return object_session(self)
