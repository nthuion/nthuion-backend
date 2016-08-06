from contextlib import suppress
import datetime

from .base import View, require_permission
from .mixins import VotingMixin, CommentMixin
from nthuion.validation import (
    body_schema, Required, Optional, All, Length,
    qs_schema, Coerce, Range
)
from nthuion.utils import noresultfound_is_404
from nthuion.models import Issue, Tag


class IssueValidation:

    title = All(str, Length(max=Issue.title.type.length))
    content = All(str, Length(max=Issue.content.type.length))
    tags = [All(str, Length(max=Tag.name.type.length))]
    is_anonymous = bool


class IssueList(View):

    @staticmethod
    def factory(request):
        return Issue

    @qs_schema({
        Optional('offset', default=0): All(Coerce(int), Range(min=0)),
        Optional('limit', default=100): All(
            Coerce(int), Range(min=0, max=1000)),
    })
    def get(self, qs):
        """Returns list of issues"""
        query = self.db.query(Issue)\
            .offset(qs['offset'])\
            .limit(qs['limit'])
        user = self.user
        return {
            'data': [issue.as_dict(user) for issue in query]
        }

    @require_permission('create')
    @body_schema({
        Required('title'): IssueValidation.title,
        Required('content'): IssueValidation.content,
        Required('tags'): IssueValidation.tags,
        Required('is_anonymous'): IssueValidation.is_anonymous
    })
    def post(self, body):
        """
        create a issue, returns the created issue object on success
        """
        title = body['title']
        tags = body['tags']
        content = body['content']
        is_anonymous = body['is_anonymous']
        issue = Issue(
            title=title,
            content=content,
            author=self.user,
            tags=Tag.from_names(self.db, tags),
            is_anonymous=is_anonymous
        )
        self.db.add(issue)
        self.db.flush()
        return issue.as_dict(self.user)


class IssueContextMixin:

    @staticmethod
    def factory(request):
        with noresultfound_is_404():
            return request.db.query(Issue)\
                .filter(Issue.id == request.matchdict['id']).one()


class IssueView(IssueContextMixin, View):

    """Issue of the id"""

    def get(self):
        """
        returns the issue object
        """
        return self.context.as_dict(self.user)

    @require_permission('update')
    @body_schema({
        Optional('title'): IssueValidation.title,
        Optional('content'): IssueValidation.content,
        Optional('tags'): IssueValidation.tags,
        Optional('is_anonymous'): IssueValidation.is_anonymous,
    })
    def put(self, body):
        """
        update the issue

        returns the updated issue object on success
        """
        obj = self.context

        with suppress(KeyError):
            obj.title = body['title']
        with suppress(KeyError):
            obj.content = body['content']
        with suppress(KeyError):
            obj.is_anonymous = body['is_anonymous']
        try:
            tags = body['tags']
        except KeyError:
            pass
        else:
            obj.tags = Tag.from_names(self.db, tags)
        obj.mtime = datetime.datetime.now()
        self.db.flush()
        return obj.as_dict(self.user)


class IssueVoteView(IssueContextMixin, VotingMixin, View):
    """Entity representing the user's vote of the issue"""


class IssueCommentView(IssueContextMixin, CommentMixin, View):
    """Comments for the issue"""
