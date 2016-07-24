from .base import WebTest, BaseTest
from nthuion.models import Tag, Question, User, Comment
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

    def test_get(self):
        with transaction.manager:
            u = User(name='user123')
            self.session.add(u)
            token = u.acquire_token()
            self.session.add(
                Question(
                    author=u,
                    is_anonymous=True,
                    content='a',
                    title='title'
                )
            )
        res = self.app.get('/api/questions')
        self.assertEqual(1, len(res.json['data']))
        qjson = res.json['data'][0]
        self.assertIsNone(qjson['author'])
        self.assertEqual(True, qjson['is_anonymous'])
        self.assertEqual('a', qjson['content'])
        self.assertEqual('title', qjson['title'])
        self.assertEqual(0, qjson['votes'])

        res = self.app.get(
            '/api/questions',
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        qjson = res.json['data'][0]
        self.assertEqual(1, len(res.json['data']))
        self.assertIsNotNone(qjson['author'])
        self.assertEqual('user123', qjson['author']['name'])
        self.assertEqual(0, qjson['votes'])

    def test_post_requires_login(self):
        self.app.post(
            '/api/questions',
            status=400
        )

    def test_post_question(self):
        with transaction.manager:
            user = User(name='user100')
            self.session.add(user)
            token = user.acquire_token()
        self.app.post_json(
            '/api/questions',
            {
                'title': 'question title',
                'content': 'question content',
                'tags': ['tag1', 'tag2', 'tag3'],
                'is_anonymous': True
            },
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        query = self.session.query(Question)
        self.assertEqual(1, query.count())
        question = query.first()
        self.assertEqual('question title', question.title)
        self.assertEqual('question content', question.content)
        self.assertEqual(True, question.is_anonymous)
        self.assertEqual('user100', question.author.name)
        self.assertEqual(
            ['tag1', 'tag2', 'tag3'],
            sorted(tag.name for tag in question.tags)
        )
        self.assertEqual(0, question.votes)


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
        self.assertEqual(
            0, resp.json['votes']
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


class OneQuestionTest(WebTest):

    def setUp(self):
        super().setUp()
        with transaction.manager:
            user = User(name='lorem')
            question = Question(
                title='ipsum',
                author=user,
                content='dolor sit amet',
                tags=Tag.from_names(
                    self.session, 'consectetur', 'adipiscing', 'elit'),
                is_anonymous=False
            )
            self.session.add(user)
            self.token = user.acquire_token()
            self.token_header = {
                'Authorization': 'Token {}'.format(self.token)
            }
            self.session.add(question)
        self.qid, = self.session.query(Question.id).first()


class QuestionVoteTest(OneQuestionTest):

    def assertVoteValue(self, value):
        resp = self.app.get(
            '/api/questions/{}/vote'.format(self.qid),
            headers=self.token_header
        )
        self.assertEqual(
            {
                'value': value
            },
            resp.json
        )

    def voteUp(self):
        return self.app.put_json(
            '/api/questions/{}/vote'.format(self.qid),
            {'value': 1},
            headers=self.token_header
        )

    def voteDown(self):
        return self.app.put_json(
            '/api/questions/{}/vote'.format(self.qid),
            {'value': -1},
            headers=self.token_header
        )

    def unvote(self):
        return self.app.delete(
            '/api/questions/{}/vote'.format(self.qid),
            headers=self.token_header
        )

    def test_vote_zero(self):
        self.assertVoteValue(0)

    def test_vote_up(self):
        self.voteUp()
        self.assertVoteValue(1)

    def test_vote_down(self):
        self.voteDown()
        self.assertVoteValue(-1)

    def test_vote_multiple(self):
        self.assertVoteValue(0)
        self.voteDown()
        self.assertVoteValue(-1)
        self.unvote()
        self.assertVoteValue(0)
        self.voteUp()
        self.assertVoteValue(1)
        self.voteDown()
        self.assertVoteValue(-1)


class QuestionCommentTest(OneQuestionTest):

    def test_post_comment(self):
        self.app.post_json(
            '/api/questions/{}/comments'.format(self.qid),
            {
                'content': '10rem 1psum'
            },
            headers=self.token_header
        )

        self.assertEqual(
            '10rem 1psum',
            self.session.query(Comment).one().content
        )
