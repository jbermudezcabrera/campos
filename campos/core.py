import abc
import re

from qtpy import QtWidgets as Qt

from enums import Validation, Labelling

__author__ = 'Juan Manuel Bermúdez Cabrera'


class Field(Qt.QWidget, metaclass=abc.ABCMeta):
    _FIELDS_COUNT = 0
    _ID_PATTERN = r'[a-z_]+[a-z0-9_]*'

    def __init__(self, name='', text='', description='', default=None,
                 on_change=None, labelling='current', validation='current',
                 validators=()):
        super(Field, self).__init__()
        Field._FIELDS_COUNT += 1
        self.default = default

        self._name = None
        self.name = name

        self.text = text if text else self.name.capitalize().replace('_', ' ')
        self.description = description if description else text

        self._labelling = None
        self.labelling = labelling

        self._on_change = None
        self.on_change = on_change

        self._validation = None
        self.validation = validation

        self.errors = []
        self.validators = []

        for v in validators:
            if callable(v):
                self.validators.append(v)
            else:
                raise ValueError('Expecting callable, got {}'.format(type(v)))

        self._get_change_signal().connect(self._validation_cb)

    @property
    def name(self):
        """Text to identify the field inside forms or other contexts,
        must be a valid variable name, it defaults to field{consecutive_number}

        :type: :class:`str`

        :raises ValueError: if an invalid field name is given
        """
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            self._name = 'field{}'.format(self._FIELDS_COUNT)
        elif re.fullmatch(self._ID_PATTERN, value, re.IGNORECASE):
            self._name = value
        else:
            msg = "Expecting valid variable name, got '{}'".format(value)
            raise ValueError(msg)

    @property
    @abc.abstractmethod
    def text(self):
        """Text to show in the field's label.

        :type: :class:`str`
        """
        pass

    @text.setter
    @abc.abstractmethod
    def text(self, value):
        pass

    @property
    @abc.abstractmethod
    def description(self):
        """Useful short information about the field, usually shown as a tooltip.

        :type: :class:`str`
        """
        pass

    @description.setter
    @abc.abstractmethod
    def description(self, value):
        pass

    @property
    def validation(self):
        """Field's validation mechanism, see :class:`~campos.enums.Validation`
        for possible values.

        :type: :class:`str` or :class:`~campos.enums.Validation`
        """
        return self._validation

    @validation.setter
    def validation(self, value):
        self._validation = Validation.get_member(value)

    @property
    @abc.abstractmethod
    def labelling(self):
        """Field's label position, see :class:`~campos.enums.Labelling` for
        possible values.

        :type: :class:`str` or :class:`~campos.enums.Labelling`
        """
        pass

    @labelling.setter
    @abc.abstractmethod
    def labelling(self, value):
        pass

    @property
    def on_change(self):
        """Handler to call when field's value changes, unlike ``Qt's connect``
        it only supports one handler, if you want to connect multiple handlers
        you should use ``connect``.

        To disconnect a connected handler just set ``on_change = None``

        :type: callable or None
        """
        return self._on_change

    @on_change.setter
    def on_change(self, callback):
        signal = self._get_change_signal()

        if self._on_change is not None:  # disconnect the previous handler
            signal.disconnect(self._on_change)
            self._on_change = None

        if callable(callback):
            signal.connect(callback)
            self._on_change = callback
        elif callback is not None:
            msg = 'Expecting callable, got {}'.format(type(callback))
            raise ValueError(msg)

    @property
    @abc.abstractmethod
    def value(self):
        """Field's current value"""
        pass

    @value.setter
    @abc.abstractmethod
    def value(self, value):
        pass

    def validate(self):
        """Validates field's current value using current validators

        :return: if the field is valid or not
        :rtype: :class:`bool`
        """
        self.errors.clear()

        for validator in self.validators:
            try:
                validator(self)
            except ValueError as e:
                self.errors.append(e)
                return False
        return True

    def _get_change_signal(self):
        msg = "'CHANGE_SIGNAL' attribute must be defined and reference a " \
              "valid Qt's signal"
        try:
            if not callable(self.CHANGE_SIGNAL):
                raise ValueError(msg)
        except AttributeError:
            raise AttributeError(msg)
        else:
            return self.CHANGE_SIGNAL

    def _validation_cb(self):
        if self.validation == Validation.INSTANT:
            self.validate()


class BaseField(Field, metaclass=abc.ABCMeta):
    """More complete abstract base class for fields, implementing a common use
    case scenario.

    This class assumes that a field is composed by a label, a central component
    (usually where the value is entered) and other label used to show validation
    errors.

    In order to create new fields following this structure is only necessary to
    implement :attr:`value` property getter and setter and define two
    attributes:

    1. MAIN_COMPONENT: points to a QWidget or QLayout holding the main part of
    the field(without text and error labels).

    2. MAIN_WIDGET: points to the main QWidget in the field, where the value is
    introduced.

    :class:`Field` should be used as base class to create fields without
    this structure.
    """

    def __init__(self, **kwargs):
        self.label = Qt.QLabel('')
        self.error_label = Qt.QLabel('')
        self.error_label.setStyleSheet('color: rgb(255, 0, 0);')
        self.layout = None

        super(BaseField, self).__init__(**kwargs)

    @property
    def text(self):
        return self.label.text()

    @text.setter
    def text(self, value):
        self.label.setText(value)

    @property
    def description(self):
        return self._get_main_widget().toolTip()

    @description.setter
    def description(self, value):
        self._get_main_widget().setToolTip(value)

    @property
    def labelling(self):
        return self._labelling

    @labelling.setter
    def labelling(self, value):
        new = Labelling.get_member(value)

        if self.labelling != new:
            # create new layout
            if new == Labelling.LEFT:
                klass = Qt.QHBoxLayout
            elif new == Labelling.TOP:
                klass = Qt.QVBoxLayout
            else:
                msg = '{} not supported by {}'.format(new, self.__class__)
                raise ValueError(msg)

            layout = klass()
            layout.setSpacing(5)
            layout.setContentsMargins(0, 0, 0, 0)

            # remove current layout's children and add them to new layout
            current = self.layout()
            for i in range(current.count()):
                item = current.itemAt(i)
                if isinstance(item, Qt.QLayout):
                    current.removeItem(item)
                    layout.addLayout(item)
                else:
                    current.removeWidget(item)
                    layout.addWidget(item)

            # stretch main component
            layout.setStretch(1, 1)

            # re-parent current layout
            Qt.QWidget().setLayout(current)

            # set new layout
            self.setLayout(layout)

    def validate(self):
        valid = super(BaseField, self).validate()

        if self.error_label is not None:
            self.error_label.setText('' if valid else str(self.errors.pop()))
        return valid

    def _get_main_widget(self):
        msg = "'MAIN_WIDGET' attribute must be defined and reference a " \
              "valid QtWidget"
        try:
            if not isinstance(self.MAIN_WIDGET, Qt.QWidget):
                raise ValueError(msg)
        except AttributeError:
            raise AttributeError(msg)
        else:
            return self.MAIN_WIDGET

    def _get_main_component(self):
        msg = "'MAIN_COMPONENT' attribute must be defined and reference a " \
              "valid QtWidget or QLayout"
        try:
            if not isinstance(self.MAIN_COMPONENT, (Qt.QWidget, Qt.QLayout)):
                raise ValueError(msg)
        except AttributeError:
            raise AttributeError(msg)
        else:
            return self.MAIN_WIDGET
