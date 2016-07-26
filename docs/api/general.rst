General
=======

This document describes conventions used in the API

.. http:any:: /api/*

    :statuscode 400: the request is malformed

    :statuscode 401: the user is required to authenticate, or the token is invalid

    :statuscode 403: the authenticated user is not allowed to access the resource

    :statuscode 500: there is a bug in the server, consider
                     `reporting it <https://github.com/nthuion/nthuion-backend/issues>`_
