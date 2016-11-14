import contextlib

from qtpy.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QMessageBox,
                            QGroupBox, QGridLayout, QHBoxLayout)

import sources
from enums import Validation, ButtonType
from utils import callable

__author__ = 'Juan Manuel Bermúdez Cabrera'


class Form(QDialog):
    # FIXME: review doc
    """Forms are used to arrange fields in order to facilitate
    data input and validation.

    You can create a form by calling the ``Form`` constructor
    and providing member fields and option buttons::

        fields = [StringField(), SelectField(), FileField(), TextField()]
        buttons = ('reset', 'accept', 'cancel')
        form = Form(validation='instant', members=fields, options=buttons)

    Or also by calling :func:`from_source` which generates the form's fields from a
    custom source object::

        class Person:
            def __init__(self, name, last_name, age):
                self.name = name
                self.last_name = last_name
                self.age = age

        p = Person('Billy', 'Smith', 20)
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
    :class:`EditionForm` subclasses which provide default behaviour
    for object creation and modification.

    :param title: form's title
    :type title: :class:`str`

    :param validation: validation mechanism used by the form, if it's 'instant'
                       all fields are checked anytime one of them changes. If it's
                       'manual' you should invoke :func:`validate` method by yourself.
    :type validation: :class:`str` or a :class:`~campos.enums.Validation` member

    :param fields: fields to add to this form, can also be a field
                    container(has 'children' attribute) like a layout or a
                    :class:`~campos.basic.widgets.Group`
    :type fields: iterable of :class:`.Field` or field containers

    :param options: options to show in the form
    :type options: iterable of :class:`str`, :class:`~campos.enums.ButtonRole` or
                   :class:`~campos.basic.widgets.Button`

    :param on_accept: callback to invoke when a button with ``ACCEPT`` role is clicked.
                      Role must be present in `options`
    :type on_accept: callable

    :param on_cancel: callback to invoke when a button with ``CANCEL`` role is clicked, defaults
                      to closing the form. Role must be present in `options`
    :type on_cancel: callable

    :param on_reset: callback to invoke when a button with ``RESET`` role is clicked.
                     Role must be present in `options`
    :type on_reset: callable

    :param on_save: callback to invoke when a button with ``SAVE`` role is clicked.
                    Role must be present in `options`
    :type on_save: callable

    :param on_help: callback to invoke when a button with ``HELP`` role is clicked.
                    Role must be present in `options`
    :type on_help: callable

    .. note:: Buttons with acceptance roles automatically invoke validation when clicked.
              To avoid this behavior add buttons manually using :func:`add_button`

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

        self.fields = []
        for f in fields:
            self.add_field(f)

        self._validation = None
        self.validation = validation

        for opt in (opt.lower() for opt in options):
            standard_btn = ButtonType.get_member(opt)
            callback_kw = 'on_{}'.format(opt)
            callback = kwargs.get(callback_kw)

            button = self.add_button(standard_btn, on_click=callback)

            if self.button_box.buttonRole(button) in self.ACCEPTANCE_ROLES:
                button.clicked.connect(self.validate)

            if not callback:
                if self.button_box.buttonRole(button) in self.REJECTION_ROLES:
                    button.clicked.connect(self.close)

    def _enable_acceptance_btns(self, enabled):
        for btn in self.button_box.buttons():
            if self.button_box.buttonRole(btn) in self.ACCEPTANCE_ROLES:
                btn.setEnabled(enabled)

    def _field_value_changed_cb(self):
        if self.validation == Validation.INSTANT:
            self.validate()

    @staticmethod
    def from_source(obj, **source_kw):
        """Creates a form extracting fields from an object.

        Fields are generated using a suited :class:`~campos.sources.FieldSource`
        object see ``campos.sources`` package for available options.

        :param obj: object to extract fields from.
        :type obj: any

        :param source_kw: keyword arguments to pass to
                          :class:`~campos.sources.FieldSource` constructor
        """
        title = type(obj).__name__.capitalize()
        source = sources.get_fields_source(obj, **source_kw)
        fields = source.fields.values()

        form = Form(fields=fields, validation='current')
        form.setWindowTitle(title)
        return form

    def add_field(self, field):
        """Adds a field to this form.

        :param field: new field
        :type field: :class:`~core.Field`
        """

        # Field validation is now under control of the form
        field.validation = 'manual'
        field.CHANGE_SIGNAL.connect(self._field_value_changed_cb)

        self.members_layout.addWidget(field)
        self.fields.append(field)

    def remove_field(self, name):
        """Removes a field of this form.

        :param name: name of the field to remove
        :type name: :class:`~core.Field`
        """
        field = self.field(name)
        self.members_layout.removeWidget(field)
        self.fields.remove(field)
        field.deleteLater()

    def add_button(self, btn, on_click=None):
        # TODO: add doc

        if isinstance(btn, (str, ButtonType)):
            standard_btn = ButtonType.get_member(btn).value
            button = self.button_box.addButton(standard_btn)
        else:
            self.button_box.addButton(btn, QDialogButtonBox.ActionRole)
            button = btn

        if callable(on_click):
            button.clicked.connect(on_click)
        return button

    def field(self, name):
        """Find a field by its name.

        :param name: name of the field
        :type name: :class:`str`

        :return: a field
        :rtype: :class:`~core.Field`

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

         If it's 'instant' all fields are checked anytime one of them changes.
         If it's 'manual' you should invoke :func:`validate` method by yourself.

        :type: :class:`~enums.Validation`
        """
        return self._validation

    @validation.setter
    def validation(self, value):
        self._validation = Validation.get_member(value)

    def validate(self, msg=None):
        """Runs validation on every field of this form.

        This method is automatically called if form validation
        is set to 'instant' and all buttons with an acceptance role
        are disabled when invalid fields are found.

        If form validation is set to 'manual' then a message is
        shown when invalid fields are found.

        :param msg: text to show when invalid fields are found.
                    Used only when form validation is set to 'manual'
        :type msg: :class:`str`

        :return: whether all fields are valid or not
        :rtype: :class:`bool`
        """
        valid = True
        for field in self.fields:
            valid &= field.validate()

        # enable all acceptance buttons
        self._enable_acceptance_btns(True)

        if not valid:
            if self.validation == Validation.MANUAL:
                text = 'Missing or invalid fields were found, please fix them'
                text = text if msg is None else msg
                QMessageBox.warning(self, 'Invalid fields', text)
            else:
                self._enable_acceptance_btns(False)
        return valid

    def group(self, title, fieldnames, layout='vertical'):
        # FIXME: doc
        """Groups fields in a common area under a title.

        :param title: title of the group
        :type title: :class:`str`

        :param fieldnames: names of the fields to group
        :type fieldnames: iterable of :class:`str`

        :param groupkw: keyword arguments to pass to
                        :class:`~campos.basic.widgets.Group` constructor
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

    This form's options defaults to ``('reset', 'accept', 'cancel')``.
    Also, a :func:`reset` method is included and connected by default
    to a reset button to restore all fields in the form to their default values.

    .. seealso:: :class:`EditionForm`
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('options', ('reset', 'accept', 'cancel'))
        kwargs.setdefault('on_reset', self.reset)
        kwargs.setdefault('title', 'Create')
        super(CreationForm, self).__init__(**kwargs)

    def close(self):
        super().close()
        self.reset()

    def reset(self):
        """Restores all fields in the form to their default values"""
        for field in self.fields:
            field.value = field.default

    @staticmethod
    def from_source(obj, **source_kw):
        title = 'Create {}'.format(type(obj).__name__.capitalize())
        source = sources.get_fields_source(obj, **source_kw)

        return CreationForm(title=title, members=source.fields.values(),
                            validation='current')


class EditionForm(Form):
    """Form subclass with useful defaults to edit existing objects.

    This form's options defaults to ``('reset', 'accept', 'cancel')``.
    Also, a :func:`reset` method is included and connected by default
    to a reset button to restore all fields in the form to their saved values.

    You can edit an existing object using :func:`edit` method which
    obtains a value for every child from the object, field names must
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
        kwargs.setdefault('title', 'Edit')
        super(EditionForm, self).__init__(**kwargs)

        self._real_defaults = {}

    def reset(self):
        """Restores all fields in the form to their saved values if :func:`edit` method has been
        called, otherwise restores to default values
        """
        for field in self.fields:
            field.value = field.default

    @staticmethod
    def from_source(obj, **source_kw):
        title = 'Edit {}'.format(type(obj).__name__.capitalize())
        source = sources.get_fields_source(obj, **source_kw)

        return EditionForm(title=title, members=source.fields.values(),
                           validation='default')

    def close(self):
        super().close()
        for field in self.fields:
            if field.name in self._real_defaults:
                field.default = self._real_defaults[field.name]
        self.reset()

    def edit(self, obj, disabled=()):
        """Puts the form in edition mode, filling fields with object values.

        To prevent some of the fields from been modified when editing use
        disable keyword and provide the names of the fields. For manually created
        forms, field names must match object attributes in order to load and store
        values correctly.

        :param obj: object used to fill form fields, only those attributes which
                    match field names will be used.
        :type obj: any

        :param disabled: names of the fields to be disabled in edition mode.
        :type disabled: iterable of :class:`str`
        """
        self._real_defaults.clear()

        for field in self.fields:
            # enable to remove settings from previous editions
            field.enable()

            # save field's real default value, the one given in the keyword argument
            self._real_defaults[field.name] = field.default

            # fill default and value properties with object's current values
            with contextlib.suppress(AttributeError):
                value = getattr(obj, field.name)
                field.default = value
                field.value = value

                # disable if necessary
                if field.name in disabled:
                    field.disable()
        return self
