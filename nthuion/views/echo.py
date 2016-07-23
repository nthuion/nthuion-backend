from .base import View


class EchoView(View):
    """returns the content, debug use"""

    def get(self):
        """
        returns the query string as JSON

        .. note::

            all values are returned as arrays

            .. code-block:: text

                /api/echo?a=b&a=c&c=d

            gives:

            .. code-block:: json

                {"a": ["b", "c"], "c": ["d"]}
        """
        return self.request.params.dict_of_lists()

    def post(self):
        """
        returns JSON body POSTed

        :statuscode 400: on invalid json
        """
        return self.request.json_body

    def put(self):
        """
        returns JSON body PUT'd

        :statuscode 400: on invalid json
        """
        return self.request.json_body
