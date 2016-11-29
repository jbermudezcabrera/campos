import os
import operator
from datetime import date, time, datetime

import qtpy.QtWidgets as Qt
from qtpy.QtCore import QDate, QTime, QDateTime

from .core import BaseField
from .utils import first_of_type, callable
from .validators import (NumberRange, StringLength, DateRange, TimeRange,
                         DatetimeRange)

__author__ = 'Juan Manuel Bermúdez Cabrera'


class IntField(BaseField):
    """Field to introduce :class:`int` values

    :param min: minimum admitted value, defaults to 0
    :type min: :class:`int`

    :param max: maximum admitted value, defaults to 100
    :type min: :class:`int`

    :param step: amount to increase or decrease current value by, defaults to 1
    :type min: :class:`int`
    """

    def __init__(self, *args, min=0, max=100, step=1, **kwargs):
        self._spin = Qt.QSpinBox()

        kwargs.setdefault('default', 0)
        super(IntField, self).__init__(*args, **kwargs)

        self._range = first_of_type(self.validators, NumberRange)
        if self._range is None:
            self._range = NumberRange(min=min, max=max)

        self.validators.append(self._range)
        self.min = self._range.min
        self.max = self._range.max
        self.step = step

    @property
    def main_component(self):
        return self._spin

    @property
    def change_signal(self):
        return self.main_component.valueChanged

    @property
    def value(self):
        return self.main_component.value()

    @value.setter
    def value(self, value):
        self.main_component.setValue(value)

    def has_data(self):
        return True

    @property
    def step(self):
        """Amount to increase or decrease current value by.

        :type: :class:`int`
        """
        return self.main_component.singleStep()

    @step.setter
    def step(self, value):
        self.main_component.setSingleStep(value)

    @property
    def min(self):
        """Minimum admitted value.

        :type: :class:`int`
        """
        return self._range.min

    @min.setter
    def min(self, value):
        self._range.min = value
        self.main_component.setMinimum(value)

    @property
    def max(self):
        """Maximum admitted value.

        :type: :class:`int`
        """
        return self._range.max

    @max.setter
    def max(self, value):
        self._range.max = value
        self.main_component.setMaximum(value)


class FloatField(IntField):
    """Field to introduce :class:`float` values

    :param precision: decimal places, defaults to 2
    :type min: :class:`int`
    """

    def __init__(self, *args, precision=2, **kwargs):
        self._double_spin = Qt.QDoubleSpinBox()

        kwargs.setdefault('default', 0)
        super(FloatField, self).__init__(*args, **kwargs)

        self.precision = precision
        self.value = self.default

    @property
    def main_component(self):
        return self._double_spin

    @property
    def precision(self):
        """Decimal places.

        :type: :class:`int`
        """
        return self.main_component.decimals()

    @precision.setter
    def precision(self, value):
        self.main_component.setDecimals(value)


class StringField(BaseField):
    """Field to introduce :class:`str`

    :param min_length: minimum admitted length, defaults to 0
    :type min_length: :class:`int`

    :param max_length: maximum admitted length, defaults to 100
    :type max_length: :class:`int`
    """

    def __init__(self, *args, min_length=0, max_length=100, **kwargs):
        self._editor = Qt.QLineEdit()

        kwargs.setdefault('default', '')
        super(StringField, self).__init__(*args, **kwargs)

        self._length = first_of_type(self.validators, StringLength)
        if self._length is None:
            self._length = StringLength(min=min_length, max=max_length)

        self.validators.append(self._length)
        self.min_length = self._length.min
        self.max_length = self._length.max

    @property
    def main_component(self):
        return self._editor

    @property
    def change_signal(self):
        return self.main_component.textChanged

    @property
    def value(self):
        return self.main_component.text()

    @value.setter
    def value(self, new):
        self.main_component.setText(new)

    def has_data(self):
        return len(self.value) > 0

    @property
    def min_length(self):
        """Minimum admitted length.

        :type: :class:`int`
        """
        return self._length.min

    @min_length.setter
    def min_length(self, value):
        if value < 0:
            msg = 'Expecting non negative number, got {}'
            raise ValueError(msg.format(value))
        self._length.min = value

    @property
    def max_length(self):
        """Maximum admitted length.

        :type: :class:`int`
        """
        return self._length.max

    @max_length.setter
    def max_length(self, value):
        if value < 0:
            msg = 'Expecting non negative number, got {}'
            raise ValueError(msg.format(value))
        self._length.max = value
        self.main_component.setMaxLength(value)


class TextField(StringField):
    """Field to introduce large strings"""

    def __init__(self, *args, **kwargs):
        self._text_editor = Qt.QTextEdit()

        kwargs.setdefault('default', '')
        kwargs.setdefault('max_length', 1000)

        super(TextField, self).__init__(*args, **kwargs)

    @property
    def main_component(self):
        return self._text_editor

    @property
    def value(self):
        return self.main_component.toPlainText()

    @value.setter
    def value(self, value):
        self.main_component.setPlainText(value)

    @property
    def max_length(self):
        """Maximum admitted length.

        :type: :class:`int`
        """
        return self._length.max

    @max_length.setter
    def max_length(self, value):
        if value < 0:
            msg = 'Expecting non negative number, got {}'
            raise ValueError(msg.format(value))
        self._length.max = value


class BoolField(BaseField):
    """Field to ask for yes or no input"""

    def __init__(self, *args, **kwargs):
        self._box = Qt.QCheckBox('')

        kwargs.setdefault('default', False)
        super(BoolField, self).__init__(*args, **kwargs)

    @property
    def main_component(self):
        return self._box

    @property
    def change_signal(self):
        return self._box.stateChanged

    @property
    def value(self):
        return self.main_component.isChecked()

    @value.setter
    def value(self, value):
        self.main_component.setChecked(value)

    def has_data(self):
        return True


class DateField(BaseField):
    """Field to introduce :class:`datetime.date` values.

    :param format: Qt's format string used to show the current value and to
                   convert values assigned to `min` , `max` and `value` .
                   Defaults to 'dd/MM/yyyy'
    :type format: :class:`str`

    :param min: minimum admitted date, defaults to :func:`datetime.date.today`
    :type min: :class:`datetime.date` or :class:`str`

    :param max: maximum admitted date, defaults to :attr:`datetime.date.max`
    :type max: :class:`datetime.date` or :class:`str`

    .. note:: if the values passed to `min` , `max` or `value`  are strings then
              a date object is parsed using the current `format`
    """

    def __init__(self, *args, format='dd/MM/yyyy', min=date.today(),
                 max=date.max, **kwargs):
        self._editor = Qt.QDateEdit()
        self._editor.setCalendarPopup(True)

        kwargs.setdefault('default', date.today())
        super(DateField, self).__init__(*args, **kwargs)

        self.format = format
        self._range = first_of_type(self.validators, DateRange)

        if self._range is None:
            self._range = DateRange()
            self.min = min
            self.max = max
        else:
            self.min = self._range.min
            self.max = self._range.max

        self.validators.append(self._range)

    @property
    def main_component(self):
        return self._editor

    @property
    def change_signal(self):
        return self.main_component.dateChanged

    @property
    def value(self):
        return self._to_date(self.main_component.date())

    @value.setter
    def value(self, value):
        self.main_component.setDate(self._to_date(value))

    def has_data(self):
        return True

    @property
    def format(self):
        """Qt's date format string used to show the date in the widget and to
        parse string values assigned to `min`, `max` and `value`.

        :type: :class:`str`
        """
        return self.main_component.displayFormat()

    @format.setter
    def format(self, value):
        self.main_component.setDisplayFormat(value)

    @property
    def min(self):
        """Minimum admitted date.

        :type: :class:`datetime.date` or date string

        .. note:: if the value passed to `min` is a string then a date is parsed
                  using current `format`
        """
        return self._range.min

    @min.setter
    def min(self, value):
        py_date = self._to_date(value)
        self.main_component.setMinimumDate(py_date)
        self._range.min = py_date

    @property
    def max(self):
        """Maximum admitted date.

        :type: :class:`datetime.date` or date string

        .. note:: if the value passed to `max` is a string then a date is parsed
                  using current `format`
        """
        return self._range.max

    @max.setter
    def max(self, value):
        py_date = self._to_date(value)
        self.main_component.setMaximumDate(py_date)
        self._range.max = py_date

    def _to_date(self, value):
        qdate = value
        if isinstance(qdate, str):
            qdate = QDate.fromString(value, self.format)
        elif not isinstance(qdate, date):
            qdate = date(qdate.year(), qdate.month(), qdate.day())
        return qdate


class TimeField(BaseField):
    """Field to introduce :class:`datetime.time` values.

    :param format: Qt's format string used to show the current value and to
                   convert values assigned to `min` , `max` and `value` .
                   Defaults to 'HH:mm:ss'
    :type format: :class:`str`

    :param min: minimum admitted time, defaults to :attr:`datetime.time.min`
    :type min: :class:`datetime.time` or :class:`str`

    :param max: maximum admitted time, defaults to :attr:`datetime.time.max`
    :type max: :class:`datetime.time` or :class:`str`

    .. note:: if the values passed to `min` , `max` or `value` are strings then
              a time object is parsed using the current `format`
    """

    def __init__(self, *args, format='HH:mm:ss', min=time.min, max=time.max,
                 **kwargs):
        self._editor = Qt.QTimeEdit()

        kwargs.setdefault('default', datetime.now().time())
        super(TimeField, self).__init__(*args, **kwargs)

        self.format = format
        self._range = first_of_type(self.validators, TimeRange)

        if self._range is None:
            self._range = TimeRange()
            self.min = min
            self.max = max
        else:
            self.min = self._range.min
            self.max = self._range.max

        self.validators.append(self._range)

    @property
    def main_component(self):
        return self._editor

    @property
    def change_signal(self):
        return self.main_component.timeChanged

    @property
    def value(self):
        return self._to_time(self.main_component.time())

    @value.setter
    def value(self, value):
        self.main_component.setTime(self._to_time(value))

    def has_data(self):
        return True

    @property
    def format(self):
        """Qt's time format string used to show the time in the widget and to
        parse string values assigned to `min`, `max` and `value`.

        :type: :class:`str`
        """
        return self.main_component.displayFormat()

    @format.setter
    def format(self, value):
        self.main_component.setDisplayFormat(value)

    @property
    def min(self):
        """Minimum admitted time.

        :type: :class:`datetime.time` or time string

        .. note:: if the value passed to `min` is a string then a time is parsed using the
                  current `format`
        """
        return self._range.min

    @min.setter
    def min(self, value):
        # first convert input to a valid time object since value can be a string
        py_time = self._to_time(value
                                )
        self.main_component.setMinimumTime(py_time)
        self._range.min = py_time

    @property
    def max(self):
        """Maximum admitted time.

        :type: :class:`datetime.time` or time string

        .. note:: if the value passed to `max` is a string then a time is parsed
                  using the current `format`
        """
        return self._range.max

    @max.setter
    def max(self, value):
        # first convert input to a valid time object since value can be a string
        py_time = self._to_time(value)

        self.main_component.setMaximumTime(py_time)
        self._range.max = py_time

    def _to_time(self, value):
        qtime = value
        if isinstance(qtime, str):
            qtime = QTime.fromString(value, self.format)
        elif not isinstance(qtime, time):
            qtime = time(qtime.hour(), qtime.minute(), qtime.second(),
                         qtime.msec())
        return qtime


class DatetimeField(BaseField):
    """Field to introduce :class:`datetime.datetime` values.

    :param format: Qt's format string used to show current value and to convert
                   values assigned to `min` , `max` and `value` .
                   Defaults to 'dd/MM/yyyy HH:mm:ss'
    :type format: :class:`str`

    :param min: minimum admitted datetime, defaults to
                :attr:`datetime.datetime.min`
    :type min: :class:`datetime.datetime` or :class:`str`

    :param max: maximum admitted datetime, defaults to
                :attr:`datetime.datetime.max`
    :type max: :class:`datetime.datetime` or :class:`str`

    .. note:: if the values passed to `min` , `max` or `value` are strings then
              a datetime object is parsed using current format
    """

    def __init__(self, *args, format='dd/MM/yyyy HH:mm:ss', min=datetime.min,
                 max=datetime.max, **kwargs):
        self._editor = Qt.QDateTimeEdit()
        self._editor.setCalendarPopup(True)

        kwargs.setdefault('default', datetime.now())
        super(DatetimeField, self).__init__(*args, **kwargs)

        self.format = format
        self._range = first_of_type(self.validators, DatetimeRange)

        if self._range is None:
            self._range = DatetimeRange()
            self.min = min
            self.max = max
        else:
            self.min = self._range.min
            self.max = self._range.max

        self.validators.append(self._range)

    @property
    def main_component(self):
        return self._editor

    @property
    def change_signal(self):
        return self.main_component.dateTimeChanged

    @property
    def min(self):
        """Minimum admitted datetime.

        :type: :class:`datetime.datetime` or datetime string

        .. note:: if the value passed to `min` is a string then a datetime is
                  parsed using current format
        """
        return self._range.min

    @min.setter
    def min(self, value):
        dt = self._to_datetime(value)
        self.main_component.setMinimumDateTime(dt)
        self._range.min = dt

    @property
    def max(self):
        """Maximum admitted datetime.

        :type: :class:`datetime.datetime` or datetime string

        .. note:: if the value passed to `max` is a string then a datetime is
                  parsed using current format
        """
        return self._range.max

    @max.setter
    def max(self, value):
        dt = self._to_datetime(value)
        self.main_component.setMaximumDateTime(dt)
        self._range.max = dt

    @property
    def format(self):
        """Qt's format string used to show current value and to convert values
        assigned to `min` , `max` and `value` .

        :type: :class:`str`
        """
        return self.main_component.displayFormat()

    @format.setter
    def format(self, value):
        self.main_component.setDisplayFormat(value)

    @property
    def value(self):
        return self._to_datetime(self.main_component.dateTime())

    @value.setter
    def value(self, value):
        self.main_component.setDateTime(self._to_datetime(value))

    def has_data(self):
        return True

    def _to_datetime(self, value):
        qdatetime = value
        if isinstance(qdatetime, str):
            qdatetime = QDateTime.fromString(value, self.format)
        elif not isinstance(qdatetime, datetime):
            qdate, qtime = qdatetime.date(), qdatetime.time()

            qdatetime = datetime(qdate.year(), qdate.month(), qdate.day(),
                                 qtime.hour(), qtime.minute(), qtime.second(),
                                 qtime.msec())
        return qdatetime


class SelectField(BaseField):
    """Field to select an option among several ones.

    The value of this field is a :class:`tuple` with the text of the selected
    option at index 0 and its value at index 1.

    `choices` argument can be an iterable or a callable that yields an iterable
    and its members can adopt several shapes:

    * If is an string then that's the option's text and value.
    * If is a subscriptable object then the text is expected at index 0 and
      value at index 1 defaulting to index 0 if is not reachable.
    * If is other kind of object then the text is it :func:`str` result and
      value is the object itself.

    .. note:: previous rules only apply for option's text or value if `get_text`
              or `get_value` aren't defined:

    :param choices: options to show
    :type choices: iterable or callable

    :param blank: whether to show or not an option meaning no selection.
    :type blank: :class:`bool`

    :param blank_text: text to show in the meaningless option(value is equal to
                       text too)
    :type blank_text: :class:`str`

    :param get_text: used to obtain option's text, can be a callable to invoke
                     using each `choices` member as first argument or a string
                     indicating the name of the attribute to read from them.
    :type get_text: callable or :class:`str`

    :param get_value: used to obtain option's value, can be a callable to invoke
                      using each `choices` member as first argument or a string
                      indicating the name of the attribute to read from them.
    :type get_text: callable or :class:`str`
    """

    def __init__(self, *args, choices=(), blank=False, blank_text='',
                 get_text=None, get_value=None, **kwargs):
        self._combo = Qt.QComboBox()
        self._combo.setEditable(False)

        self._text_getter = self._create_text_getter(get_text)
        self._value_getter = self._create_value_getter(get_value)

        self.choices = []

        self._blank_present = blank
        self._blank_text = blank_text
        if blank:
            self.add_choice(blank_text, blank_text)

        for ch in choices() if callable(choices) else choices:
            text = self._text_getter(ch)
            value = self._value_getter(ch)
            self.add_choice(text, value)

        if kwargs.get('default') is None:
            default = self.choices[0] if self.choices else ('', '')
            kwargs['default'] = default[0]
        super(SelectField, self).__init__(*args, **kwargs)

    @property
    def main_component(self):
        return self._combo

    @property
    def change_signal(self):
        return self.main_component.currentIndexChanged

    @property
    def value(self):
        """The selected option.

        .. note:: To change the current selection you can pass only the new
                  option's text or a tuple like
                  ``(option's text, option's value)``.

        :return: a :class:`tuple` like ``(option's text, option's value)``
        :rtype: :class:`tuple`
        """
        component = self.main_component
        index = component.currentIndex()
        return component.currentText(), component.itemData(index)

    @value.setter
    def value(self, new):
        if isinstance(new, str):
            text = new
        else:
            text, _ = new

        index = self.main_component.findText(text)

        if index < 0 and self.choices:
            raise ValueError('No choice with text {}'.format(text))
        self.main_component.setCurrentIndex(index)

    def has_data(self):
        return self.main_component.currentIndex() >= 0

    def add_choice(self, text, value):
        """Adds a new choice to the options list.

        :param text: text of the new option
        :type text: :class:`str`

        :param value: value of the new option
        :type value: any
        """
        self.choices.append((text, value))
        self.main_component.addItem(text, value)

    def clear(self):
        """Removes all options except the blank one if present"""
        self.main_component.clear()
        self.choices.clear()

        if self._blank_present:
            self.add_choice(self._blank_text, self._blank_text)

    @staticmethod
    def _create_text_getter(arg):
        if callable(arg):
            getter = arg
        elif isinstance(arg, str):
            getter = operator.attrgetter(arg)
        else:
            def getter(e):
                # choice can be an string
                if isinstance(e, str):
                    return e

                # at this point e must be a subscriptable object with the text
                # value at index 0
                try:
                    return e[0]
                except TypeError:
                    # non subscriptable object, the output is it str()
                    return str(e)
        return getter

    @staticmethod
    def _create_value_getter(arg):
        if callable(arg):
            getter = arg
        elif isinstance(arg, str):
            getter = operator.attrgetter(arg)
        else:
            def getter(e):
                # choice can be an string
                if isinstance(e, str):
                    return e

                try:
                    return e[1]  # try to get the value at index 1
                except IndexError:
                    return e[0]  # value not present so use text instead
                except TypeError:
                    # non subscriptable object, the output is the same element
                    return e
        return getter


class FileField(BaseField):
    """Field to input file(s).

    File paths can be entered manually and are separated by ``PATH_SEP``.
    The value of this field is always a list of paths, independently of
    the value of `multi_select`

    :param multi_select: whether to allow or not selection of several files
    :type multi_select: :class:`bool`

    :param chooser_title: text to show in the file chooser
    :type chooser_title: :class:`str`

    :param button_text: text to show in the file chooser invoker button
    :type button_text: :class:`str`

    .. seealso:: :class:`DirField`
    """

    PATHS_SEP = ';'

    def __init__(self, *args, multi_select=False, chooser_title='Choose a file',
                 button_text='Browse', **kwargs):
        # text field to show selected file(s) path(s)
        self._string = StringField()
        self._string.text = ''

        self._file_chooser = Qt.QFileDialog()

        self._browse = Qt.QPushButton('')
        self._browse.clicked.connect(self._file_chooser.exec)

        self._layout = Qt.QHBoxLayout()
        self._layout.addWidget(self._string, stretch=1)
        self._layout.addWidget(self._browse)

        kwargs.setdefault('default', [])
        super(FileField, self).__init__(*args, **kwargs)

        def _close_cb():
            joined = self.PATHS_SEP.join(self._file_chooser.selectedFiles())

            if len(joined) > self._string.max_length:
                self._string.max_length = len(joined)
            self._string.value = joined

        class _PathValidator:
            def __call__(self, field):
                if len(field.value) > 0:
                    if not all(os.path.isfile(p) for p in field.value):
                        raise ValueError('Invalid file(s) found')

        self._file_chooser.finished.connect(_close_cb)
        self.validators.append(_PathValidator())

        self.chooser_title = chooser_title
        self.button_text = button_text

        self._multi_select = None
        self.multi_select = multi_select

    @property
    def main_component(self):
        return self._layout

    @property
    def change_signal(self):
        return self._string.change_signal

    @property
    def value(self):
        paths = self._string.value
        return paths.split(self.PATHS_SEP) if paths else []

    @value.setter
    def value(self, value):
        self._string.value = self.PATHS_SEP.join(value)

    def has_data(self):
        return self._string.has_data()

    @property
    def chooser_title(self):
        """Text to show in the file chooser.

        :type: :class:`str`
        """
        return self._file_chooser.windowTitle()

    @chooser_title.setter
    def chooser_title(self, value):
        self._file_chooser.setWindowTitle(value)

    @property
    def button_text(self):
        """Text to show in the file chooser invoker button.

        :type: :class:`str`
        """
        return self._browse.text()

    @button_text.setter
    def button_text(self, value):
        self._browse.setText(value)

    @property
    def multi_select(self):
        """Whether to allow or not selection of several files.

        :type: :class:`bool`
        """
        return self._multi_select

    @multi_select.setter
    def multi_select(self, value):
        self._multi_select = value
        if value:
            self._file_chooser.setFileMode(Qt.QFileDialog.ExistingFiles)
        else:
            self._file_chooser.setFileMode(Qt.QFileDialog.ExistingFile)

    def add_filter(self, name, patterns):
        """Adds a named filter to this field. Filters do not apply to manually
        entered paths.

        For instance, if you want to show the following filters::

            Image files (*.png *.jpg)
            Text files (*.txt)
            Any files (*)

        You can add them like this::

            fi = FileField()
            fi.add_filter('Image files', ['*.png', '*.jpg'])
            fi.add_filter('Text files', ['*.txt'])
            fi.add_filter('Any files', ['*'])

        :param name: a string identifying the filter
        :type name: :class:`str`

        :param patterns: a collection of Qt's filename-wildcard patterns
        :type patterns: iterable of strings
        """
        new = '{} ({})'.format(name, ' '.join(patterns))
        filters = self._file_chooser.nameFilters()
        filters.append(new)
        self._file_chooser.setNameFilters(filters)


class DirField(BaseField):
    """Field to input a directory path.

    Dir path can be entered manually.

    :param chooser_title: text to show in the directory chooser
    :type chooser_title: :class:`str`

    :param button_text: text to show in the directory chooser invoker button
    :type button_text: :class:`str`

    .. seealso:: :class:`FileInput`
    """

    def __init__(self, *args, chooser_title='Choose a directory',
                 button_text='Browse', **kwargs):
        # text widget to show selected dir path
        self._string = StringField()
        self._string.text = ''

        self._dir_chooser = Qt.QFileDialog()
        self._dir_chooser.setFileMode(Qt.QFileDialog.Directory)
        self._dir_chooser.setOption(Qt.QFileDialog.ShowDirsOnly, True)

        self._browse = Qt.QPushButton()
        self._browse.clicked.connect(self._dir_chooser.exec)

        self._layout = Qt.QHBoxLayout()
        self._layout.addWidget(self._string, stretch=1)
        self._layout.addWidget(self._browse)

        kwargs.setdefault('default', '')
        super(DirField, self).__init__(*args, **kwargs)

        def _close_cb():
            path = self._dir_chooser.directory().absolutePath()

            if len(path) > self._string.max_length:
                self._string.max_length = len(path)
            self._string.value = path

        class _PathValidator:
            def __call__(self, field):
                if len(field.value) > 0 and not os.path.isdir(field.value):
                    raise ValueError('Invalid path')

        self._dir_chooser.finished.connect(_close_cb)
        self.validators.append(_PathValidator())

        self.chooser_title = chooser_title
        self.button_text = button_text

    @property
    def main_component(self):
        return self._layout

    @property
    def change_signal(self):
        return self._string.change_signal

    @property
    def value(self):
        return self._string.value

    @value.setter
    def value(self, value):
        self._string.value = value

    def has_data(self):
        return self._string.has_data()

    @property
    def chooser_title(self):
        """Text to show in the directory chooser.

        :type: :class:`str`
        """
        return self._dir_chooser.windowTitle()

    @chooser_title.setter
    def chooser_title(self, value):
        self._dir_chooser.setWindowTitle(value)

    @property
    def button_text(self):
        """Text to show in the directory chooser invoker button.

        :type: :class:`str`
        """
        return self._browse.text()

    @button_text.setter
    def button_text(self, value):
        self._browse.setText(value)
