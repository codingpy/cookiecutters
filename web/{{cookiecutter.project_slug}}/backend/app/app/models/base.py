import re

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    # Generate __tablename__ automatically
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return to_snake(cls.__name__)


def to_snake(s):
    return re.sub("(?<=[^_])((?=[A-Z][a-z])|(?<=[^A-Z])(?=[A-Z]))", "_", s).lower()
