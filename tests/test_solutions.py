import transaction
from .base import WebTest
from nthuion.models import Issue, Solution, User, Tag

from hypothesis import given, strategies as st


class SolutionTest(WebTest):

    def create_issue(self):
        user = User(name='username')
        self.session.add(user)
        issue = Issue(
            title='qtitle',
            content='qcontent',
            tags=Tag.from_names(self.session, ['tag1', 'tag2', 'tag3']),
            is_anonymous=False,
            author=user,
        )
        self.token = user.acquire_token()
        self.token_header = {'Authorization': 'Token {}'.format(self.token)}
        self.session.add(issue)
        self.session.flush()
        self.uid = user.id
        self.qid = issue.id
        transaction.commit()

    def create_solution(self):
        self.create_issue()
        solution = Solution(
            issue_id=self.qid,
            title='stitle',
            content='scontent',
            author_id=self.uid,
            tags=Tag.from_names(self.session, ['a', 'b', 'c'])
        )
        self.session.add(solution)
        self.session.flush()
        self.sid = solution.id
        transaction.commit()


class SolutionListTest(SolutionTest):

    def test_get(self):
        self.create_solution()
        res = self.app.get(
            '/api/solutions'
        )
        self.assertEqual(1, len(res.json['data']))
        sol = res.json['data'][0]
        self.assertEqual('stitle', sol['title'])
        self.assertEqual('scontent', sol['content'])
        self.assertEqual(self.qid, sol['issue']['id'])
        self.assertEqual(self.uid, sol['author']['id'])
        self.assertEqual('username', sol['author']['name'])
        self.assertEqual(0, sol['votes'])

    def test_post(self):
        self.create_issue()
        res = self.app.post_json(
            '/api/solutions',
            {
                'title': 'mytitle',
                'content': 'mycontent',
                'issue_id': self.qid,
                'tags': ['a', 'b', 'c']
            },
            headers=self.token_header
        )
        assert 'id' in res.json
        assert res.json['id'] is not None
        assert 'mytitle' == res.json['title']
        assert 'mycontent' == res.json['content']
        assert self.qid == res.json['issue']['id']
        assert set('abc') == set(res.json['tags'])

    def test_post_anon(self):
        self.create_issue()
        self.app.post_json(
            '/api/solutions',
            {
                'title': 'mytitle',
                'content': 'mycontent',
                'issue_id': self.qid
            },
            status=401
        )


class SolutionSingleTest(SolutionTest):

    def test_get(self):
        self.create_solution()
        res = self.app.get(
            '/api/solutions/{}'.format(self.sid)
        )
        jobj = res.json
        assert self.sid == jobj['id']
        assert 'stitle' == jobj['title']
        assert 'scontent' == jobj['content']
        assert set('abc') == set(jobj['tags'])

    @given(
        st.booleans(),
        st.lists(st.text(max_size=25)),
        st.text(max_size=80),
        st.text(max_size=30000, average_size=100),
    )
    def test_put(self, has_issue, tags, title, content):
        self.create_solution()
        issue_id = self.qid if has_issue else None
        res = self.app.put_json(
            '/api/solutions/{}'.format(self.sid),
            {
                'issue_id': issue_id,
                'tags': tags,
                'title': title,
                'content': content
            },
            headers=self.token_header
        )
        jobj = res.json
        assert 'id' in jobj
        assert (issue_id is None) == (jobj['issue'] is None)
        if issue_id is not None:
            assert issue_id == jobj['issue']['id']
        assert set(tags) == set(jobj['tags'])
        assert title == jobj['title']
        assert content == jobj['content']


# XXX test ctime, mtime
