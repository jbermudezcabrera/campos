import os
import abc
import contextlib

from utils import Enum

__author__ = 'Juan Manuel Bermúdez Cabrera'


class BaseEnum(Enum):
    """Base enumeration class"""

    @classmethod
    def get_member(cls, arg):
        """Facilitates access to enum members using following shortcuts.

        * If `arg` is a member of this enum returns `arg`.

        * If `arg` is an `str` then a case-insensitive search is done among this enum members
          looking for one whose name matches `arg`.

          If no member is found with name equal to `arg` then:

          - If ``arg.upper() == 'CURRENT'`` and the enum is subclass of :class:`HasCurrent` the
            :func:`HasCurrent.get_current` method is called.

          - Else, if ``arg.upper() == 'DEFAULT'`` and the enum is subclass of :class:`HasDefault`
            the :func:`HasDefault.default` method is called.

        :param arg: a member object or a string representing its name, 'current' or 'default' if
                    supported.
        :type arg: an enum member or :class:`str`.

        :return: an enum member.

        :raises ValueError: if a member couldn't be found using `arg`.
        """
        if isinstance(arg, cls):
            return arg
        if isinstance(arg, str):
            u_arg = arg.strip().upper()
            for member in cls:
                if member.name.upper() == u_arg:
                    return member

            if u_arg == 'CURRENT' and issubclass(cls, HasCurrent):
                return cls.get_current()

            if u_arg == 'DEFAULT' and issubclass(cls, HasDefault):
                return cls.default()

        message = "Unknown member '{}' of {}, valid values are: {}"
        joined = ','.join("'{}'".format(str(m).lower()) for m in cls.__members__)
        raise ValueError(message.format(arg, cls.__name__, joined))


class HasDefault:
    """Behavior to implement in order to give a :class:`BaseEnum` the ability to provide a
    default value.

    .. seealso:: :class:`HasCurrent`
    """

    @classmethod
    @abc.abstractmethod
    def default(cls):
        """Obtains the default value of a :class:`BaseEnum` subclass.

        :Examples:

        * Validation.default()
        * Validation.get_member('default')

        :return: the default enum member.
        """
        pass


class HasCurrent:
    """Behavior to implement in order to give a :class:`BaseEnum` the ability to globally set and
    obtain a current value.

    .. seealso:: :class:`HasDefault`
    """

    @classmethod
    def get_current(cls):
        """Obtains the current value of a :class:`BaseEnum` subclass.

        If a current value has not been established using :func:`set_current` and the enum is
        an :class:`HasDefault` subclass then the :func:`HasDefault.default` method is called,
        otherwise an AttributeError is raised.

        :Examples:

        * Validation.get_current()
        * Validation.get_member('current')

        :return: the current enum member or the default value if supported.

        :raises AttributeError: if no value has been established using :func:`set_current` and
                                the enum is not a :class:`HasDefault` subclass.
        """
        try:
            return getattr(cls, '_CURRENT')
        except AttributeError:
            if issubclass(cls, HasDefault):
                return cls.default()
            msg = 'No {} option has been settled'.format(cls.__name__)
            raise AttributeError(msg)

    @classmethod
    def set_current(cls, value):
        """Establish the current value of a :class:`BaseEnum` subclass.

        `value` is processed using :func:`BaseEnum.get_member`, therefore all its shortcuts can be
        used here.

        :Examples:

        * ViewsPackage.set_current('pyqt4')
        * ViewsPackage.get_member(ViewsPackage.PyQt4)

        :param value: enum member to set as the current one.
        :type value: all values supported by :func:`BaseEnum.get_member`

        :raises ValueError: if a member couldn't be found using `value`.
        """
        cls._CURRENT = cls.get_member(value)


class QtAPI(HasCurrent, BaseEnum):
    """Available Qt bindings.

    .. note:: This enum can be empty if none of the supported Qt bindings can be imported.
    """
    with contextlib.suppress(ImportError):
        import PyQt4

    with contextlib.suppress(ImportError):
        import PyQt5

    with contextlib.suppress(ImportError):
        import PySide

    @classmethod
    def set_current(cls, value):
        super(QtAPI, cls).set_current(value)

        os.environ['QT_API'] = QtAPI.get_current().name.lower()


class Labelling(HasDefault, HasCurrent, BaseEnum):
    """Possible positions to display a label in fields, default is 'left'"""

    #: Left to the field
    LEFT = 0

    #: On top of the field
    TOP = 1

    @classmethod
    def default(cls):
        return cls.LEFT


class Validation(HasDefault, HasCurrent, BaseEnum):
    """Available validation mechanisms to be used in fields, the default is 'instant'"""

    #: Validation is left to the user, :func:`.composite.Field.validate` must be called.
    MANUAL = 0

    #: Validation occurs any time the value of a field changes.
    INSTANT = 1

    @classmethod
    def default(cls):
        return cls.INSTANT
