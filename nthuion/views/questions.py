import transaction
from voluptuous import Schema, Any
from contextlib import suppress

from .base import View
from nthuion.utils import keyerror_is_bad_request, noresultfound_is_404
from nthuion.models import Question, Tag, Vote


class QuestionList(View):
    def get(self):
        """Returns list of questions"""
        query = self.db.query(Question)
        user = self.user
        return {
            'data': [question.as_dict(user) for question in query]
        }

    def post(self):
        """POST a new question, required fields are ``title``, ``tags``,
        ``content``, ``is_anonymous``
        """
        body = self.request.json_body
        with transaction.manager:
            with keyerror_is_bad_request():
                title = body['title']
                tags = body['tags']
                content = body['content']
                is_anonymous = body['is_anonymous']
            question = Question(
                title=title,
                content=content,
                author=self.user,
                tags=Tag.from_names(self.db, *tags),
                is_anonymous=is_anonymous
            )
            self.db.add(question)


class QuestionView(View):

    """Question of the id"""

    @staticmethod
    def factory(request):
        with noresultfound_is_404():
            return request.db.query(Question)\
                .filter(Question.id == request.matchdict['id']).one()

    def get(self):
        """
        returns

        .. sourcecode:: json

            {
                "title": "string",
                "content": "string",
                "tags": ["list", "of", "string"],
                "author": {
                    "id": "number",
                    "name": "string"
                },
                "votes": "number"
            }
        """
        return self.context.as_dict()

    put_schema = Schema({
        'title': str,
        'content': str,
        'tags': [str]
    })

    def put(self):
        """
        optional fields: ``title``, ``content``, ``tags``
        """
        self.check_permission('w')
        obj = self.context
        body = self.request.json_body

        self.put_schema(body)

        with suppress(KeyError):
            obj.title = body['title']
        with suppress(KeyError):
            obj.content = body['content']
        try:
            tags = body['tags']
        except KeyError:
            pass
        else:
            with transaction.manager:
                obj.tags = Tag.from_names(self.db, tags)
                return obj.as_dict()


class QuestionVoteView(View):
    """Entity representing the user's vote of the question"""

    @staticmethod
    def factory(request):
        with noresultfound_is_404():
            return request.db.query(Question)\
                .filter(Question.id == request.matchdict['id']).one()

    def get(self):
        """
        Returns the current vote

        .. sourcecode:: json

            {"value": value}

        value may be either ``-1``, ``0`` or ``1``
        """
        vote = self.db.query(Vote.value)\
            .filter(Vote.entry_id == self.context.id)\
            .filter(Vote.user_id == self.user.id)\
            .scalar()
        if vote is None:
            return {'value': 0}
        else:
            return {'value': vote}

    post_schema = Schema({
        'value': Any(1, -1)
    })

    def put(self):
        """
        vote for the question

        vote up:

        .. sourcecode:: json

            {"value": 1}

        vote down:

        .. sourcecode:: json

            {"value": -1}
        """
        self.post_schema(self.request.json_body)
        vote = self.db.query(Vote)\
            .filter(Vote.entry_id == self.context.id)\
            .filter(Vote.user_id == self.user.id)\
            .first()
        if vote is None:
            vote = Vote(entry_id=self.context.id, user_id=self.user.id)
        vote.value = self.request.json_body['value']
        self.db.add(vote)

    def delete(self):
        """
        unvote

        no body required
        """
        self.db.query(Vote)\
            .filter(Vote.entry_id == self.context.id)\
            .filter(Vote.user_id == self.user.id)\
            .delete()
