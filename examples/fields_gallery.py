"""Shows all field types and settings available"""

import os

# set gui api to use
os.environ['QT_API'] = 'pyqt5'

from qtpy import uic
from qtpy.QtWidgets import (QApplication, QActionGroup, QMainWindow)

import campos

__author__ = 'Juan Manuel Bermúdez Cabrera'


class FieldsGallery(QMainWindow):
    def __init__(self):
        super(FieldsGallery, self).__init__()

        uic.loadUi('fields_gallery.ui', self)
        self.fields = self.create_fields()

        for field in self.fields:
            self.fieldsLayout.addWidget(field)

        self.create_menus()
        self.btn_validate.clicked.connect(self.validate)

    def _validation_changed(self, action):
        campos.Validation.set_current(action.text())
        new = campos.Validation.get_current()

        if new == campos.Validation.INSTANT:
            self.validate()
            self.btn_validate.setEnabled(False)
        else:
            self.btn_validate.setEnabled(True)

        for field in self.fields:
            field.validation = new

    def _labelling_changed(self, action):
        campos.Labelling.set_current(action.text())
        new = campos.Labelling.get_current()

        for field in self.fields:
            field.labelling = new

    def validate(self):
        for field in self.fields:
            field.validate()

    @staticmethod
    def create_fields():
        fields = []

        fields.append(campos.BoolField(text='Boolean field', default=True))
        fields.append(campos.IntField(text='An integer'))
        fields.append(campos.FloatField(text='A float', precision=4,
                                        default=3.1416))
        fields.append(campos.StringField(text='A simple string', required=True,
                                         min_length=5))
        fields.append(campos.TextField(text='Larger string', required=True))
        fields.append(campos.FileField(text='Select file(s)', multi_select=True))
        fields.append(campos.DirField(text='Select a directory', required=True))

        colors = ['red', 'blue', 'green', 'white']
        fields.append(campos.SelectField(text='Select a color', choices=colors))
        fields.append(campos.TimeField(text='Select a time'))
        fields.append(campos.DateField(text='Select a date'))
        fields.append(campos.DatetimeField(text='Select a date and a time'))
        return fields

    def create_menus(self):
        # setup validation menu
        group = QActionGroup(self)
        group.triggered.connect(self._validation_changed)

        for member in campos.Validation:
            action = group.addAction(member.name)
            action.setCheckable(True)
            self.menuValidation.addAction(action)

            if member == campos.Validation.default():
                action.setChecked(True)
                action.trigger()

        # setup labelling menu
        group = QActionGroup(self)
        group.triggered.connect(self._labelling_changed)

        for member in campos.Labelling:
            action = group.addAction(member.name)
            action.setCheckable(True)
            self.menuLabelling.addAction(action)

            if member == campos.Labelling.default():
                action.setChecked(True)
                action.trigger()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = FieldsGallery()
    window.show()
    sys.exit(app.exec_())
