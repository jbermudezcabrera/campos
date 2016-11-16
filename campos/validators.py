import re
import abc
import math
from datetime import date, time, datetime

__author__ = 'Juan Manuel Bermúdez Cabrera'


class Validator(metaclass=abc.ABCMeta):
    """Base class for field validation.

    Subclasses must define a ``__call__(self, field)`` method which validates the current value
    of `field` and raises a ValueError error if it is not valid.

    :param message: message to show when an invalid value is found.
    :type message: :class:`str`
    """

    def __init__(self, message='Invalid data'):
        self.message = message

    @abc.abstractmethod
    def __call__(self, field):
        pass


class DataRequired(Validator):
    """Checks if a field is not empty.

    Only basic validations are done here, the following values are considered
    invalid:

    * None
    * Empty strings or containing only blank spaces.
    * Numbers when :func:`math.isfinite` is `False`.
    * Empty collections.
    * Time objects if its evaluation in a boolean context is False

    :param message: message to show when no data is found
    :type message: :class:`str`
    """

    def __init__(self, message='Required'):
        super(DataRequired, self).__init__(message=message)

    def __call__(self, field):
        value = field.value
        valid = True

        if value is None:
            valid = False
        elif isinstance(value, str):
            valid = len(value.strip()) > 0
        elif isinstance(value, (int, float)):
            valid = math.isfinite(value)
        elif hasattr(value, '__len__'):
            valid = len(value) > 0
        elif isinstance(value, time) and not value:
            valid = False

        if not valid:
            raise ValueError(self.message)


class NumberRange(Validator):
    """Number range validation.

    :param min: minimum valid value, defaults to 0
    :type min: :class:`int` or :class:`float`

    :param max: maximum valid value, defaults to 100
    :type max: :class:`int` or :class:`float`

    :param message: message to show if ``not min <= value <= max``
    :type message: :class:`str`
    """

    def __init__(self, min=0, max=100, message=None):
        super(NumberRange, self).__init__(message=message)
        self.min = min
        self.max = max

    def __call__(self, field):
        value = field.value

        if not self.min <= value <= self.max:
            message = self.message
            if self.message is None:
                message = 'Value must be between {} and {}'
                message = message.format(self.min, self.max)
            raise ValueError(message)


class StringLength(Validator):
    """String length validation.

    :param min: minimum valid length, defaults to 0
    :type min: :class:`int`

    :param max: maximum valid length, defaults to 100
    :type max: :class:`int`

    :param message: message to show if ``not min <= len(value) <= max``
    :type message: :class:`str`
    """

    def __init__(self, min=0, max=100, message=None):
        super(StringLength, self).__init__(message=message)
        self.min = min
        self.max = max

    def __call__(self, field):
        value = field.value

        if not self.min <= len(value) <= self.max:
            message = self.message
            if self.message is None:
                message = 'Value must be between {} and {} characters long'
                message = message.format(self.min, self.max)
            raise ValueError(message)


class RegExp(Validator):
    """Validate text against a regular expression.

    :param exp: string or compiled regular expression
    :type exp: :class:`str` or compiled re

    :param flags: flags to pass to :func:`re.compile` if it's necessary
    :type flags: :class:`int`

    :param message: message to show if value doesn't fully match the regular
                    expression
    :type message: :class:`str`
    """

    def __init__(self, exp, flags=0, message="Value doesn't match pattern"):
        super(RegExp, self).__init__(message=message)
        self.compiled = re.compile(exp, flags) if isinstance(exp, str) else exp

    def __call__(self, field):
        if not self.compiled.fullmatch(field.value):
            raise ValueError(self.message)


class DateRange(Validator):
    """Range validation for :class:`datetime.date` objects.

    :param min: minimum valid date, defaults to the current date
    :type min: :class:`datetime.date`

    :param max: maximum valid date, defaults to `date.max`
    :type max: :class:`datetime.date`

    :param message: message to show if ``not min <= value <= max``
    :type message: :class:`str`
    """

    def __init__(self, min=date.today(), max=date.max, message=None):
        super(DateRange, self).__init__(message=message)
        self.min = min
        self.max = max

    def __call__(self, field):
        value = field.value

        if not self.min <= value <= self.max:
            message = self.message
            if self.message is None:
                message = 'Date must be between {} and {}'
                message = message.format(self.min, self.max)
            raise ValueError(message)


class TimeRange(Validator):
    """Range validation for :class:`datetime.time` objects.

    :param min: minimum valid time, defaults to :attr:`datetime.time.min`
    :type min: :class:`datetime.time`

    :param max: maximum valid time, defaults to :attr:`datetime.time.max`
    :type min: :class:`datetime.time`

    :param message: message to show if ``not min <= value <= max``
    :type message: :class:`str`
    """

    def __init__(self, min=time.min, max=time.max, message=None):
        super(TimeRange, self).__init__(message=message)
        self.min = min
        self.max = max

    def __call__(self, field):
        value = field.value

        if not self.min <= value <= self.max:
            message = self.message
            if self.message is None:
                message = 'Time must be between {} and {}'
                message = message.format(self.min, self.max)
            raise ValueError(message)


class DatetimeRange(Validator):
    """Range validation for :class:`datetime.datetime` objects.

    :param min: minimum valid datetime, defaults to
                :attr:`datetime.datetime.min`
    :type min: :class:`datetime.datetime`

    :param max: maximum valid datetime, defaults to
                :attr:`datetime.datetime.max`
    :type min: :class:`datetime.datetime`

    :param message: message to show if ``not min <= value <= max``
    :type message: :class:`str`
    """

    def __init__(self, min=datetime.min, max=datetime.max, message=None):
        super(DatetimeRange, self).__init__(message=message)
        self.min = min
        self.max = max

    def __call__(self, field):
        value = field.value

        if not self.min <= value <= self.max:
            message = self.message
            if self.message is None:
                message = 'Date and time must be between {} and {}'
                message = message.format(self.min, self.max)
            raise ValueError(message)
