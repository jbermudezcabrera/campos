"""This example shows how to obtain fully functional forms
for creation and edition using your custom python object.
It also demonstrates how to prepare a form for edition of
a given object.
"""

import sys
from datetime import date
from collections import namedtuple

import campos
from campos import validators

__author__ = 'Juan Manuel Bermúdez Cabrera'

Person = namedtuple('Person', 'fullname address age birth_date height exclude_me')

person = Person('Pepito Candela Viva', 'Santa Clara, Cuba', 20,
                date.today().replace(1996), 1.85, 'excluded')

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication

    app = QApplication(sys.argv)

    # set gui api to use
    campos.set_views_package('pyqt4')

    # create a New Person form and and Edit Person from a Person object excluding an attribute
    new, edition = campos.get_forms(person, exclude=['exclude_me'])

    # add some validation to New Person Form
    name = new.field('fullname')
    name.validators.append(validators.DataRequired())
    name.min_length = 10
    name.max_length = 50

    address = new.field('address')
    address.validators.append(validators.DataRequired())

    # add a new button with a custom callback
    btn = campos.Button(text='Call lambda', role='default',
                        on_click=lambda: print('click'))
    new.add_button(btn)

    # add a new field with validation
    f = campos.StringField(name='ten', text='Up to 10 chars',
                           max_length=10)
    new.add_member(f)

    # fills Edit Person form with data from a Person object
    # full name field value can't be changed
    edition.edit(person, disabled=['fullname'])

    # show both forms
    new.show()
    sys.exit(edition.show())
