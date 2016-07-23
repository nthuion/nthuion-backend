from .base import WebTest, BaseTest
from nthuion.models import Tag, Question, User
import transaction


class RelationTest(BaseTest):

    def test(self):
        user = User(name='user')
        question = Question(
            poster=user,
            title='mytitle',
            content='lorem ipsum',
            is_anonymous=False,
        )
        with transaction.manager:
            self.session.add(user)
            question.tags = Tag.from_names(self.session, 'tag1', 'tag2')
            self.session.add(question)
        tag1, tag2 = sorted(
            self.session.query(Question).one().tags, key=lambda x: x.name
        )
        self.assertEqual('tag1', tag1.name)
        self.assertEqual('tag2', tag2.name)

        with transaction.manager:
            self.session.add(
                Question(
                    poster=user,
                    title='title2',
                    content='content2',
                    is_anonymous=False,
                    tags=Tag.from_names(self.session, 'tag2', 'tag3', 'tag4')
                )
            )
        self.assertEqual(4, self.session.query(Tag).count())


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
