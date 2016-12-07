.. _building:

.. |building_ex| image:: _static/building.png

Building forms
--------------

You can also create your very own form using |name| form classes and
filling them with fields or any other Qt object you want(see *building.py* for
a more complete example)::

    # [optional] do this only if you want to use an specific Qt binding
    import os
    os.environ['QT_API'] = 'pyqt4'

    import sys
    from collections import namedtuple

    from PyQt4.QtGui import QApplication

    import campos

    # define a Person type
    Person = namedtuple('Person', 'id name last_name phone address country')

    app = QApplication(sys.argv)

    form = campos.CreationForm(validation='instant', options=('ok', 'cancel'))
    form.setWindowTitle('Manually done')

    personal_id = campos.StringField(name='id', text='ID', max_length=11,
                                     required=True)
    name = campos.StringField(name='name', text='Name')
    last = campos.StringField(name='last_name', text='Last name')
    country = campos.SelectField(name='country', text='Country',
                                 choices=['Cuba', 'EE.UU'])

    form.add_field(personal_id)
    form.add_field(name)
    form.add_field(last)
    form.add_field(country)

    # group some fields
    form.group('Very personal info', ['id', 'name', 'last_name'])

    sys.exit(form.exec_())

The code above produces the following form:

|building_ex|
