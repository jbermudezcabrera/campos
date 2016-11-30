"""This example demonstrates the basics on building complete forms using campos.

It creates several fields, marking some of them as required and adding some
custom validation.

Finally fields are added to a CreationForm which have several buttons and a
custom callback connected to one of them. After added, some related fields
are grouped.
"""

__author__ = 'Juan Manuel Bermúdez Cabrera'


def fake_create_person():
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


def create_form():
    id = campos.StringField(name='id', text='Personal ID', max_length=11,
                            required=True)
    name = campos.StringField(name='name', text='Name', required=True)
    last = campos.StringField(name='last_name', text='Last name', required=True)

    val = campos.RegExp(r'\+?\d+', message='Invalid phone number')
    phone = campos.StringField(name='phone', text='Phone number',
                               validators=[val])
    address = campos.StringField(name='address', text='Home address')

    country = campos.SelectField(name='country', text='Country', blank=True,
                                 blank_text='Other', choices=['Cuba', 'EE.UU'],
                                 default='Cuba')

    fields = (id, name, last, phone, address, country)

    global form
    form = campos.CreationForm(on_save=fake_create_person, fields=fields)
    form.button('cancel').clicked.connect(form.close)
    form.setWindowTitle('Create Person')

    # group some fields
    form.group('Very personal info', ('phone', 'address'), layout='grid')
    form.group('Identification', ['id', 'name', 'last_name'])
    return form


if __name__ == '__main__':
    import os
    import sys

    # set gui api to use
    os.environ['QT_API'] = 'pyside'

    from qtpy.QtWidgets import QMessageBox, QApplication

    import campos

    # set global settings for validation type and label positions
    campos.Validation.set_current('instant')
    campos.Labelling.set_current('top')

    app = QApplication(sys.argv)
    dialog = create_form()
    sys.exit(dialog.exec_())
