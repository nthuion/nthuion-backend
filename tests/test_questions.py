from .base import WebTest


class QuestionListTest(WebTest):

    def test_returns_something(self):
        res = self.app.get('/api/questions')
        self.assertTrue(res.json['data'])


class QuestionTest(WebTest):

    def test_post_requires_login(self):
        self.app.post(
            '/api/questions',
            status=400
        )
