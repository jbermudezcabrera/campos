import re

from qtpy import QtWidgets as Qt

from enums import Validation, Labelling
from utils import callable, first_of_type
from validators import DataRequired

__author__ = 'Juan Manuel Bermúdez Cabrera'


class Field(Qt.QWidget):
    _FIELDS_COUNT = 0
    _ID_PATTERN = r'[a-z_]+[a-z0-9_]*'

    def __init__(self, *args, name='', text='', description='', default=None,
                 on_change=None, labelling='current', validation='current',
                 validators=(), required=False, message=None):
        super(Field, self).__init__(*args)
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
        self.message = message
        self.required = required

        for v in validators:
            if callable(v):
                self.validators.append(v)
            else:
                raise ValueError('Expecting callable, got {}'.format(type(v)))

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
    def text(self):
        """Text to show in the field's label.

        :type: :class:`str`
        """
        raise NotImplementedError

    @text.setter
    def text(self, value):
        raise NotImplementedError

    @property
    def description(self):
        """Useful short information about the field, usually shown as a tooltip.

        :type: :class:`str`
        """
        raise NotImplementedError

    @description.setter
    def description(self, value):
        raise NotImplementedError

    @property
    def required(self):
        return first_of_type(self.validators, DataRequired) is not None

    @required.setter
    def required(self, value):
        validator = first_of_type(self.validators, DataRequired)
        if value:
            if validator is None:
                self.validators.append(DataRequired())
        else:
            if validator is not None:
                self.validators.remove(validator)

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
        if self.validation == Validation.INSTANT:
            self._get_change_signal().connect(self._validation_cb)
        else:
            self._get_change_signal().disconnect(self._validation_cb)

    @property
    def labelling(self):
        """Field's label position, see :class:`~campos.enums.Labelling` for
        possible values.

        :type: :class:`str` or :class:`~campos.enums.Labelling`
        """
        raise NotImplementedError

    @labelling.setter
    def labelling(self, value):
        raise NotImplementedError

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
    def value(self):
        """Field's current value"""
        raise NotImplementedError

    @value.setter
    def value(self, value):
        raise NotImplementedError

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


class BaseField(Field):
    """More complete abstract base class for fields, implementing a common use
    case scenario.

    This class assumes that a field is composed by a label, a central component
    (usually where the value is entered) and other label used to show validation
    errors.

    In order to create new fields following this structure is only necessary to
    implement :attr:`value` property getter and setter and define a
    MAIN_COMPONENT attribute pointing to a QWidget or QLayout holding the main
    part of the field(without text and error labels).

    :class:`Field` should be used as base class to create fields without
    this structure.
    """

    def __init__(self, *args, **kwargs):
        self.label = Qt.QLabel('')
        self.error_label = Qt.QLabel('')
        self.error_label.setStyleSheet('color: rgb(255, 0, 0);')
        self.layout = None

        super(BaseField, self).__init__(*args, **kwargs)

    @property
    def text(self):
        return self.label.text()

    @text.setter
    def text(self, value):
        self.label.setText(value)

    @property
    def description(self):
        main = self._get_main_component()
        if isinstance(main, Qt.QWidget):
            return main.toolTip()

        # it's a layout
        for i in range(main.count()):
            item = main.itemAt(i)
            if isinstance(item, Qt.QWidget) and item.toolTip():
                return item.toolTip()
        return ''

    @description.setter
    def description(self, value):
        main = self._get_main_component()
        if isinstance(main, Qt.QWidget):
            main.setToolTip(value)
        else:
            # it's a layout
            for i in range(main.count()):
                item = main.itemAt(i)
                if isinstance(item, Qt.QWidget) and not item.toolTip():
                    item.setToolTip(value)

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

            # if it was a previous layout then remove it's children and add them
            # to the new layout
            if self.labelling:
                # set new layout and re-parent existing one
                current = self.layout()
                self.setLayout(layout)

                for i in range(current.count()):
                    item = current.itemAt(i)
                    if isinstance(item, Qt.QLayout):
                        current.removeItem(item)
                        layout.addLayout(item)
                    else:
                        current.removeWidget(item)
                        layout.addWidget(item)
            else:
                # setting layout and adding children for first time
                layout.addWidget(self.label)

                main = self._get_main_component()
                if isinstance(main, Qt.QLayout):
                    layout.addLayout(main)
                else:
                    layout.addWidget(main)

                layout.addWidget(self.error_label)
                self.setLayout(layout)

            # stretch main component
            layout.setStretch(1, 1)

    def validate(self):
        valid = super(BaseField, self).validate()

        if self.error_label is not None:
            msg = ''
            if not valid:
                msg = self.message if self.message else str(self.errors.pop())
            self.error_label.setText(msg)
        return valid

    def _get_main_component(self):
        msg = "'MAIN_COMPONENT' attribute must be defined and reference a " \
              "valid QtWidget or QLayout"
        try:
            if not isinstance(self.MAIN_COMPONENT, (Qt.QWidget, Qt.QLayout)):
                raise ValueError(msg)
        except AttributeError:
            raise AttributeError(msg)
        else:
            return self.MAIN_COMPONENT
