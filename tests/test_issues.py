from .base import WebTest, BaseTest
from .common import OneUserTest
from nthuion.models import Tag, Issue, User, Comment
import transaction
import datetime

from hypothesis import given, strategies as st


class RelationTest(BaseTest):

    def test(self):
        user = User(name='user')
        issue = Issue(
            author=user,
            title='mytitle',
            content='lorem ipsum',
            is_anonymous=False,
        )
        with transaction.manager:
            self.session.add(user)
            issue.tags = Tag.from_names(self.session, ['tag1', 'tag2'])
            self.session.add(issue)

        q = self.session.query(Issue).one()

        # test tags
        tag1, tag2 = sorted(q.tags, key=lambda x: x.name)
        self.assertEqual('tag1', tag1.name)
        self.assertEqual('tag2', tag2.name)

        with transaction.manager:
            self.session.add(
                Issue(
                    author=user,
                    title='title2',
                    content='content2',
                    is_anonymous=False,
                    tags=Tag.from_names(self.session, ['tag2', 'tag3', 'tag4'])
                )
            )
        self.assertEqual(4, self.session.query(Tag).count())

    def prepare_issue(self, anonymous):
        with transaction.manager:
            user = User(name='user')
            issue = Issue(
                author=user,
                title='t',
                content='lorem ipsum',
                is_anonymous=anonymous,
            )
            self.session.add(user)
            self.session.add(issue)
        return (
            self.session.query(Issue).one(),
            self.session.query(User).one()
        )

    def test_anonymous(self):
        q, u = self.prepare_issue(True)
        self.assertEqual(u.as_dict(), q.as_dict(viewer=u)['author'])
        self.assertEqual(None, q.as_dict(viewer=User(name='user'))['author'])
        self.assertEqual(None, q.as_dict(None)['author'])

    def test_not_anonymous(self):
        q, u = self.prepare_issue(False)
        self.assertEqual(u.as_dict(), q.as_dict(viewer=u)['author'])
        self.assertEqual(
            u.as_dict(),
            q.as_dict(viewer=User(name='user'))['author']
        )
        self.assertEqual(u.as_dict(), q.as_dict(None)['author'])


class IssueListTest(WebTest):

    def test_get(self):
        with transaction.manager:
            u = User(name='user123')
            self.session.add(u)
            token = u.acquire_token()
            self.session.add(
                Issue(
                    author=u,
                    is_anonymous=True,
                    content='a',
                    title='title'
                )
            )
        res = self.app.get('/api/issues')
        self.assertEqual(1, len(res.json['data']))
        qjson = res.json['data'][0]
        self.assertIsNone(qjson['author'])
        self.assertEqual(True, qjson['is_anonymous'])
        self.assertEqual('a', qjson['content'])
        self.assertEqual('title', qjson['title'])
        self.assertEqual(0, qjson['votes'])
        self.assertIn('views', qjson)
        self.assertIn('popularity', qjson)

        res = self.app.get(
            '/api/issues',
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
            '/api/issues',
            status=401
        )

    def test_post_issue(self):
        with transaction.manager:
            user = User(name='user100')
            self.session.add(user)
            token = user.acquire_token()
        self.app.post_json(
            '/api/issues',
            {
                'title': 'issue title',
                'content': 'issue content',
                'tags': ['tag1', 'tag2', 'tag3'],
                'is_anonymous': True
            },
            headers={
                'Authorization': 'Token {}'.format(token)
            }
        )
        query = self.session.query(Issue)
        self.assertEqual(1, query.count())
        issue = query.first()
        self.assertEqual('issue title', issue.title)
        self.assertEqual('issue content', issue.content)
        self.assertEqual(True, issue.is_anonymous)
        self.assertEqual('user100', issue.author.name)
        self.assertEqual(
            ['tag1', 'tag2', 'tag3'],
            sorted(tag.name for tag in issue.tags)
        )
        self.assertEqual(0, issue.votes)

    def test_issue_limit_offset(self):
        with transaction.manager:
            u = User(name='user123')
            self.session.add(u)
            for i in range(10):
                self.session.add(
                    Issue(
                        author=u,
                        is_anonymous=True,
                        content='a',
                        title='title'
                    )
                )

        jobj = self.app.get(
            '/api/issues',
            {'limit': 4}
        ).json
        assert 4 == len(jobj['data'])

        jobj = self.app.get(
            '/api/issues',
            {'offset': 7}
        ).json
        assert 3 == len(jobj['data'])

        jobj = self.app.get(
            '/api/issues',
            {'offset': 6, 'limit': 5}
        ).json
        assert 4 == len(jobj['data'])

        jobj = self.app.get(
            '/api/issues',
            {'offset': 6, 'limit': 2}
        ).json
        assert 2 == len(jobj['data'])


class ProblematicInputTest(WebTest):

    def setUp(self):
        super().setUp()
        with transaction.manager:
            user = User(name='spamposter')
            self.session.add(user)
            self.token = user.acquire_token()

    def post_issue(
        self,
        title='title',
        content='content',
        tags=['a', 'b'],
        is_anonymous=True,
        status=None
    ):
        self.app.post_json(
            '/api/issues',
            {
                'title': title,
                'content': content,
                'tags': tags,
                'is_anonymous': is_anonymous,
            },
            headers={
                'Authorization': 'Token {}'.format(self.token)
            },
            status=status
        )

    def test_invalid_title(self):
        limit = Issue.title.type.length
        self.post_issue(title='q' * limit)
        self.post_issue(title='q' * (limit + 1), status=400)

    def test_invalid_content(self):
        limit = 30000
        self.post_issue(content='c' * limit)
        self.post_issue(content='c' * limit + 'c', status=400)
        self.post_issue(content=None, status=400)

    def test_invalid_tags(self):
        self.post_issue(tags=True, status=400)
        self.post_issue(tags=['a', 'b'])
        self.post_issue(tags=['a'])
        self.post_issue(tags=['t' * Tag.name.type.length + 't'], status=400)

    def test_same_tags(self):
        self.post_issue(tags=['a', 'a', 'a'])

    def test_invalid_anonymous(self):
        self.post_issue(is_anonymous=True)
        self.post_issue(is_anonymous=False)
        self.post_issue(is_anonymous='string', status=400)


class IssueTest(WebTest):

    def prepare_q(self):
        with transaction.manager:
            user = User(name='ggg')
            self.session.add(
                Issue(
                    title='lorem',
                    content='c',
                    author=user,
                    is_anonymous=False
                )
            )

    def test_get(self):
        self.prepare_q()
        resp = self.app.get(
            '/api/issues/{}'.format(
                self.session.query(Issue).first().id
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
            '/api/issues/404',
            status=404
        )

    def test_anony_put_401(self):
        self.prepare_q()
        self.app.put_json(
            '/api/issues/{}'.format(
                self.session.query(Issue).first().id),
            {},
            status=401
        )


class OneIssueTest(OneUserTest):

    ANON = False

    def setUp(self):
        super().setUp()
        with transaction.manager:
            issue = Issue(
                title='ipsum',
                author_id=self.uid,
                content='dolor sit amet',
                tags=Tag.from_names(
                    self.session, ['consectetur', 'adipiscing', 'elit']),
                is_anonymous=self.ANON
            )
            self.session.add(issue)
        self.qid, = self.session.query(Issue.id).first()


class IssueAnonTest(OneIssueTest):

    ANON = True

    def test_this_test_is_correctly_configured(self):
        self.assertTrue(self.session.query(Issue).first().is_anonymous)

    def test_listing(self):
        res = self.app.get('/api/issues')
        self.assertIsNone(res.json['data'][0]['author'])
        res = self.app.get('/api/issues', headers=self.token_header)
        self.assertIsNotNone(res.json['data'][0]['author'])

    def test_one(self):
        res = self.app.get('/api/issues/{}'.format(self.qid))
        self.assertIsNone(res.json['author'])
        res = self.app.get(
            '/api/issues/{}'.format(self.qid),
            headers=self.token_header
        )
        self.assertIsNotNone(res.json['author'])
        self.assertEqual(0, res.json['user_vote'])

    def test_one_put(self):
        res = self.app.put_json(
            '/api/issues/{}'.format(self.qid),
            {"title": "updated title"},
            headers=self.token_header
        )
        self.assertEqual('updated title', res.json['title'])
        self.assertIsNotNone(res.json['author'])


class IssueVoteTest(OneIssueTest):

    def assertVoteValue(self, value):
        resp = self.app.get(
            '/api/issues/{}/vote'.format(self.qid),
            headers=self.token_header
        )
        self.assertEqual(
            {
                'value': value
            },
            resp.json
        )

    def voteUp(self, after):
        res = self.app.put_json(
            '/api/issues/{}/vote'.format(self.qid),
            {'value': 1},
            headers=self.token_header
        )
        self.assertEqual(
            after,
            res.json['votes'],
        )
        resp = self.app.get(
            '/api/issues/{}'.format(self.qid),
            headers=self.token_header
        )
        self.assertEqual(
            1,
            resp.json['user_vote']
        )

    def voteDown(self, after):
        res = self.app.put_json(
            '/api/issues/{}/vote'.format(self.qid),
            {'value': -1},
            headers=self.token_header
        )
        self.assertEqual(
            after,
            res.json['votes'],
        )
        resp = self.app.get(
            '/api/issues/{}'.format(self.qid),
            headers=self.token_header
        )
        self.assertEqual(
            -1,
            resp.json['user_vote']
        )

    def unvote(self, after):
        res = self.app.delete(
            '/api/issues/{}/vote'.format(self.qid),
            headers=self.token_header
        )
        self.assertEqual(
            after,
            res.json['votes'],
        )
        resp = self.app.get(
            '/api/issues/{}'.format(self.qid),
            headers=self.token_header
        )
        self.assertEqual(
            0,
            resp.json['user_vote']
        )

    def test_vote_zero(self):
        self.assertVoteValue(0)

    def test_vote_up(self):
        self.voteUp(1)
        self.assertVoteValue(1)

    def test_vote_down(self):
        self.voteDown(-1)
        self.assertVoteValue(-1)

    def test_vote_multiple(self):
        self.assertVoteValue(0)
        self.voteDown(-1)
        self.assertVoteValue(-1)
        self.unvote(0)
        self.assertVoteValue(0)
        self.voteUp(1)
        self.assertVoteValue(1)
        self.voteDown(-1)
        self.assertVoteValue(-1)


class IssueCommentTest(OneIssueTest):

    def test_get_comments(self):
        def add_comment(c):
            self.session.add(
                Comment(parent_id=self.qid, author_id=self.uid, content=c)
            )
        with transaction.manager:
            add_comment('abc')
            add_comment('def')
            add_comment('ghi')
        res = self.app.get('/api/issues/{}/comments'.format(self.qid))
        comments = [comment['content'] for comment in res.json['data']]
        self.assertEqual(3, len(comments))
        self.assertIn('abc', comments)
        self.assertIn('def', comments)
        self.assertIn('ghi', comments)

    def test_post_comment(self):
        self.app.post_json(
            '/api/issues/{}/comments'.format(self.qid),
            {
                'content': '10rem 1psum'
            },
            headers=self.token_header
        )

        self.assertEqual(
            '10rem 1psum',
            self.session.query(Comment).one().content
        )

        res = self.app.get(
            '/api/issues/{}/comments'.format(self.qid)
        )

        self.assertEqual(
            1,
            len(res.json['data'])
        )
        self.assertEqual(
            '10rem 1psum',
            res.json['data'][0]['content']
        )
        self.assertIn(
            'id',
            res.json['data'][0]
        )


def issue_parameters():
    return given(
        st.text(
            st.characters(
                blacklist_characters='\x00',
                blacklist_categories=('Cs',)),
            max_size=30000,
            average_size=100),
        st.booleans(),
        st.lists(
            st.text(
                st.characters(
                    blacklist_characters='\x00',
                    blacklist_categories=('Cs',)),
                max_size=25),
            average_size=4),
        st.text(
            st.characters(
                blacklist_characters='\x00',
                blacklist_categories=('Cs',)),
            max_size=80)
    )


class PostReturnValueTest(OneUserTest):

    @issue_parameters()
    def test_post_issues_returnes_object_with_id(
        self, content, anon, tags, title
    ):
        res = self.app.post_json(
            '/api/issues',
            dict(
                content=content,
                is_anonymous=anon,
                tags=tags,
                title=title
            ),
            headers=self.token_header
        )
        self.assertIn('id', res.json)
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(content, res.json['content'])
        self.assertEqual(set(tags), set(res.json['tags']))
        self.assertEqual(title, res.json['title'])


class PutReturnValueTest(OneIssueTest):

    @issue_parameters()
    def test_put_issue_returns_object_with_id(
        self, content, anon, tags, title
    ):
        res = self.app.put_json(
            '/api/issues/{}'.format(self.qid),
            {
                'content': content,
                'is_anonymous': anon,
                'tags': tags,
                'title': title
            },
            headers=self.token_header
        )
        self.assertIn('id', res.json)
        self.assertIsNotNone(res.json['id'])
        self.assertEqual(content, res.json['content'])
        self.assertEqual(anon, res.json['is_anonymous'])
        self.assertEqual(set(tags), set(res.json['tags']))
        self.assertEqual(title, res.json['title'])


class IssueCommentQueryTest(OneIssueTest):

    def setUp(self):
        super().setUp()
        for i in range(10):
            with transaction.manager:
                self.app.post_json(
                    '/api/issues/{}/comments'.format(self.qid),
                    {
                        'content': str(i)
                    },
                    headers=self.token_header
                )
        with transaction.manager:
            self.session.query(Comment).filter(Comment.content == '9')\
                .one().ctime -= datetime.timedelta(days=1)

    def test_ordering(self):
        jobj = self.app.get(
            '/api/issues/{}/comments'.format(self.qid)
        ).json
        assert 10 == len(jobj['data'])
        assert '9' == jobj['data'][0]['content']
        for i, comment in enumerate(jobj['data'][1:]):
            assert str(i) == comment['content']

    def test_limit(self):
        jobj = self.app.get(
            '/api/issues/{}/comments?limit=1'.format(self.qid)
        ).json

        assert 1 == len(jobj['data'])
        assert '9' == jobj['data'][0]['content']

    def test_offset(self):
        jobj = self.app.get(
            '/api/issues/{}/comments?offset=2'.format(self.qid)
        ).json

        assert 8 == len(jobj['data'])
        for i, comment in enumerate(jobj['data'], start=1):  # skip 9, 0
            assert str(i) == comment['content']

    def test_limit_and_offset(self):
        jobj = self.app.get(
            '/api/issues/{}/comments?limit=3&offset=8'.format(self.qid)
        ).json

        assert 2 == len(jobj['data'])
        assert '7' == jobj['data'][0]['content']
        assert '8' == jobj['data'][1]['content']


class ViewsPopularityTest(OneIssueTest):

    def test_views_popularity_get_updated(self):
        self.app.get(
            '/api/issues/{}'.format(self.qid)  # ip is None
        )

        with transaction.manager:
            u1 = User(name='ggg')
            self.session.add(u1)
            t1 = u1.acquire_token()
            t1b = u1.acquire_token()
            u2 = User(name='xxx')
            self.session.add(u2)
            t2 = u2.acquire_token()

        def token_visit(tok):
            return self.app.get(
                '/api/issues/{}'.format(self.qid),
                headers={'Authorization': 'Token {}'.format(tok)}
            )

        token_visit(t1)
        token_visit(t1b)
        token_visit(t2)

        self.ts.flush_traffic(self.session)

        assert 3 == self.session.query(Issue).first().views
        assert 3 == self.session.query(Issue).first().popularity

        token_visit(t1)
        token_visit(t2)
        token_visit(t2)
        token_visit(t1)

        self.ts.flush_traffic(self.session)
        assert 5 == self.session.query(Issue).first().views
        assert 5 == self.session.query(Issue).first().popularity

        # make sure the change is visible to the end user
        assert 5 == token_visit(t1).json['views']
        assert 5 == token_visit(t1).json['popularity']


class IssueOrderingTest(WebTest):

    def setUp(self):
        super().setUp()
        with transaction.manager:
            user = User(name='x')
            self.session.add(user)
            now = datetime.datetime.now()
            self.session.add(
                Issue(
                    author=user,
                    title='old',
                    content='popular',
                    popularity=1,
                    is_anonymous=False,
                    ctime=now
                )
            )
            self.session.add(
                Issue(
                    author=user, title='new', content='not-popular',
                    is_anonymous=False,
                    ctime=now + datetime.timedelta(days=1)
                )
            )

    def test_latest_first(self):
        res = self.app.get(
            '/api/issues',
            {'ordering': 'latest'}
        )
        first, second = res.json['data']
        assert ('new', 'old') == (first['title'], second['title'])

    def test_popular_first(self):
        res = self.app.get(
            '/api/issues',
            {'ordering': 'popularity'}
        )
        first, second = res.json['data']
        assert 'popular' == first['content']
        assert 'not-popular' == second['content']
        assert first['popularity'] > second['popularity']


# XXX test ctime, mtime
