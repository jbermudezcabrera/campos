.. campos documentation master file, created by
   sphinx-quickstart on Wed Aug 24 08:26:45 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: includes

Welcome to |name|
====================

|name| helps you to quickly create or generate fully functional forms.
Read a bit more about it or jump to `User's Guide`_

Main features
-------------

- Good integration
    You can use |name|' fields and forms like normal Qt objects anytime you
    want in your existing gui code like.

- Dynamic generation
    Just pass a source object to :func:`campos.get_forms` method and |name|
    will give you two nice ready to use forms.

- Simplified API
    Use |name|' fields as building blocks to create your forms.

- Works with major Qt bindings
    Thanks to QtPy you just need to set ``os.environ['QT_API']``
    before you use |name| if you have a favorite Qt binding, one of the
    existing ones will be used otherwise.

User's Guide
------------

This part of the documentation will show you how to get started in using |name|.

.. toctree::
   :maxdepth: 2

   installation
   quickstart

API Reference
-------------

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api/campos.rst
