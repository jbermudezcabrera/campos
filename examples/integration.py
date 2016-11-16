"""This example shows how to integrate campos
with your project. It launches a normal PyQt main window
with a menu bar and then it uses campos to show two forms
to create and edit persons. These forms provide validation,
default behavior for some buttons and confirmation messages.

Please note that code from line 49 to 105 is gui-library
independent so if you switch line 47 to
campos.set_views_package('pyqt5') you will be
using PyQt5(if it is installed) without modifying those lines.
"""

import functools
import sys

from PyQt4.QtGui import QApplication
from PyQt4.uic import loadUi

import campos
from campos import validators

__author__ = 'Juan Manuel Bermúdez Cabrera'


class Person:
    def __init__(self, name, age=None, address='', height=None, alive=True):
        self.name = name
        self.age = age
        self.address = address
        self.alive = alive
        self._height = height
        self.to_exclude = 'do not show this field'
        self.life = 'I was born... ' * 10
        self.curriculum = None

    def say_hello(self, other):
        return "{} is saying hello to {}".format(self.name, other.name)


if __name__ == '__main__':

    p1 = Person(__author__, age=26, address='Santa Clara, Cuba', height=1.85)

    # Application setup code
    app = QApplication(sys.argv)
    window = loadUi('person.ui')
    window.actionAbout_Qt.triggered.connect(QApplication.instance().aboutQt)

    # tell campos which gui library must use
    campos.set_views_package('pyqt4')

    # create a New Person form and and Edit Person from a Person object excluding attributes
    new, edition = campos.get_forms(p1, under=True, exclude=['to_exclude', 'curriculum'])

    # add some validation to both forms
    length = validators.StringLength(min=5, max=50)

    # creation form
    field = new.field('name')
    field.required = True
    field.validators.append(length)

    field = new.field('address')
    field.required = True

    # edition form
    field = edition.field('name')
    field.required = True
    field.validators.append(length)

    field = edition.field('address')
    field.required = True

    # add a file field to both forms
    new.add_member(campos.FileField(name='cv', text='Curriculum Vitae', ))
    edition.add_member(campos.FileField(name='cv', text='Curriculum Vitae'))


    def edit(obj):
        """Fills Edit Person form with data from a Person object,
        name data can't be changed"""
        edition.edit(obj, disabled=['name']).show()


    def save():
        """"Callback for changes savings"""
        p1.address = edition.address
        p1.age = edition.age
        p1.alive = edition.alive
        p1._height = edition._height
        p1.life = edition.life
        p1.curriculum = edition.cv[0] if edition.cv else []

        campos.Message('Changes saved correctly', type='information').show()
        edition.close()


    def cancel():
        """Callback for dialog cancel"""
        msg = campos.Message('Are you sure?', type='question')
        msg.show()

        if msg.accepted:
            edition.close()

    # connect edition form with save and cancel callback
    edition.button('save').on_click = save
    edition.button('cancel').on_click = cancel

    # connect menu actions with forms
    window.actionNew.triggered.connect(new.show)
    window.actionEdit.triggered.connect(functools.partial(edit, p1))

    window.show()
    sys.exit(app.exec())
