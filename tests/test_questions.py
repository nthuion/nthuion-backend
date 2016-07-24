from .base import WebTest, BaseTest
from nthuion.models import Tag, Question, User
import transaction


class RelationTest(BaseTest):

    def test(self):
        user = User(name='user')
        question = Question(
            author=user,
            title='mytitle',
            content='lorem ipsum',
            is_anonymous=False,
        )
        with transaction.manager:
            self.session.add(user)
            question.tags = Tag.from_names(self.session, 'tag1', 'tag2')
            self.session.add(question)

        q = self.session.query(Question).one()

        # test tags
        tag1, tag2 = sorted(q.tags, key=lambda x: x.name)
        self.assertEqual('tag1', tag1.name)
        self.assertEqual('tag2', tag2.name)

        with transaction.manager:
            self.session.add(
                Question(
                    author=user,
                    title='title2',
                    content='content2',
                    is_anonymous=False,
                    tags=Tag.from_names(self.session, 'tag2', 'tag3', 'tag4')
                )
            )
        self.assertEqual(4, self.session.query(Tag).count())

    def prepare_question(self, anonymous):
        with transaction.manager:
            user = User(name='user')
            question = Question(
                author=user,
                title='t',
                content='lorem ipsum',
                is_anonymous=anonymous,
            )
            self.session.add(user)
            self.session.add(question)
        return (
            self.session.query(Question).one(),
            self.session.query(User).one()
        )

    def test_anonymous(self):
        q, u = self.prepare_question(True)
        self.assertEqual(u.as_dict(), q.as_dict(viewer=u)['author'])
        self.assertEqual(None, q.as_dict(viewer=User(name='user'))['author'])
        self.assertEqual(None, q.as_dict()['author'])

    def test_not_anonymous(self):
        q, u = self.prepare_question(False)
        self.assertEqual(u.as_dict(), q.as_dict(viewer=u)['author'])
        self.assertEqual(
            u.as_dict(),
            q.as_dict(viewer=User(name='user'))['author']
        )
        self.assertEqual(u.as_dict(), q.as_dict()['author'])


class QuestionListTest(WebTest):

    def test_returns_something(self):
        res = self.app.get('/api/questions')
        self.assertTrue(res.json['data'])

    def test_post_requires_login(self):
        self.app.post(
            '/api/questions',
            status=400
        )


class QuestionTest(WebTest):

    def prepare_q(self):
        with transaction.manager:
            user = User(name='ggg')
            self.session.add(
                Question(
                    title='lorem',
                    content='c',
                    author=user,
                    is_anonymous=False
                )
            )

    def test_get(self):
        self.prepare_q()
        resp = self.app.get(
            '/api/questions/{}'.format(
                self.session.query(Question).first().id
            ),
        )
        self.assertEqual(
            'lorem', resp.json['title']
        )
        self.assertEqual(
            'c', resp.json['content']
        )
        self.assertEqual(
            'ggg', resp.json['author']['name']
        )
        self.assertEqual(
            False, resp.json['is_anonymous']
        )
        self.assertEqual(
            [], resp.json['tags']
        )

    def test_get_404(self):
        self.app.get(
            '/api/questions/404',
            status=404
        )

    def test_anony_put_401(self):
        self.prepare_q()
        self.app.put_json(
            '/api/questions/{}'.format(
                self.session.query(Question).first().id),
            {},
            status=401
        )
