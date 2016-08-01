import datetime

from contextlib import suppress
from pyramid.httpexceptions import HTTPUnprocessableEntity
from nthuion.validation import\
    body_schema, Required, Optional, Any, All, Length
from .base import View, require_permission
from .mixins import VotingMixin, CommentMixin
from nthuion.utils import noresultfound_is_404
from nthuion.models import Solution, Tag, Issue


class SolutionValidation:

    title = All(str, Length(max=Solution.title.type.length))
    content = All(str, Length(max=Solution.content.type.length))
    issue_id = Any(int, None)
    tags = [All(str, Length(max=Tag.name.type.length))]


def issue_or_422(db, id):
    if id is None:
        return None
    obj = db.query(Issue).get(id)
    if obj is None:
        raise HTTPUnprocessableEntity(
            'issue with id {} does not exist'.format(id))
    return obj


class SolutionListView(View):

    @staticmethod
    def factory(request):
        return Solution

    def get(self):
        return {
            'data': [sol.as_dict(self.user) for sol in self.db.query(Solution)]
        }

    @require_permission('create')
    @body_schema({
        Required('title'): SolutionValidation.title,
        Required('content'): SolutionValidation.content,
        Optional('issue_id', default=None): SolutionValidation.issue_id,
        Required('tags'): SolutionValidation.tags
    })
    def post(self, body):
        """
        create a solution

        :statuscode 422: ``issue_id`` does not refer to a valid issue

        returns created solution object on success
        """
        solution = Solution(
            title=body['title'],
            content=body['content'],
            issue=issue_or_422(self.db, body['issue_id']),
            author=self.user,
            tags=Tag.from_names(self.db, body['tags'])
        )
        self.db.add(solution)
        self.db.flush()
        return solution.as_dict(self.user)


class SolutionContextMixin:

    @staticmethod
    def factory(request):
        with noresultfound_is_404():
            return request.db.query(Solution)\
                .filter(Solution.id == request.matchdict['id']).one()


class SolutionView(SolutionContextMixin, View):

    """Solution of the id"""

    def get(self):
        return self.context.as_dict(self.user)

    @require_permission('update')
    @body_schema({
        Optional('title'): SolutionValidation.title,
        Optional('content'): SolutionValidation.content,
        Optional('issue_id'): SolutionValidation.issue_id,
        Optional('tags'): SolutionValidation.tags,
    })
    def put(self, body):
        """
        update the solution

        :statuscode 422: ``issue_id`` does not refer to a valid issue

        returns updated solution object on success
        """
        obj = self.context

        with suppress(KeyError):
            obj.title = body['title']
        with suppress(KeyError):
            obj.content = body['content']
        with suppress(KeyError):
            obj.issue = issue_or_422(self.db, body['issue_id'])
        try:
            tags = body['tags']
        except KeyError:
            pass
        else:
            obj.tags = Tag.from_names(self.db, tags)
        obj.mtime = datetime.datetime.now()
        self.db.flush()
        return obj.as_dict(self.user)


class SolutionVoteView(SolutionContextMixin, VotingMixin, View):
    """Entity representing the user's vote of the issue"""


class SolutionCommentView(SolutionContextMixin, CommentMixin, View):
    pass
