Solution
========

Solution object:

    * id -- integer
    * title -- string
    * content -- string
    * tags -- array of string
    * author -- null / user object
    * issue -- null / issue object (only ``id``, ``title``)
    * votes -- integer
    * ncomments -- integer

============= ==============
Role          Permission
============= ==============
Authenticated create
------------- --------------
Owner         update
------------- --------------
Authenticated comment
------------- --------------
Authenticated vote
============= ==============

.. autoapi:: /api/solutions
