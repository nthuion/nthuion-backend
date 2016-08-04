import datetime

from .base import View, require_permission
from .mixins import VotingMixin, CommentMixin, CommentValidation
from nthuion.validation import body_schema, Optional
from nthuion.models import Comment
from pyramid.httpexceptions import HTTPNotFound


class CommentContextMixin:

    @staticmethod
    def factory(request):
        ctx = request.db.query(Comment).get(request.matchdict['id'])
        if ctx is None:
            raise HTTPNotFound
        return ctx


class CommentView(CommentContextMixin, View):

    def get(self):
        """
        returns the comment object
        """
        return self.context.as_dict()

    @require_permission('update')
    @body_schema({
        Optional('content'): CommentValidation.content
    })
    def put(self, data):
        """
        update the comment, returns the updated comment object
        """
        if 'content' in data:
            self.context.content = data['content']
            self.context.mtime = datetime.datetime.now()
            self.db.flush()
        return self.context.as_dict()


class CommentCommentView(CommentContextMixin, CommentMixin, View):
    """
    comments on a specific comment
    """


class CommentVoteView(CommentContextMixin, VotingMixin, View):
    """
    vote for a comment
    """
