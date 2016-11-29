import re

from qtpy import QtWidgets as Qt

from .enums import Validation, Labelling
from .utils import callable, first_of_type
from .validators import DataRequired

__author__ = 'Juan Manuel Bermúdez Cabrera'


class Field(Qt.QWidget):
    """Base class for input fields, isn't generally used directly.

    A field is usually composed of a label and an input component. The field's
    label position can be changed individually by modifying `labelling` property
    or globally by calling :func:`~campos.enums.HasCurrent.set_current` on
    :class:`~campos.enums.Labelling` enum. It goes the same way with field's
    validation, see :class:`~campos.enums.Validation` enum for possible
    validation mechanisms.

    Subclasses must implement :func:`has_data` method and :attr:`change_signal`
    property.

    :param name: text to identify the field inside forms or other contexts,
                 must be a valid variable name, it defaults to
                 ``field{consecutive_number}``
    :type name: :class:`str`

    :param text: text to show in field's label, it defaults to ``name``
    :type text: :class:`str`

    :param description: useful short information about the field, usually shown
                        as a tooltip
    :type description: :class:`str`

    :param default: default value when field is shown by first time

    :param on_change: handler to call when field's value changes, this is a
                      shortcut and it only supports one handler at a time,
                      if you want to connect multiple handlers you should use
                      ``field.change_signal.connect(handler)`` for each handler
    :type on_change: callable

    :param labelling: field's label position, see
                      :class:`~campos.enums.Labelling` for possible values,
                      defaults to 'current'
    :type labelling: :class:`str` or :class:`~campos.enums.Labelling`

    :param validation: field's validation mechanism, see
                       :class:`~campos.enums.Validation` for possible values,
                       defaults to 'current'
    :type validation: :class:`str` or :class:`~campos.enums.Validation`

    :param validators: validators used to process field's value when
                       validation is invoked
    :type validators: iterable of :class:`~campos.validators.Validator`

    :param required: marks this field as required or not, this a shortcut for
                     ``field.validators.append(DataRequired())``
    :type required: :class:`bool`

    :param message: text to show if field is invalid, if set, this message has
                    priority over validators' messages
    :type message: :class:`str`
    """

    _FIELDS_COUNT = 0
    _ID_PATTERN = r'[a-z_]+[a-z0-9_]*'

    def __init__(self, *args, name='', text='', description='', default=None,
                 on_change=None, labelling='current', validation='current',
                 validators=(), required=False, message=None):
        super(Field, self).__init__(*args)
        Field._FIELDS_COUNT += 1

        self.default = default
        try:
            self.value = self.default
        except TypeError:
            msg = 'Expecting valid default value for {}, got {}'
            msg = msg.format(type(self).__name__, self.default)
            raise TypeError(msg)

        self._name = None
        self.name = name

        self.text = text if text else self.name.capitalize().replace('_', ' ')
        self.description = description if description else text

        self._labelling = None
        self.labelling = labelling

        self._on_change = None
        self.on_change = on_change

        self.valid = True
        self._validation = None
        self.validation = validation

        self.errors = []
        self.validators = []
        self.message = message

        for v in validators:
            if callable(v):
                self.validators.append(v)
            else:
                raise ValueError('Expecting callable, got {}'.format(v))

        self.required = required

    @property
    def name(self):
        """Text to identify the field inside forms or other contexts,
        must be a valid variable name, it defaults to
        ``field{consecutive_number}``

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
            msg = 'Expecting valid variable name, got {}'.format(value)
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
        """Marks this field as required or not, this a shortcut for
        ``field.validators.append(DataRequired())``

        :type: :class:`bool`
        """
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
        previous = self._validation
        self._validation = Validation.get_member(value)

        if self._validation != previous:
            if self._validation == Validation.INSTANT:
                self.change_signal.connect(self._validation_cb)
            elif previous is not None:
                self.change_signal.disconnect(self._validation_cb)

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
        """Handler to call when field's value changes, this is a shortcut and
        it only supports one handler at a time, if you want to connect multiple
        handlers you should use ``field.change_signal.connect(handler)``
        for each handler.

        To disconnect a connected handler just set ``on_change = None``

        :type: callable or None
        """
        return self._on_change

    @on_change.setter
    def on_change(self, callback):
        if self._on_change is not None:  # disconnect the previous handler
            self.change_signal.disconnect(self._on_change)
            self._on_change = None

        if callable(callback):
            self.change_signal.connect(callback)
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

    def has_data(self):
        """Check if the field has any data.

        :returns: True only if the field contains any data
        :rtype: :class:`bool`
        """
        raise NotImplementedError

    @property
    def change_signal(self):
        """Returns a valid Qt signal which is fired whenever the field's
        value changes

        :rtype: callable
        """
        raise NotImplementedError

    def validate(self):
        """Validates field's current value using current validators. After
        validation all errors are stored in ``errors`` list in the form of
        :class:`ValueError` objects, if the field is valid ``errors`` will be
        empty.

        :return: if the field is valid or not
        :rtype: :class:`bool`
        """
        self.errors.clear()

        if not (self.required or self.has_data()):
            self.valid = True
        else:
            for validator in self.validators:
                try:
                    validator(self)
                except ValueError as e:
                    self.errors.append(e)
            self.valid = len(self.errors) == 0

    def _validation_cb(self):
        if self.validation == Validation.INSTANT:
            self.validate()


class BaseField(Field):
    """More complete base class for fields, implementing a common use case
    scenario.

    This class assumes that a field is composed by a label, a central component
    (usually where the value is entered) and other label used to show validation
    errors.

    In order to create new fields following this structure is only necessary to
    implement :attr:`value` and :attr:`main_component` properties.

    :class:`Field` should be used as base class to create fields without
    this structure.
    """

    def __init__(self, *args, **kwargs):
        self.label = Qt.QLabel('')
        self.error_label = Qt.QLabel('')
        self.error_label.setStyleSheet('color: rgb(255, 0, 0);')
        self.field_layout = None

        super(BaseField, self).__init__(*args, **kwargs)

    @property
    def main_component(self):
        """Returns a valid QWidget or QLayout holding the main part of the
        field(without text and error labels)

        :rtype: QWidget or QLayout
        """
        raise NotImplementedError

    @property
    def text(self):
        return self.label.text()

    @text.setter
    def text(self, value):
        self.label.setText(value)

    @property
    def description(self):
        if isinstance(self.main_component, Qt.QWidget):
            return self.main_component.toolTip()

        # it's a layout
        for i in range(self.main_component.count()):
            item = self.main_component.itemAt(i)
            if isinstance(item, Qt.QWidget) and item.toolTip():
                return item.toolTip()
        return ''

    @description.setter
    def description(self, value):
        if isinstance(self.main_component, Qt.QWidget):
            self.main_component.setToolTip(value)
        else:
            # it's a layout
            for i in range(self.main_component.count()):
                item = self.main_component.itemAt(i)
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
            if self.field_layout is not None:
                self.field_layout.takeAt(2)  # error label
                self.field_layout.takeAt(1)  # main component
                self.field_layout.takeAt(0)  # label

                # re-parent existing layout
                Qt.QWidget().setLayout(self.field_layout)

            # add children to new layout
            layout.addWidget(self.label)

            if isinstance(self.main_component, Qt.QWidget):
                layout.addWidget(self.main_component)
            else:
                layout.addLayout(self.main_component)

            layout.addWidget(self.error_label)

            # stretch main component
            layout.setStretch(1, 1)

            # set layout
            self.field_layout = layout
            self.setLayout(layout)
            self._labelling = new

    def validate(self):
        super(BaseField, self).validate()

        if self.error_label is not None:
            msg = ''
            if not self.valid:
                msg = self.message if self.message else str(self.errors.pop())
            self.error_label.setText(msg)
