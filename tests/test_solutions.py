from unittest import skip
import transaction
from .base import WebTest
from nthuion.models import Issue, Solution, User, Tag


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
        self.app.post_json(
            '/api/solutions',
            {
                'title': 'mytitle',
                'content': 'mycontent',
                'issue_id': self.qid,
                'tags': ['a', 'b', 'c']
            },
            headers=self.token_header
        )

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
