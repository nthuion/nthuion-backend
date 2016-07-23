from .base import WebTest, BaseTest
from nthuion.models import Tag, Question, User
import transaction


class RelationTest(BaseTest):

    def test(self):
        tag1 = Tag(name='tag1')
        tag2 = Tag(name='tag2')
        user = User(name='user')
        question = Question(
            tags=[tag1, tag2],
            poster=user,
            title='mytitle',
            content='lorem ipsum',
            is_anonymous=False,
        )
        with transaction.manager:
            self.session.add(tag1)
            self.session.add(tag2)
            self.session.add(user)
            self.session.add(question)


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
