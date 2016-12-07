.. _generating:

.. |creation| image:: _static/generating_creation.png
.. |creation_mod| image:: _static/generating_creation_mod.png

.. |edition| image:: _static/generating_edition.png
.. |edition_mod| image:: _static/generating_edition_mod.png

Generating forms
----------------

The quickest way to include a form created with |name| in your project
is generating it from your object's model(see *generating.py* for a more
complete example)::

    # [optional] do this only if you want to use an specific Qt binding
    import os
    os.environ['QT_API'] = 'pyqt4'

    import sys
    from collections import namedtuple

    from PyQt4.QtGui import QApplication

    import campos

    # define a Person type
    Person = namedtuple('Person', 'id name last_name phone address country')

    penny = Person(id='F4356721', name='Kaley', last_name='Cuoco', phone='',
                   address='', country='EE.UU')

    app = QApplication(sys.argv)

    # generate creation and editions forms from your object attributes
    new, edition = campos.get_forms(penny)

    new.show()
    edition.show()
    sys.exit(app.exec_())

After these lines of code you will obtain two ready to use forms
containing fields for every valid attribute encountered in your object.
It's also possible to use SQLAlchemy objects and tables:

|creation| |edition|

If you are interested in only one particular type of form you can use
*from_source* methods in form classes::

    # to obtain a form customized for creation
    form = campos.CreationForm.from_source(penny)

    # to obtain a form customized for edition
    form = campos.EditionForm.from_source(penny)

    # to obtain a neutral form
    form = campos.Form.from_source(penny)

You can modify these forms, add or remove options and fields, load an
object for edition and connect custom callbacks and validation mechanisms::

    from PyQt4.QtGui import QPushButton

    # add a new button with a custom callback
    new.add_button(QPushButton('Click me'), on_click=lambda: print('clicked'))

    # add a new field with validation
    f = campos.StringField(name='ten', text='Up to 10 chars', max_length=10)
    new.add_field(f)

    # load a custom object to edit it
    edition.edit(penny, disabled=['fullname'])

The images below show the modified creation form and the edition form with
a person's data loaded:

|creation_mod| |edition_mod|

Please note that validation is done automatically and the form can't be
committed until all fields are valid. You can customize the way validation
is done and field's label and error message positions.
