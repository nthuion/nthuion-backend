import abc

from nthuion.views.base import require_permission
from nthuion.validation import (
    body_schema, Any, Required, All, Length, Range, qs_schema, Optional, Coerce
)
from nthuion.models import Vote, Comment


class FactoryRequired(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def factory(request):
        raise NotImplementedError


class VotingMixin(abc.ABC):

    @require_permission('vote')
    def get(self):
        """
        Returns the current vote

        .. sourcecode:: json

            {"value": 1}

        value may be either ``-1``, ``0`` or ``1``
        """
        return {'value': self.context.get_user_vote_value(self.user)}

    @require_permission('vote')
    @body_schema({
        Required('value'): Any(1, -1)
    })
    def put(self, body):
        """
        vote up:

        .. sourcecode:: json

            {"value": 1}

        vote down:

        .. sourcecode:: json

            {"value": -1}

        :resjson votes: on a success vote, the updated vote count is returned
        """
        vote = self.context.query_vote(self.user).first()
        if vote is None:
            vote = Vote(entry_id=self.context.id, user_id=self.user.id)
        vote.value = body['value']
        self.db.add(vote)
        self.db.flush()
        return {'votes': self.context.votes}

    @require_permission('vote')
    def delete(self):
        """
        unvote

        no body required

        :resjson votes: on a success unvote, the updated vote count is returned
        """
        self.context.query_vote(self.user).delete()
        self.db.flush()
        return {'votes': self.context.votes}


class CommentValidation:

    content = All(str, Length(max=Comment.content.type.length))


class CommentMixin(FactoryRequired):

    @qs_schema({
        Optional('offset', default=0): All(Coerce(int), Range(min=0)),
        Optional('limit', default=100): All(
            Coerce(int), Range(min=0, max=1000)),
    })
    def get(self, qs):
        """
        returns the list of comments of the object

        .. sourcecode:: json

            {
                "data": [
                    {
                        "id": 10,
                        "parent": {
                            "id": 100
                        },
                        "author": "user object",
                        "content": "comment content"
                    }
                ]
            }
        """
        query = self.db.query(Comment)\
            .filter(Comment.parent_id == self.context.id)\
            .order_by(Comment.ctime)\
            .offset(qs['offset'])\
            .limit(qs['limit'])
        return {
            'data': [comment.as_dict(self.user) for comment in query]
        }

    @require_permission('comment')
    @body_schema({
        Required('content'): CommentValidation.content
    })
    def post(self, data):
        """post a comment to the object

        .. sourcecode:: json

            {
                "content": "lorem ipsum ..."
            }
        """
        comment = Comment(
            parent=self.context,
            content=data['content'],
            author=self.user
        )
        self.db.add(comment)
        self.db.flush()
        return comment.as_dict(self.user)
