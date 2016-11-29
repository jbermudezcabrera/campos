import abc
import re
import inspect
import datetime as dt
from collections import OrderedDict

from .. import fields
from ..utils import callable
from ..validators import (NumberRange, StringLength, DateRange, TimeRange,
                          DatetimeRange)

__author__ = 'Juan Manuel Bermúdez Cabrera'

OLDEST_PERSON = 122  # years
TALLEST_PERSON = 2.72  # m
HEAVIEST_PERSON = 635  # kg


class FieldSource(metaclass=abc.ABCMeta):
    """Base class for field extractors.

    Inspects an object looking for valid attributes to create fields,
    callables are always ignored and extra filters can be provided using
    keyword arguments(``exclude``, ``under``, ``dunder``). Field's text can
    be modified by setting ``prettify=True`` (default) or providing a custom
    transformation function using ``apply`` keyword.

    The following steps are performed when extracting valid object attributes
    to create fields:

    * Non-callable attributes and their values are extracted from the provided
      object.

    * Attribute names are filtered using expressions in ``exclude`` and values
      of ``under`` (beginning with exactly one _) and ``dunder`` (beginning with
      two or more _).

    * A transformation function(if provided through ``apply`` keyword) is used
      to obtain a nice text for the future field using attribute's name.

    * Some simple and common transformations such as _ removal and text
      capitalization are done upon attributes names in order to obtain a nice
      text for the future field. Note this step is performed even if a
      transformation function is provided, to disable this behavior set
      ``pretiffy=False``.

    * Finally only attributes with supported python types can pass, see
      :attr:`SUPPORTED_TYPES`. Subclasses must implement this check accordingly
      since some objects may contain wrapped python types.

    Fields are created after this filtering process, this is done by calling an
    utility function designed for each supported python type.
    See :func:`from_bool`, :func:`from_int`, :func:`from_str`, etc.
    Subclasses must implement :func:`create_fields` for this.

    :param obj: object to extract fields from
    :type obj: any

    :param exclude: regular expressions to exclude, attribute names matching
                    any of these will be ignored.
    :type exclude: iterable of :class:`str` or compiled :mod:`re`

    :param under: whether to allow or not attribute names beginning with
                  exactly one _. Defaults to False.

    :param dunder: whether to allow or not attribute names beginning with two
                   or more _. Defaults to False.

    :param prettify: perform some simple and common transformations such as _
                     removal and text capitalization upon attributes names in
                     order to obtain a nice text for the future field.
                     Defaults to True.

    :param apply: transformation function to apply to each attribute name to
                  obtain a nice text for the future field. Note that if
                  ``prettify=True`` this is done after that step.
    :type apply: callable
    """

    #: Supported python types.
    SUPPORTED_TYPES = (int, float, str, bool, dt.date, dt.time, dt.datetime)

    def __init__(self, obj, exclude=(), under=False, dunder=False,
                 prettify=True, apply=None):
        self.object = obj
        attributes = OrderedDict()  # attr_name --> (text, value)

        # 1: exclude functions
        for attr, value in self.get_members():
            if not callable(value):
                attributes[attr] = attr, value

        # 2: exclude attributes with unwanted names
        excluded_patterns = self._excluded_patterns(exclude, under, dunder)

        for attr in tuple(attributes.keys()):
            for pattern in excluded_patterns:
                if pattern.fullmatch(attr):
                    attributes.pop(attr)
                    break

        # 3: apply given transformation function(if there is one)
        if callable(apply):
            for attr, text_value in attributes.items():
                text = text_value[0]
                value = text_value[1]
                attributes[attr] = apply(text), value

        # 4: prettify attribute's text
        if prettify:
            for attr, text_value in attributes.items():
                text = text_value[0]
                value = text_value[1]
                attributes[attr] = self._prettify(text), value

        self.fields = self.create_fields(attributes)

    def get_members(self):
        """Returns all members of the source object, along with their value.

        :return: a list of tuples (member_name, member_value)
        :rtype: :class:`list`
        """
        return inspect.getmembers(self.object)

    @abc.abstractmethod
    def create_fields(self, attributes):
        """Creates new fields from ``attributes``.

        Subclasses must implement this and check if type of each attribute
        is a supported python type, see :attr:`SUPPORTED_TYPES`.

        In order to create new fields the from_* methods in this module can
        can be useful.

        :param attributes: a dict like d[attr_name] = (attr_text, attr_value)
                           where attr_name will be the new field's name and
                           attr_text its nice text.
        :type attributes: :class:`dict`

        :return: a dict like d[field_name] = field
        :rtype: :class:`dict`
        """
        pass

    @staticmethod
    def _excluded_patterns(exclude, under, dunder):
        patterns = []
        if not under:
            patterns.append(re.compile(r'_'))
            patterns.append(re.compile(r'_[^_]+.*'))

        if not dunder:
            patterns.append(re.compile(r'__'))
            patterns.append(re.compile(r'_{2,}[^_]+.*'))

        for exp in exclude:
            pattern = exp
            if isinstance(exp, str):
                pattern = re.compile(exp)
            patterns.append(pattern)
        return patterns

    @staticmethod
    def _prettify(text):
        text = text.lstrip('_')  # remove leading _
        text = text.rstrip('_')  # remove trailing _
        text = text.replace('_', ' ')  # replace internal _ with space
        text = text.capitalize()
        return text


def get_fields_source(arg, **source_kw):
    """Tries to find the best :class:`FieldSource` for the given argument.

    An :class:`~object.ObjectSource` is always returned when a more adequate
    field source isn't found.

    :param arg: object to find the right field source for.
    :param arg: any

    :param source_kw: keyword arguments to pass to the ``FieldSource``
                      constructor.

    :return: a new field source object
    :rtype: :class:`FieldSource`

    :raises ValueError: if argument is ``None``
    """
    msg = "Can't obtain a field source from {}".format(arg)
    if arg is None:
        raise ValueError(msg)

    source = None
    try:
        # if SQLAlchemy can't be imported it's pretty sure arg is not a
        # SQLAlchemy object
        from sqlalchemy import Table
    except ImportError:
        pass
    else:
        # check if arg is a SQLAlchemy object
        if isinstance(arg, Table) or hasattr(arg, '__table__'):
            from .sqlalchemy import SQLAlchemySource
            source = SQLAlchemySource(arg, **source_kw)

    if source is None:
        from .object import ObjectSource
        source = ObjectSource(arg, **source_kw)
    return source


def from_bool(name, text, value, **kwargs):
    """Creates a ``BoolField`` from a boolean value.

    :param name: name for the field
    :type name: :class:`str`

    :param text: text for the field
    :type text: :class:`str`

    :param value: a boolean value
    :type value: :class:`bool`

    :param kwargs: keyword arguments to pass to field constructor

    :return: a new ``BoolField`` with the given name and text
    :rtype: :class:`~campos.fields.BoolField`
    """
    fkwargs = kwargs.copy()
    fkwargs['name'] = name
    fkwargs['text'] = text
    return fields.BoolField(**fkwargs)


def from_int(name, text, value, **kwargs):
    """Creates a ``IntField`` from an integer value. A bit of logic
    is applied using provided arguments to determine some field's settings.

    :param name: name for the field
    :type name: :class:`str`

    :param text: text for the field
    :type text: :class:`str`

    :param value: integer value to help adjust field's settings
    :type value: :class:`int`

    :param kwargs: keyword arguments to pass to field constructor

    :return: a new ``IntField`` with the given name and text
    :rtype: :class:`~campos.fields.IntField`
    """
    fkwargs = kwargs.copy()
    fkwargs['name'] = name
    fkwargs['text'] = text

    if text.lower() == 'age' and 0 <= value <= OLDEST_PERSON:
        fkwargs['min'] = kwargs.get('min', 0)
        fkwargs['max'] = kwargs.get('max', OLDEST_PERSON)
        fkwargs['step'] = kwargs.get('step', 1)
    else:
        val = NumberRange()
        # if default range isn't enough use given value with a span of 100 units
        if val.min is None or value <= val.min:
            fkwargs['min'] = kwargs.get('min', value - 100)
        if val.max is None or value >= val.max:
            fkwargs['max'] = kwargs.get('max', value + 100)
    return fields.IntField(**fkwargs)


def from_float(name, text, value, **kwargs):
    """Creates a ``FloatField`` from a float value. A bit of logic
    is applied using provided arguments to determine some field's settings.

    :param name: name for the field
    :type name: :class:`str`

    :param text: text for the field
    :type text: :class:`str`

    :param value: float value to help adjust field's settings
    :type value: :class:`float`

    :param kwargs: keyword arguments to pass to field constructor

    :return: a new ``FloatField`` with the given name and text
    :rtype: :class:`~campos.fields.FloatField`
    """
    fkwargs = kwargs.copy()
    fkwargs['name'] = name
    fkwargs['text'] = text

    if text.lower() == 'height' and 0 <= value <= TALLEST_PERSON:
        fkwargs['min'] = kwargs.get('min', 0)
        fkwargs['max'] = kwargs.get('max', TALLEST_PERSON)
        fkwargs['step'] = kwargs.get('step', 0.5)
    elif text.lower() == 'weight' and 0 <= value <= HEAVIEST_PERSON:
        fkwargs['min'] = kwargs.get('min', 0)
        fkwargs['max'] = kwargs.get('max', HEAVIEST_PERSON)
        fkwargs['step'] = kwargs.get('step', 1)
    else:
        val = NumberRange()
        # if default range isn't enough use given value with a span of 100 units
        if val.min is None or value <= val.min:
            fkwargs['min'] = kwargs.get('min', value - 100)
        if val.max is None or value >= val.max:
            fkwargs['max'] = kwargs.get('max', value + 100)
    return fields.FloatField(**fkwargs)


def from_str(name, text, value, istext=False, **kwargs):
    """Creates a ``StringField`` or a ``TextField`` from a string value.
    A bit of logic is applied using provided arguments to determine
    some field's settings and if output will be a string field or a text field.
    If you want the output to be a ``TextField`` set ``istext=True``.

    :param name: name for the field
    :type name: :class:`str`

    :param text: text for the field
    :type text: :class:`str`

    :param value: string value to help adjust field's settings
    :type value: :class:`str`

    :param istext: if True forces output to be a ``TextField``
    :type istext: :class:`bool`

    :param kwargs: keyword arguments to pass to field constructor

    :return: a new ``StringField`` or ``TextField`` with the given name and text
    :rtype: :class:`~campos.fields.StringField` or
            :class:`~campos.fields.TextField`
    """
    fkwargs = kwargs.copy()
    fkwargs['name'] = name
    fkwargs['text'] = text

    fkwargs['min_length'] = kwargs.get('min_length', 0)

    val = StringLength()
    if istext or len(value) > val.max or '\n' in value:
        return fields.TextField(**fkwargs)
    return fields.StringField(**fkwargs)


def from_date(name, text, value, **kwargs):
    """Creates a ``DateField`` from a date object. A bit of logic
    is applied using provided arguments to determine some field's settings.

    :param name: name for the field
    :type name: :class:`str`

    :param text: text for the field
    :type text: :class:`str`

    :param value: date object to help adjust field's settings
    :type value: :class:`datetime.date`

    :param kwargs: keyword arguments to pass to field constructor

    :return: a new ``DateField`` with the given name and text
    :rtype: :class:`~campos.fields.DateField`

    .. seealso:: :func:`from_time` and :func:`from_datetime`
    """
    fkwargs = kwargs.copy()
    fkwargs['name'] = name
    fkwargs['text'] = text

    val = DateRange()
    if value < val.min and 'min' not in fkwargs:
        fkwargs['min'] = value
    return fields.DateField(**fkwargs)


def from_time(name, text, value, **kwargs):
    """Creates a ``TimeField`` from a time object. A bit of logic
    is applied using provided arguments to determine some field's settings.

    :param name: name for the field
    :type name: :class:`str`

    :param text: text for the field
    :type text: :class:`str`

    :param value: time object to help adjust field's settings
    :type value: :class:`datetime.time`

    :param kwargs: keyword arguments to pass to field constructor

    :return: a new ``TimeField`` with the given name and text
    :rtype: :class:`~campos.fields.TimeField`

    .. seealso:: :func:`from_date` and :func:`from_datetime`
    """
    fkwargs = kwargs.copy()
    fkwargs['name'] = name
    fkwargs['text'] = text

    val = TimeRange()
    if value < val.min and 'min' not in fkwargs:
        fkwargs['min'] = value
    return fields.TimeField(**fkwargs)


def from_datetime(name, text, value, **kwargs):
    """Creates a ``DatetimeField`` from a datetime object. A bit of logic
    is applied using provided arguments to determine some field's settings.

    :param name: name for the field
    :type name: :class:`str`

    :param text: text for the field
    :type text: :class:`str`

    :param value: datetime object to help adjust field's settings
    :type value: :class:`datetime.datetime`

    :param kwargs: keyword arguments to pass to field constructor

    :return: a new ``DatetimeField`` with the given name and text
    :rtype: :class:`~campos.fields.DatetimeField`

    .. seealso:: :func:`from_date` and :func:`from_time`
    """
    fkwargs = kwargs.copy()
    fkwargs['name'] = name
    fkwargs['text'] = text

    val = DatetimeRange()
    if value < val.min and 'min' not in fkwargs:
        fkwargs['min'] = value
    return fields.DatetimeField(**fkwargs)
