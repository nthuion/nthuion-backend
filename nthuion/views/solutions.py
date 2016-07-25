from nthuion.validation import\
    body_schema, Required, Optional, Any, All, Length
from .base import View
from nthuion.models import Solution, Tag


class SolutionValidation:

    title = All(str, Length(max=Solution.title.type.length))
    content = All(str, Length(max=Solution.content.type.length))
    question_id = Any(int, None)
    tags = [All(str, Length(max=Tag.name.type.length))]


class SolutionListView(View):

    def get(self):
        return {
            'data': [sol.as_dict() for sol in self.db.query(Solution)]
        }

    @body_schema({
        Required('title'): SolutionValidation.title,
        Required('content'): SolutionValidation.content,
        Optional('question_id', default=None): SolutionValidation.question_id,
        Required('tags'): SolutionValidation.tags
    })
    def post(self):
        """XXX: The implementation is not complete yet"""
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
