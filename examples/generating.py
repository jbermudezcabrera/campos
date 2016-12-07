"""This example demonstrates the basics on generating forms from your models
using campos.

This example creates the exact same form that ``building`` example but uses
generated fields instead.
"""

__author__ = 'Juan Manuel Bermúdez Cabrera'


def fake_create_person(form):
    if form.valid:
        msg = 'ID: {}<br/>'.format(form.id)
        msg += 'Name: {}<br/>'.format(form.name)
        msg += 'Last name: {}<br/>'.format(form.last_name)
        msg += 'Phone: {}<br/>'.format(form.phone)
        msg += 'Address: {}<br/>'.format(form.address)
        msg += 'Country: {}<br/>'.format(form.country[0])

        msg = 'New person created correctly with values:<br/>{}'.format(msg)
        msg = '<html>{}</html>'.format(msg)

        QMessageBox.information(None, 'Created', msg)
        form.close()


def create_form(person):
    country = campos.SelectField(name='country', text='Country', blank=True,
                                 blank_text='Other', choices=['Cuba', 'EE.UU'],
                                 default='Cuba')

    form = campos.CreationForm.from_source(person,
                                           source_kw={'exclude': ['country']},
                                           form_kw={'fields': [country]})
    form.button('save').clicked.connect(partial(fake_create_person, form))

    id = form.field('id')
    id.text = 'Personal ID'
    id.required = True
    id.max_length = 11

    form.field('name').required = True
    form.field('last_name').required = True

    val = campos.RegExp(r'\+?\d+', message='Invalid phone number')
    phone = form.field('phone')
    phone.text = 'Phone number'
    phone.validators.append(val)

    form.field('address').text = 'Home address'

    # group some fields
    form.group('Very personal info', ('phone', 'address'), layout='grid')
    form.group('Identification', ['id', 'name', 'last_name'])
    form.validate()
    return form


if __name__ == '__main__':
    import os
    import sys
    from functools import partial
    from collections import namedtuple

    # set gui api to use
    os.environ['QT_API'] = 'pyside'

    from qtpy.QtWidgets import QMessageBox, QApplication

    import campos

    # define a Person type
    Person = namedtuple('Person', 'id name last_name phone address country')

    # create a person object
    penny = Person(id='F4356721', name='Kaley', last_name='Cuoco', phone='',
                   address='', country='EE.UU')

    # set global settings for validation type and label positions
    campos.Validation.set_current('instant')
    campos.Labelling.set_current('top')

    app = QApplication(sys.argv)
    dialog = create_form(penny)
    sys.exit(dialog.exec_())
