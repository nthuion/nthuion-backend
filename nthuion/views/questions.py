import transaction
from voluptuous import Schema
from contextlib import suppress

from .base import View
from .voting import VotingMixin
from nthuion.utils import keyerror_is_bad_request, noresultfound_is_404
from nthuion.models import Question, Tag, Comment


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

        :<json title:
        :<json tags: array of strings
        :<json content:
        :<json is_anonymous: whether the question should be
                             posted anonymously
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
                tags=Tag.from_names(self.db, tags),
                is_anonymous=is_anonymous
            )
            self.db.add(question)


class QuestionContextMixin:

    @staticmethod
    def factory(request):
        with noresultfound_is_404():
            return request.db.query(Question)\
                .filter(Question.id == request.matchdict['id']).one()


class QuestionView(QuestionContextMixin, View):

    """Question of the id"""

    def get(self):
        """
        :>json title: string
        :>json content: string
        :>json tags: array of strings
        :>json author: object, with id and name
        :>json votes: number
        """
        return self.context.as_dict(self.user)

    put_schema = Schema({
        'title': str,
        'content': str,
        'tags': [str]
    })

    def put(self):
        """
        optional fields: ``title``, ``content``, ``tags``
        """
        # self.check_permission('w')
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
            obj.tags = Tag.from_names(self.db, tags)
        return obj.as_dict(self.user)


class QuestionVoteView(QuestionContextMixin, VotingMixin, View):
    """Entity representing the user's vote of the question"""


class QuestionCommentView(QuestionContextMixin, View):

    def get(self):
        """
        returns the list of comments of this question

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

    post_schema = Schema({'content': str})

    def post(self):
        """post a comment to the question

        the only required attribute is ``content``

        .. sourcecode:: json

            {
                "content": "lorem ipsum ..."
            }
        """
        body = self.request.json_body
        self.post_schema(body)
        self.db.add(
            Comment(
                parent=self.context,
                content=body['content'],
                author=self.user
            )
        )
