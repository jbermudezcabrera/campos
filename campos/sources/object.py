import datetime as dt
from collections import OrderedDict

from . import (FieldSource, from_bool, from_int, from_float, from_str,
               from_date, from_time, from_datetime)

__author__ = 'Juan Manuel Bermúdez Cabrera'


class ObjectSource(FieldSource):
    """Generic field source for all kinds of objects, this is the fallback
    class when more fitted sources can't be found.

    .. seealso:: :class:`~.sqlalchemy.SQLAlchemySource`
    """
    def create_fields(self, attributes):
        # exclude attributes with unsupported values
        filtered = OrderedDict()
        for attr, text_value in attributes.items():
            text, value = text_value
            if type(value) in self.SUPPORTED_TYPES:
                filtered[attr] = text, value

        fields = OrderedDict()
        for attr, text_value in filtered.items():
            field = None
            text, value = text_value

            if isinstance(value, bool):
                field = from_bool(attr, text, value)

            elif isinstance(value, int):
                field = from_int(attr, text, value)

            elif isinstance(value, float):
                field = from_float(attr, text, value)

            elif isinstance(value, str):
                field = from_str(attr, text, value)

            elif isinstance(value, dt.datetime):
                field = from_datetime(attr, text, value)

            elif isinstance(value, dt.date):
                field = from_date(attr, text, value)

            elif isinstance(value, dt.time):
                field = from_time(attr, text, value)

            if field is not None:
                fields[field.name] = field
        return fields
