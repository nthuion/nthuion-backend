import transaction
from .base import WebTest
from nthuion.models import Question, Solution, User, Tag


class SolutionTest(WebTest):

    def create_solution(self):
        user = User(name='username')
        self.session.add(user)
        question = Question(
            title='qtitle',
            content='qcontent',
            tags=Tag.from_names(self.session, ['tag1', 'tag2', 'tag3']),
            is_anonymous=False,
            author=user,
        )
        self.session.add(question)
        solution = Solution(
            question=question,
            title='stitle',
            content='scontent',
            author=user,
        )
        self.session.add(solution)
        self.session.flush()
        self.uid = user.id
        self.qid = question.id
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
