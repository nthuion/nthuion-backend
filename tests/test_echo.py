from .base import WebTest


class TestEcho(WebTest):

    payload = {'nthu': 'ion', 'afg': 984}

    def test_get(self):
        res = self.app.get(
            '/api/echo',
            params=self.payload,
            status=200)

        # query string does not have
        self.assertEqual(
            {'nthu': ['ion'], 'afg': ['984']}, res.json)

    def test_post(self):
        res = self.app.post_json(
            '/api/echo',
            params=self.payload,
            status=200)
        self.assertEqual(self.payload, res.json)

    def test_invalid_request(self):
        self.app.post(
            '/api/echo',
            params=self.payload,
            status=400
        )
        self.app.put(
            '/api/echo',
            params=self.payload,
            status=400
        )

    def test_put(self):
        res = self.app.put_json(
            '/api/echo',
            params=self.payload,
            status=200
        )
        self.assertEqual(self.payload, res.json)
