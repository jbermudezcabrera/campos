import contextlib

from qtpy.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QMessageBox,
                            QGroupBox, QGridLayout, QHBoxLayout)

from . import sources
from .enums import Validation, ButtonType
from .utils import callable

__author__ = 'Juan Manuel Bermúdez Cabrera'


class Form(QDialog):
    """Forms are used to arrange fields in order to facilitate
    data input and validation.

    You can create a form by calling the ``Form`` constructor
    and providing fields and options::

        fields = [StringField(), SelectField(), FileField(), TextField()]
        buttons = ('reset', 'ok', 'cancel')
        form = Form(fields=fields, options=buttons)

    Or also by calling :func:`from_source` which generates form's fields
    introspecting a source object::

        class Person:
            def __init__(self, name, last_name, age):
                self.name = name
                self.last_name = last_name
                self.age = age

        p = Person('Sheldon', 'Cooper', 25)
        form = Form.from_source(p)

    You can group related fields using :func:`group` method::

        form.group('Identification', ['name', 'last_name'])

    Also you can find a field contained in the form using its name::

        field = form.field('last_name')

    and obtain it's value using dot notation::

        value = form.last_name

    Forms provide validation through :func:`validate` method which is
    called automatically when validation is set to 'instant'.

    More specialized forms can be created using :class:`CreationForm` and
    :class:`EditionForm` subclasses which provide some useful default behaviour
    for object creation and modification.

    :param validation: validation mechanism used by the form, if it's 'instant'
                       all fields are checked anytime one of them changes and
                       corresponding buttons are enabled/disabled accordingly.
                       If it's 'manual' you should invoke :func:`validate`
                       method by yourself.
    :type validation: :class:`str` or a :class:`~campos.enums.Validation` member

    :param fields: fields to add to this form
    :type fields: iterable of :class:`.Field`

    :param options: options to show in the form, these can be ``QPushButton``
                    instances or :class:`~campos.enums.ButtonType` enum members
                    (note that you can use strings too).

                    If you use ``ButtonType`` members(or string) then you can
                    connect the button with a callback passed as a keyword
                    argument.

                    For instance, if your options are ``['save', 'cancel']``
                    you can pass two keyword arguments named ``on_save`` and
                    ``on_cancel`` which will be connected to save and cancel
                    buttons. Note that the keyword(except the ``on_`` part)
                    matches the option name(``ButtonType`` member's name).

                    Buttons with a rejection role(accept, cancel, etc) will be
                    connected to form's ``close()`` method if no callback is
                    settled for them.

    :type options: iterable of :class:`str`, :class:`~campos.enums.ButtonType`
                   or ``QPushButton``

    .. seealso:: :class:`CreationForm` and :class:`EditionForm`
    """
    ACCEPTANCE_ROLES = (QDialogButtonBox.AcceptRole, QDialogButtonBox.YesRole,
                        QDialogButtonBox.ApplyRole)
    REJECTION_ROLES = (QDialogButtonBox.RejectRole, QDialogButtonBox.NoRole,
                       QDialogButtonBox.DestructiveRole)

    def __init__(self, options=('ok', 'cancel'), fields=(),
                 validation='current', **kwargs):
        super(Form, self).__init__()

        self.members_layout = QVBoxLayout()
        self.members_layout.setSpacing(10)

        self.button_box = QDialogButtonBox()

        layout = QVBoxLayout(self)
        layout.addLayout(self.members_layout)
        layout.addWidget(self.button_box)

        for opt in options:
            callback = None

            if isinstance(opt, (str, ButtonType)):
                if isinstance(opt, str):
                    callback_kw = 'on_{}'.format(opt.lower())
                else:
                    callback_kw = 'on_{}'.format(opt.name.lower())

                callback = kwargs.get(callback_kw)
            self.add_button(opt, on_click=callback)

        self.fields = []

        self._validation = None
        self.validation = validation
        self.valid = True

        for f in fields:
            self.add_field(f)

    def _enable_acceptance_btns(self, enabled):
        for btn in self.button_box.buttons():
            if self.button_box.buttonRole(btn) in self.ACCEPTANCE_ROLES:
                btn.setEnabled(enabled)

    @staticmethod
    def from_source(obj, source_kw={}, form_kw={}):
        """Creates a form introspecting fields from an object.

        Fields are generated using a suited :class:`~campos.sources.FieldSource`
        instance.

        :param obj: object to extract fields from.
        :type obj: any

        :param source_kw: keyword arguments to pass to
                          :class:`~campos.sources.FieldSource` constructor
        :type source_kw: :class:`dict`

        :param form_kw: keyword arguments to pass to :class:`Form` constructor
        :type form_kw: :class:`dict`
        """
        source = sources.get_fields_source(obj, **source_kw)

        fields = form_kw.pop('fields', [])
        fields.extend(source.fields.values())

        form = Form(fields=fields, **form_kw)

        title = type(obj).__name__.capitalize()
        form.setWindowTitle(title)
        return form

    def add_field(self, field):
        """Adds a field to this form.

        :param field: new field
        :type field: :class:`~campos.core.Field`
        """
        self.members_layout.addWidget(field)
        self.fields.append(field)

        field.validation = 'manual'
        if self.validation == Validation.INSTANT:
            field.change_signal.connect(self.validate)
            # force validation when new fields are added
            self.validate()

    def remove_field(self, name):
        """Removes and returns a field from this form using its name.

        :param name: name of the field to remove
        :type name: :class:`~core.Field`

        :returns: the removed field
        :rtype: :class:`~campos.core.Field`
        """
        field = self.field(name)
        if self.validation == Validation.INSTANT:
            field.change_signal.disconnect(self.validate)

        self.members_layout.removeWidget(field)
        self.fields.remove(field)
        return field

    def add_button(self, btn, on_click=None):
        """Adds a new button or option to form's button box and connects it
        with a callback. The new button is always returned.

        Buttons with a rejection role(accept, cancel, etc) will be connected to
        form's ``close()`` method if no callback is settled for them.

        :param btn: new option to add, can be a ``QPushButton`` instance or
                    :class:`~campos.enums.ButtonType` enum members(note that
                    you can use strings too)
        :type btn: :class:`str`, :class:`~campos.enums.ButtonType`
                   or ``QPushButton``

        :param on_click: callback to invoke whenever the button is clicked.
        :type on_click: callable

        :returns: the new button
        :rtype: ``QPushButton``
        """
        if isinstance(btn, (str, ButtonType)):
            standard_btn = ButtonType.get_member(btn).value
            button = self.button_box.addButton(standard_btn)
        else:
            self.button_box.addButton(btn, QDialogButtonBox.ActionRole)
            button = btn

        role = self.button_box.buttonRole(button)
        if role in self.REJECTION_ROLES and on_click is None:
            on_click = self.close

        if callable(on_click):
            button.clicked.connect(on_click)
        elif on_click is not None:
            raise ValueError('Expecting callable got {}'.format(type(on_click)))
        return button

    def button(self, which):
        """Finds a button given its type.

        :param which: button type to find, must be a valid member of
                      :class:`~campos.enums.ButtonType` enum(note that you can
                      use strings)
        :type which: :class:`str` or :class:`~campos.enums.ButtonType`

        :returns: the button which type matches the argument
        :rtype: ``QPushButton``

        :raises ValueError: if no button of the given type was found
        """
        if isinstance(which, (str, ButtonType)):
            btype = ButtonType.get_member(which)
            standard_btn = btype.value
            button = self.button_box.button(standard_btn)

            if button is None:
                msg = "{} is not present in form's options".format(btype)
                raise ValueError(msg)
            return button

        msg = 'Expecting {} member, got {}'.format(ButtonType.__name__, which)
        raise ValueError(msg)

    def field(self, name):
        """Find a field by its name.

        :param name: name of the field
        :type name: :class:`str`

        :return: a field
        :rtype: :class:`~campos.core.Field`

        :raise ValueError: if there is no field in the form with the given name
        """
        for field in self.fields:
            if field.name == name:
                return field
        raise ValueError('No field named {}'.format(name))

    def __getattr__(self, name):
        try:
            return self.field(name).value
        except ValueError:
            raise AttributeError('No attribute named {}'.format(name))

    @property
    def validation(self):
        """Validation mechanism used by the form.

         If it's 'instant' all fields are checked whenever one of them changes.
         If it's 'manual' you should invoke :func:`validate` method by yourself.

        :type: :class:`~campos.enums.Validation`
        """
        return self._validation

    @validation.setter
    def validation(self, value):
        previous = self._validation
        self._validation = Validation.get_member(value)

        if self._validation != previous:
            if self._validation == Validation.INSTANT:
                for f in self.fields:
                    f.change_signal.connect(self.validate)
            elif previous is not None:
                for f in self.fields:
                    f.change_signal.disconnect(self.validate)

    def validate(self, title='Invalid fields', msg=None):
        """Runs validation on every field of this form.

        This method is automatically called if form validation
        is set to 'instant', all buttons with an acceptance role
        are disabled when invalid fields are found.

        If form validation is set to 'manual' then a message is
        shown when invalid fields are found.

        :param title: title of the message shown when invalid fields are found.
                      Used only when form validation is set to 'manual'
        :type title: :class:`str`

        :param msg: text to show when invalid fields are found.
                    Used only when form validation is set to 'manual'
        :type msg: :class:`str`
        """

        self.valid = True
        for field in self.fields:
            field.validate()
            self.valid &= field.valid

        # enable all acceptance buttons
        self._enable_acceptance_btns(True)

        if not self.valid:
            if self.validation == Validation.MANUAL:
                text = 'Missing or invalid fields were found, please fix them'
                text = text if msg is None else msg
                QMessageBox.warning(self, title, text)
            else:
                self._enable_acceptance_btns(False)

    def group(self, title, fieldnames, layout='vertical'):
        """Groups fields in a common area under a title using chosen layout.

        :param title: title of the group
        :type title: :class:`str`

        :param fieldnames: names of the fields to group
        :type fieldnames: iterable of :class:`str`

        :param layout: layout manager used to arrange fields inside the group.
                       Defaults to 'vertical'.
        :type layout: one of ('vertical', 'horizontal', 'grid')
        """
        group = QGroupBox()
        group.setTitle(title)

        lay = layout.lower()
        fields = (self.field(name) for name in fieldnames)

        if lay in ('vertical', 'horizontal'):
            lay = QVBoxLayout() if lay == 'vertical' else QHBoxLayout()

            for field in fields:
                self.members_layout.removeWidget(field)
                lay.addWidget(field)

        elif lay == 'grid':
            lay = QGridLayout()
            row, column = 0, 0

            for field in fields:
                self.members_layout.removeWidget(field)
                lay.addWidget(field, row, column)

                column += 1
                if column >= 2:
                    row, column = row + 1, 0
        else:
            msg = "Expecting one of ('vertical', 'horizontal', 'grid') got {}"
            raise ValueError(msg.format(layout))

        group.setLayout(lay)
        self.members_layout.insertWidget(0, group)


class CreationForm(Form):
    """Form subclass with useful defaults to create new objects.

    This form's options defaults to ``('reset', 'save', 'cancel')``.
    Also, a :func:`reset` method is included and connected by default
    to the reset button to restore all fields in the form to their default
    values.

    .. seealso:: :class:`EditionForm`
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('options', ('reset', 'save', 'cancel'))
        kwargs.setdefault('on_reset', self.reset)
        super(CreationForm, self).__init__(**kwargs)

        # reset fields' data every time form closes
        self.finished.connect(self.reset)

    def reset(self):
        """Restores all fields in the form to their default values"""
        for field in self.fields:
            field.value = field.default

    @staticmethod
    def from_source(obj, source_kw={}, form_kw={}):
        source = sources.get_fields_source(obj, **source_kw)

        fields = form_kw.pop('fields', [])
        fields.extend(source.fields.values())

        form_kw = form_kw.copy()
        form_kw.setdefault('options', ('reset', 'save', 'cancel'))

        form = CreationForm(fields=fields, **form_kw)

        title = 'Create {}'.format(type(obj).__name__.capitalize())
        form.setWindowTitle(title)

        return form


class EditionForm(Form):
    """Form subclass with useful defaults to edit existing objects.

    This form's options defaults to ``('reset', 'save', 'cancel')``.
    Also, a :func:`reset` method is included and connected by default
    to a reset button to restore all fields in the form to their saved values.

    You can edit an existing object using :func:`edit` method which
    obtains a value for every field from the object, field names must
    be equal to attributes names in the object in order to obtain their
    current value::

        class Person:
            def __init__(self, name, last_name, age):
                self.name = name
                self.last_name = last_name
                self.age = age

        billy = Person('Billy', 'Smith', 20)
        john = Person('John', 'Bit', 26)

        # create form's fields using Person attributes
        form = EditionForm.from_source(billy)

        # prepares the form for edition and fills fields with current values
        form.edit(john)

    .. seealso:: :class:`CreationForm`
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('options', ('reset', 'save', 'cancel'))
        kwargs.setdefault('on_reset', self.reset)
        super(EditionForm, self).__init__(**kwargs)

        self._real_defaults = {}

        # reset fields to their real defaults every time form closes
        self.finished.connect(self._restore_real_defaults)

    def reset(self):
        """Restores all fields in the form to their saved values if :func:`edit`
        method has been called, otherwise restores to default values
        """
        for field in self.fields:
            field.value = field.default

    @staticmethod
    def from_source(obj, source_kw={}, form_kw={}):
        source = sources.get_fields_source(obj, **source_kw)

        fields = form_kw.pop('fields', [])
        fields.extend(source.fields.values())

        form_kw = form_kw.copy()
        form_kw.setdefault('options', ('reset', 'save', 'cancel'))

        form = EditionForm(fields=fields, **form_kw)

        title = 'Edit {}'.format(type(obj).__name__.capitalize())
        form.setWindowTitle(title)

        return form

    def edit(self, obj, disabled=()):
        """Puts the form in edition mode, filling fields with object values.

        To prevent some of the fields from been modified when editing use
        disable keyword and provide the names of the fields. Field names must
        match object attributes in order to load values correctly.

        :param obj: object used to fill form fields, only those attributes which
                    match field names will be used.
        :type obj: any

        :param disabled: names of the fields to be disabled in edition mode.
        :type disabled: iterable of :class:`str`
        """
        self._real_defaults.clear()

        for field in self.fields:
            # enable to remove settings from previous editions
            field.setEnabled(True)

            # save field's real default value
            self._real_defaults[field.name] = field.default

            # fill default and value properties with object's current values
            with contextlib.suppress(AttributeError):
                value = getattr(obj, field.name)
                field.default = value
                field.value = value

                # disable if necessary
                if field.name in disabled:
                    field.setEnabled(False)
        return self

    def _restore_real_defaults(self):
        for field in self.fields:
            if field.name in self._real_defaults:
                field.default = self._real_defaults[field.name]
        self.reset()
