"""This example shows how to integrate campos with your project. It launches a
normal Qt main window with a menu bar and then it uses campos to show two forms
to create and edit persons. These forms provide validation and confirmation
messages.
"""


__author__ = 'Juan Manuel Bermúdez Cabrera'


def edit(form):
    """Fills Edit Person form with data from a Person object, id data can't be
    changed
    """
    global penny
    form.edit(penny, disabled=['id']).exec_()


def save(form):
    """"Callback for changes savings"""
    global penny
    penny = penny._replace(name=form.name)
    penny = penny._replace(last_name=form.last_name)
    penny = penny._replace(phone=form.phone)
    penny = penny._replace(address=form.address)
    penny = penny._replace(country=form.country)

    QMessageBox.information(None, 'Information', 'Changes saved correctly')
    form.close()


def cancel(form):
    """Callback for dialog cancel"""
    choice = QMessageBox.question(None, 'Question', 'Are you sure?',
                                  QMessageBox.Yes | QMessageBox.No)
    if choice == QMessageBox.Yes:
        form.close()


def create_forms(person):
    """Creates and return two forms, one for create and the other for edit
    Person objects.
    """
    creation, edition = campos.get_forms(person,
                                         source_kw={'exclude': ['country']})

    id = creation.field('id')
    id.text = 'Personal ID'
    id.required = True
    id.max_length = 11

    id = edition.field('id')
    id.text = 'Personal ID'
    id.required = True
    id.max_length = 11

    creation.field('name').required = True
    edition.field('name').required = True

    creation.field('last_name').required = True
    edition.field('last_name').required = True

    val = campos.RegExp(r'\+?\d+', message='Invalid phone number')

    phone = creation.field('phone')
    phone.text = 'Phone number'
    phone.validators.append(val)

    phone = edition.field('phone')
    phone.text = 'Phone number'
    phone.validators.append(val)

    creation.field('address').text = 'Home address'
    edition.field('address').text = 'Home address'

    country = campos.SelectField(name='country', text='Country', blank=True,
                                 blank_text='Other', choices=['Cuba', 'EE.UU'],
                                 default='Cuba')
    creation.add_field(country)

    country = campos.SelectField(name='country', text='Country', blank=True,
                                 blank_text='Other', choices=['Cuba', 'EE.UU'],
                                 default='Cuba')
    edition.add_field(country)

    # group some fields and connect callbacks
    creation.group('Very personal info', ('phone', 'address'), layout='grid')
    creation.group('Identification', ['id', 'name', 'last_name'])
    creation.button('cancel').clicked.connect(partial(cancel, creation))

    edition.group('Very personal info', ('phone', 'address'), layout='grid')
    edition.group('Identification', ['id', 'name', 'last_name'])
    edition.button('cancel').clicked.connect(partial(cancel, edition))
    edition.button('save').clicked.connect(partial(save, edition))
    return creation, edition


if __name__ == '__main__':
    import os
    import sys
    from functools import partial
    from collections import namedtuple

    # set gui api to use
    os.environ['QT_API'] = 'pyside'

    from qtpy.uic import loadUi
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
    window = loadUi('integration.ui')
    window.actionAbout_Qt.triggered.connect(QApplication.instance().aboutQt)

    creation, edition = create_forms(penny)

    # integrate forms generated with campos to an existing application
    window.actionNew.triggered.connect(creation.exec)
    window.actionEdit.triggered.connect(partial(edit, edition))

    window.show()
    sys.exit(app.exec_())
