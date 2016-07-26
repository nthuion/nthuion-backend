General
=======

This document describes conventions used in the API

.. http:any:: /api/*

    These conventions apply to all URLs under ``/api/``

    :statuscode 400: the request is malformed

    :statuscode 401: the user is required to authenticate, or the token is invalid

    :statuscode 403: the authenticated user is not allowed to access the resource

    :statuscode 500: there is a bug in the server, consider
                     `reporting it <https://github.com/nthuion/nthuion-backend/issues>`_

.. http:options:: /api/*

    Use OPTIONS to query permissions for a certain resource.

    This also set the ``Access-Control-Allow-Origin: *`` header to allow cross site AJAX.

    Implemented by all URLs under ``/api/``.

    :<json permission: array of strings

    Example:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Access-Control-Allow-Origin: *
        Content-Length: 44
        Content-Type: application/json; charset=UTF-8

        {"permissions": ["comment", "read", "vote"]}
