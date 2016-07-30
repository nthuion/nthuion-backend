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
