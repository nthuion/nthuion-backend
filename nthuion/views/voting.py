import abc

from voluptuous import Schema, Any
from nthuion.models import Vote


class VotingMixin(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def factory(request):
        raise NotImplementedError

    def query_vote(self):
        return self.db.query(Vote)\
            .filter(Vote.entry_id == self.context.id)\
            .filter(Vote.user_id == self.user.id)

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

    post_schema = Schema({
        'value': Any(1, -1)
    })

    def put(self):
        """
        vote up:

        .. sourcecode:: json

            {"value": 1}

        vote down:

        .. sourcecode:: json

            {"value": -1}
        """
        self.post_schema(self.request.json_body)
        vote = self.query_vote().first()
        if vote is None:
            vote = Vote(entry_id=self.context.id, user_id=self.user.id)
        vote.value = self.request.json_body['value']
        self.db.add(vote)

    def delete(self):
        """
        unvote

        no body required
        """
        self.query_vote().delete()
