import transaction
from contextlib import suppress

from .base import View, require_permission
from .voting import VotingMixin
from nthuion.validation import body_schema, Required, Optional, All, Length
from nthuion.utils import noresultfound_is_404
from nthuion.models import Issue, Tag, Comment


class IssueValidation:

    title = All(str, Length(max=Issue.title.type.length))
    content = All(str, Length(max=Issue.content.type.length))
    tags = [All(str, Length(max=Tag.name.type.length))]
    is_anonymous = bool


class CommentValidation:

    content = All(str, Length(max=Comment.content.type.length))


class IssueList(View):

    @staticmethod
    def factory(request):
        return Issue

    def get(self):
        """Returns list of issues"""
        query = self.db.query(Issue)
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
        title = body['title']
        tags = body['tags']
        content = body['content']
        is_anonymous = body['is_anonymous']
        with transaction.manager:
            issue = Issue(
                title=title,
                content=content,
                author=self.user,
                tags=Tag.from_names(self.db, tags),
                is_anonymous=is_anonymous
            )
            self.db.add(issue)


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
        :>json title: string
        :>json content: string
        :>json tags: array of strings
        :>json author: object, with id and name
        :>json votes: number
        """
        return self.context.as_dict(self.user)

    @require_permission('update')
    @body_schema({
        Optional('title'): IssueValidation.title,
        Optional('content'): IssueValidation.content,
        Optional('tags'): IssueValidation.tags,
    })
    def put(self, body):
        # self.check_permission('w')
        obj = self.context

        with suppress(KeyError):
            obj.title = body['title']
        with suppress(KeyError):
            obj.content = body['content']
        try:
            tags = body['tags']
        except KeyError:
            pass
        else:
            obj.tags = Tag.from_names(self.db, tags)
        return obj.as_dict(self.user)


class IssueVoteView(IssueContextMixin, VotingMixin, View):
    """Entity representing the user's vote of the issue"""


class IssueCommentView(IssueContextMixin, View):

    def get(self):
        """
        returns the list of comments of this issue

        .. sourcecode:: json

            {
                "data": [
                    {
                        "id": 10,
                        "parent": {
                            "id": 100
                        },
                        "author": "comment author",
                        "content": "comment content"
                    }
                ]
            }
        """
        return {
            'data': [comment.as_dict() for comment in self.context.comments]
        }

    @require_permission('comment')
    @body_schema({
        Required('content'): CommentValidation.content
    })
    def post(self, data):
        """post a comment to the issue

        the only required attribute is ``content``

        .. sourcecode:: json

            {
                "content": "lorem ipsum ..."
            }
        """
        self.db.add(
            Comment(
                parent=self.context,
                content=data['content'],
                author=self.user
            )
        )
