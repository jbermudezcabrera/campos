__author__ = 'Juan Manuel Bermúdez Cabrera'

try:
    from builtins import callable
except ImportError:  # callable builtin not present, replace with __call__ attribute check
    def callable(obj):
        return hasattr(obj, '__call__')

try:
    from enum import Enum
except ImportError:  # enum module not present replace with custom metaclass and base class
    from inspect import isroutine


    def _member_str(self):
        return self.name


    class EnumMeta(type):
        def __new__(cls, name, bases, namespace, **kwargs):
            namespace['__str__'] = _member_str  # injecting custom __str__
            EnumClass = type.__new__(cls, name, bases, namespace)  # new enumeration class

            members = []
            for var, value in namespace.items():
                if not var.startswith('_') and not isroutine(value):  # member's name should not start with _
                    # enumeration members are objects of the enumeration class with extra name and value attributes
                    member = EnumClass()
                    member.name = var
                    member.value = value

                    members.append(member)

            for member in members:
                # replace class namespace vars with enumeration members
                setattr(EnumClass, member.name, member)

            EnumClass.__members__ = members

            return EnumClass

        def __len__(self):
            return len(self.__members__)

        def __iter__(self):
            return iter(self.__members__)


    class Enum(metaclass=EnumMeta):
        pass


def first_validator_of_type(validators, v_type):
    for v in validators:
        if isinstance(v, v_type):
            return v
    return None
