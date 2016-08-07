nthuion-backend
===============

Backend of NTHU ION

.. image:: https://travis-ci.org/nthuion/nthuion-backend.svg?branch=master
    :target: https://travis-ci.org/nthuion/nthuion-backend

Resources
---------

* `API Documentation <https://nthuion.github.io/nthuion-backend/>`_
* `Frontend Repo <https://github.com/nthuion/nthuion-frontend>`_

Environment setup
-----------------

.. code-block:: bash

    python3 -m venv venv         # setup virtual environment
    source venv/bin/activate     # exports PATHs
    pip install -e ".[testing]"  # installs dependencies

Initialize database
-------------------

.. code-block:: bash

    initialize_nthuion_db development.ini

Run the development server
--------------------------

.. code-block:: bash

    uwsgi --ini-paste development.ini

The server will be running on port 6543

Run tests
---------

.. code-block:: bash

    py.test

Remove database
---------------

.. code-block:: bash

    rm nthuion.sqlite
