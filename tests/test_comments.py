import datetime
import transaction
from nthuion.models import Comment, Issue, Solution, Tag
from .common import ManyUserTest
from .base import WebTest


class BaseCommentTest(ManyUserTest):

    def create_issue(self, user_id, is_anonymous=False):
        """
        create an issue with the given user id and is_anonymous
        returns the id of the created issue
        """
        with transaction.manager:
            issue = Issue(
                author_id=user_id,
                is_anonymous=is_anonymous,
                tags=Tag.from_names(self.session, ['tag']),
                title='title',
                content='content'
            )
            self.session.add(issue)
            self.session.flush()
            return issue.id

    def create_solution(self, user_id, issue_id=None):
        """
        create a solution with the given user id and issue id,
        returns the id of the created solution
        """
        with transaction.manager:
            solution = Solution(
                author_id=user_id,
                tags=Tag.from_names(self.session, ['tag']),
                title='title',
                content='content'
            )
            self.session.add(solution)
            self.session.flush()
            return solution.id

    def create_comment(self, user_id, parent_id, content):
        """
        create a comment with the given user id, parent id and content
        returns the id of the created comment
        """
        with transaction.manager:
            comment = Comment(
                author_id=user_id,
                content=content,
                parent_id=parent_id
            )
            self.session.add(comment)
            self.session.flush()
            return comment.id


class CommentListTest(WebTest):

    def test_no_listing_available(self):
        self.app.options('/api/comments', status=404)


class CommentViewTest(BaseCommentTest):

    def test_get_comment_on_solution_comment(self):
        sid = self.create_solution(self.u1)
        cid = self.create_comment(self.u2, sid, 'comment content')

        data = self.app.get(
            '/api/comments/{}'.format(cid),
        ).json

        assert cid == data['id']
        assert 'comment content' == data['content']
        assert self.u2 == data['author']['id']
        assert 'ctime' in data
        assert data['ctime'] is not None
        assert 'mtime' in data
        assert data['mtime'] is None

    def test_get_comment_on_issue_comment(self):
        sid = self.create_solution(self.u2)
        cid = self.create_comment(self.u3, sid, 'cc')

        data = self.app.get(
            '/api/comments/{}'.format(cid)
        ).json

        assert cid == data['id']
        assert 'cc' == data['content']
        assert self.u3 == data['author']['id']

    def test_get_comment_on_comment_comment(self):
        sid = self.create_solution(self.u3)
        c1id = self.create_comment(self.u1, sid, 'cc1')
        c2id = self.create_comment(self.u2, c1id, 'cc2')

        data = self.app.get(
            '/api/comments/{}'.format(c2id)
        ).json

        assert c2id == data['id']
        assert 'cc2' == data['content']
        assert self.u2 == data['author']['id']

    def _test_update(self, cid, token, key, value):
        self.app.put_json(
            '/api/comments/{}'.format(cid),
            {key, value},
            headers=self.make_token_header(token)
        )

    def _test_put_comment_on(self, parent_id):
        cid = self.create_comment(self.u2, parent_id, 'contentx')

        assert ('contentx', self.u2, parent_id) == self.session.query(
            Comment.content, Comment.author_id, Comment.parent_id).filter(
            Comment.id == cid).first()

        res = self.app.put_json(
            '/api/comments/{}'.format(cid),
            {'content': 'updated content'},
            headers=self.make_token_header(self.tok2)
        )
        assert 'updated content' == res.json['content']
        assert 'updated content' == \
            self.session.query(Comment).get(cid).content

        assert 'ctime' in res.json
        assert res.json['ctime'] is not None
        assert 'mtime' in res.json
        assert res.json['mtime'] is not None

        self.app.put_json(
            '/api/comments/{}'.format(cid),
            {'content': 'not allowed to access'},
            headers=self.make_token_header(self.tok1),
            status=403
        )

        self.app.put_json(
            '/api/comments/{}'.format(cid),
            {'content': 'not logged in'},
            status=401
        )

    def test_put_comment_on_solution(self):
        self._test_put_comment_on(self.create_solution(self.u2))

    def test_put_comment_on_issue(self):
        self._test_put_comment_on(self.create_issue(self.u3))

    def test_put_comment_on_comment(self):
        self._test_put_comment_on(
            self.create_comment(
                self.u1,
                self.create_solution(
                    self.u2
                ),
                'content'
            )
        )

    def test_comment_on_comment(self):
        pcid = self.create_comment(self.u1, self.create_issue(self.u2), 'xxx')
        data = self.app.post_json(
            '/api/comments/{}/comments'.format(pcid),
            {'content': 'my content'},
            headers=self.make_token_header(self.tok3)
        ).json

        assert pcid == data['parent']['id']
        assert 'comment' == data['parent']['type']
        assert self.u3 == data['author']['id']
        assert 0 == data['votes']


class CommentVoteTest(BaseCommentTest):

    """Test vote on comment, copied from IssueVoteTest"""

    def setUp(self):
        super().setUp()
        self.cid = self.create_comment(
            self.u1,
            self.create_issue(self.u2),
            'content'
        )
        self.token_header = self.make_token_header(self.tok1)

    def assertVoteValue(self, value):
        resp = self.app.get(
            '/api/comments/{}/vote'.format(self.cid),
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
            '/api/comments/{}/vote'.format(self.cid),
            {'value': 1},
            headers=self.token_header
        )
        self.assertEqual(
            after,
            res.json['votes'],
        )

    def voteDown(self, after):
        res = self.app.put_json(
            '/api/comments/{}/vote'.format(self.cid),
            {'value': -1},
            headers=self.token_header
        )
        self.assertEqual(
            after,
            res.json['votes'],
        )

    def unvote(self, after):
        res = self.app.delete(
            '/api/comments/{}/vote'.format(self.cid),
            headers=self.token_header
        )
        self.assertEqual(
            after,
            res.json['votes'],
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


class CommentCommentOrderingTest(BaseCommentTest):

    def test_comments_is_ordered_by_time(self):
        sid = self.create_solution(self.u3)
        cid = self.create_comment(self.u1, sid, 'cc1')
        for i in range(10):
            with transaction.manager:
                self.app.post_json(
                    '/api/comments/{}/comments'.format(cid),
                    {
                        'content': str(i)
                    },
                    headers=self.make_token_header(self.tok3)
                )
        with transaction.manager:
            self.session.query(Comment).filter(Comment.content == '9')\
                .one().ctime -= datetime.timedelta(days=1)
        jobj = self.app.get(
            '/api/comments/{}/comments'.format(cid)
        ).json
        assert 10 == len(jobj['data'])
        assert '9' == jobj['data'][0]['content']
        for i, comment in enumerate(jobj['data'][1:]):
            assert str(i) == comment['content']
