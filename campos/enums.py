import abc

from qtpy.QtWidgets import QDialogButtonBox

from .utils import Enum

__author__ = 'Juan Manuel Bermúdez Cabrera'


class BaseEnum(Enum):
    """Base enumeration class"""

    @classmethod
    def get_member(cls, arg):
        """Facilitates access to enum members using the shortcuts below.

        * If `arg` is a member of this enum returns `arg`.

        * If `arg` is an `str` then a case-insensitive search is done among
          enum members looking for one whose name matches `arg`.

          If no member is found with name equal to `arg` then:

          - If ``arg.upper() == 'CURRENT'`` and the enum is subclass of
            :class:`HasCurrent` the :func:`~HasCurrent.get_current` method is
            called.

          - Else, if ``arg.upper() == 'DEFAULT'`` and the enum is subclass of
            :class:`HasDefault` the :func:`~HasDefault.default` method is
            called.

        :param arg: a member object or a string representing its name, 'current'
                    or 'default' if supported.
        :type arg: enum member or :class:`str`.

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

        message = "Unknown member '{}' of {} enum, valid values are: {}"
        joined = ','.join(member.name.lower() for member in cls)
        joined += ',current' if issubclass(cls, HasCurrent) else ''
        joined += ',default' if issubclass(cls, HasDefault) else ''
        raise ValueError(message.format(arg, cls.__name__, joined))


class HasDefault:
    """Behavior to implement in order to give a :class:`BaseEnum` subclass the
    ability to provide a default value.

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
    """Behavior to implement in order to give a :class:`BaseEnum` subclass the
    ability to globally set and obtain a current value.

    .. seealso:: :class:`HasDefault`
    """

    @classmethod
    def get_current(cls):
        """Obtains the current value of a :class:`BaseEnum` subclass.

        If a current value has not been established using :func:`set_current`
        and the enum is an :class:`HasDefault` subclass then the
        :func:`~HasDefault.default` method is called, otherwise an
        :class:`AttributeError` is raised.

        :Examples:

        Validation.get_current()
        Validation.get_member('current')

        :return: the current enum member or the default value if supported.

        :raises AttributeError: if no value has been established using
                                :func:`set_current` and the enum is not a
                                :class:`HasDefault` subclass.
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

        `value` is processed using :func:`BaseEnum.get_member`, therefore all
        its shortcuts can be used here.

        :Example:

        Labelling.set_current('left')

        :param value: enum member to set as the current one.
        :type value: all values supported by :func:`BaseEnum.get_member`

        :raises ValueError: if a member couldn't be found using `value`.
        """
        cls._CURRENT = cls.get_member(value)


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
    """Available validation mechanisms to be used in fields, the default is
    'instant'
    """

    #: Validation is left to the user.
    MANUAL = 0

    #: Validation occurs any time the value of a field changes.
    INSTANT = 1

    @classmethod
    def default(cls):
        return cls.INSTANT


class ButtonType(BaseEnum):
    """Available button types, this enum's members are shortcuts to Qt's
    StandardButtons enum
    """

    #: QDialogButtonBox.Ok
    OK = QDialogButtonBox.Ok

    #: QDialogButtonBox.Open
    OPEN = QDialogButtonBox.Open

    #: QDialogButtonBox.Save
    SAVE = QDialogButtonBox.Save

    #: QDialogButtonBox.Cancel
    CANCEL = QDialogButtonBox.Cancel

    #: QDialogButtonBox.Close
    CLOSE = QDialogButtonBox.Close

    #: QDialogButtonBox.Discard
    DISCARD = QDialogButtonBox.Discard

    #: QDialogButtonBox.Apply
    APPLY = QDialogButtonBox.Apply

    #: QDialogButtonBox.Reset
    RESET = QDialogButtonBox.Reset

    #: QDialogButtonBox.RestoreDefaults
    RESTORE_DEFAULTS = QDialogButtonBox.RestoreDefaults

    #: QDialogButtonBox.Help
    HELP = QDialogButtonBox.Help

    #: QDialogButtonBox.SaveAll
    SAVE_ALL = QDialogButtonBox.SaveAll

    #: QDialogButtonBox.Yes
    YES = QDialogButtonBox.Yes

    # QDialogButtonBox.YesToAll
    YES_TO_ALL = QDialogButtonBox.YesToAll

    #: QDialogButtonBox.No
    NO = QDialogButtonBox.No

    #: QDialogButtonBox.NoToAll
    NO_TO_ALL = QDialogButtonBox.NoToAll

    #: QDialogButtonBox.Abort
    ABORT = QDialogButtonBox.Abort

    #: QDialogButtonBox.Retry
    RETRY = QDialogButtonBox.Retry

    #: QDialogButtonBox.Ignore
    IGNORE = QDialogButtonBox.Ignore
