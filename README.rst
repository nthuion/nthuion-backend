NTHU ION API Backend
====================

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

    pserve development.ini

Run tests
---------

.. code-block:: bash

    py.test

Remove database
---------------

.. code-block:: bash

    rm nthuion.sqlite
