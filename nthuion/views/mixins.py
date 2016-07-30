import abc

from nthuion.views.base import require_permission
from nthuion.validation import body_schema, Any, Required, All, Length
from nthuion.models import Vote, Comment


class FactoryRequired(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def factory(request):
        raise NotImplementedError


class VotingMixin(abc.ABC):

    def query_vote(self):
        return self.db.query(Vote)\
            .filter(Vote.entry_id == self.context.id)\
            .filter(Vote.user_id == self.user.id)

    @require_permission('vote')
    def get(self):
        """
        Returns the current vote

        .. sourcecode:: json

            {"value": 1}

        value may be either ``-1``, ``0`` or ``1``
        """
        vote = self.query_vote().first()
        if vote is None:
            return {'value': 0}
        else:
            return {'value': vote.value}

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
        vote = self.query_vote().first()
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
        self.query_vote().delete()
        self.db.flush()
        return {'votes': self.context.votes}


class CommentValidation:

    content = All(str, Length(max=Comment.content.type.length))


class CommentMixin(FactoryRequired):

    def get(self):
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
        return {
            'data': [comment.as_dict() for comment in self.context.comments]
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
        return comment.as_dict()
