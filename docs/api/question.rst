Question (deprecated)
=====================

Question is deprecated in favor of Issue.

Issue object:

    * id -- integer
    * title -- string
    * content -- string
    * tags -- array of string
    * author -- null / user object
    * votes -- integer
    * ncomments -- integer
    * ctime -- string: iso8601 datetime
    * mtime -- string: iso8601 datetime or null if not modified since creation

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

.. autoapi:: /api/questions
