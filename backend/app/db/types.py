from sqlalchemy import JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import TypeDecorator


class JSONBCompat(TypeDecorator):
    """JSONB on Postgres, JSON elsewhere (for sqlite tests)."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.JSONB())
        return dialect.type_descriptor(JSON())
