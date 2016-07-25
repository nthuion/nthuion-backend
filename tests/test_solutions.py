from unittest import skip
import transaction
from .base import WebTest
from nthuion.models import Question, Solution, User, Tag


class SolutionTest(WebTest):

    def create_question(self):
        user = User(name='username')
        self.session.add(user)
        question = Question(
            title='qtitle',
            content='qcontent',
            tags=Tag.from_names(self.session, ['tag1', 'tag2', 'tag3']),
            is_anonymous=False,
            author=user,
        )
        self.token = user.acquire_token()
        self.token_header = {'Authorization': 'Token {}'.format(self.token)}
        self.session.add(question)
        self.session.flush()
        self.uid = user.id
        self.qid = question.id
        transaction.commit()

    def create_solution(self):
        self.create_question()
        solution = Solution(
            question_id=self.qid,
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
        self.assertEqual(self.qid, sol['question']['id'])
        self.assertEqual(self.uid, sol['author']['id'])
        self.assertEqual('username', sol['author']['name'])
        self.assertEqual(0, sol['votes'])

    def test_post(self):
        self.create_question()
        self.app.post_json(
            '/api/solutions',
            {
                'title': 'mytitle',
                'content': 'mycontent',
                'question_id': self.qid,
                'tags': ['a', 'b', 'c']
            },
            headers=self.token_header
        )

    @skip('acl is not implemented')
    def test_post_anon(self):
        self.create_question()
        self.app.post_json(
            '/api/solutions',
            {
                'title': 'mytitle',
                'content': 'mycontent',
                'question_id': self.qid
            },
            status=401
        )
