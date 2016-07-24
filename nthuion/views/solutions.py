from voluptuous import Schema, Required, Optional, Any
from .base import View
from nthuion.models import Solution


class SolutionListView(View):

    def get(self):
        return {
            'data': [sol.as_dict() for sol in self.db.query(Solution)]
        }

    post_schema = Schema({
        Required('title'): str,
        Required('content'): str,
        Optional('question_id', default=None): Any(int, None),
    })

    def post(self):
        body = self.post_schema(self.request.json_body)
        solution = Solution(
            title=body['title'],
            content=body['content'],
            question_id=body['question_id'],
            author=self.user
        )
        self.db.add(solution)
        self.db.flush()
        return solution.as_dict()
