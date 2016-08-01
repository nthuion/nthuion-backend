Comment
=======

Comment object:

    * id -- integer
    * content -- string
    * parent -- object with
        * ``id`` -- integer
        * ``type`` -- string one of ``"issue"``, ``"question"``, ``"comment"``
    * author -- user object
    * votes -- integer
    * ncomments -- integer
    * ctime -- string: iso8601 datetime
    * mtime -- string: iso8601 datetime or null if not modified since creation

============= ==============
Role          Permission
============= ==============
Owner         update
------------- --------------
Authenticated comment
------------- --------------
Authenticated vote
============= ==============

.. autoapi:: /api/comments
