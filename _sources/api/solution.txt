Solution
========

Solution object:

    * id -- integer
    * title -- string
    * content -- string
    * tags -- array of string
    * author -- user object
    * issue -- null / issue object (only ``id``, ``title``)
    * votes -- integer
    * ncomments -- integer
    * ctime -- string: iso8601 datetime
    * mtime -- string: iso8601 datetime or null if not modified since creation
    * user_vote -- ``0``, ``1`` or ``-1``: the current vote of the requesting user
    * views -- integer: number of views
    * popularity -- float

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
