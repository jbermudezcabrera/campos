"""This example demonstrates the basics on building your forms"""

import sys

from qtpy.QtWidgets import QMessageBox, QApplication

import campos
from campos.validators import DataRequired

__author__ = 'Juan Manuel Bermúdez Cabrera'


def confirm_cancel():
    answer = QMessageBox.question(None, 'Confirm', 'Are you sure?')
    if answer == QMessageBox.Yes:
        form.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # set gui api to use
    campos.API = 'pyqt4'

    # you can explore other validations in validators module
    id = campos.StringField(name='id', text='ID', max_length=11,
                            validators=[DataRequired()])

    name = campos.StringField(name='name', text='Name')
    last = campos.StringField(name='last_name', text='Last name')

    country = campos.SelectField(name='country', text='Country',
                                 choices=['Cuba', 'EE.UU'])

    form = campos.Form(validation='instant', fields=(id, name, last, country),
                       options=('save', 'cancel'), on_cancel=confirm_cancel)
    form.setWindowTitle('New Person')

    # group some fields
    form.group('Very personal info', ['id', 'name', 'last_name'], layout='grid')
    sys.exit(form.exec())
