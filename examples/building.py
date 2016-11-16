"""This example demonstrates the basics on building your forms"""

import os
import sys

# set gui api to use
os.environ['QT_API'] = 'pyside'

from qtpy.QtWidgets import QMessageBox, QApplication

import campos

__author__ = 'Juan Manuel Bermúdez Cabrera'


def confirm_cancel():
    options = QMessageBox.Yes | QMessageBox.No
    answer = QMessageBox.question(None, 'Confirm', 'Are you sure?', options)

    if answer == QMessageBox.Yes:
        form.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(type(app))

    id = campos.StringField(name='id', text='ID', max_length=11, required=True)
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
