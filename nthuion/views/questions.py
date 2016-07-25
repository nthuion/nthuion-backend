import transaction
from contextlib import suppress

from .base import View, require_permission
from .voting import VotingMixin
from nthuion.validation import body_schema, Required, Optional, All, Length
from nthuion.utils import noresultfound_is_404
from nthuion.models import Question, Tag, Comment


class QuestionValidation:

    title = All(str, Length(max=Question.title.type.length))
    content = All(str, Length(max=Question.content.type.length))
    tags = [All(str, Length(max=Tag.name.type.length))]
    is_anonymous = bool


class CommentValidation:

    content = All(str, Length(max=Comment.content.type.length))


class QuestionList(View):

    @staticmethod
    def factory(request):
        return Question

    def get(self):
        """Returns list of questions"""
        query = self.db.query(Question)
        user = self.user
        return {
            'data': [question.as_dict(user) for question in query]
        }

    @require_permission('create')
    @body_schema({
        Required('title'): QuestionValidation.title,
        Required('content'): QuestionValidation.content,
        Required('tags'): QuestionValidation.tags,
        Required('is_anonymous'): QuestionValidation.is_anonymous
    })
    def post(self, body):
        title = body['title']
        tags = body['tags']
        content = body['content']
        is_anonymous = body['is_anonymous']
        with transaction.manager:
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

    @require_permission('update')
    @body_schema({
        Optional('title'): QuestionValidation.title,
        Optional('content'): QuestionValidation.content,
        Optional('tags'): QuestionValidation.tags,
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

    @require_permission('comment')
    @body_schema({
        Required('content'): CommentValidation.content
    })
    def post(self, data):
        """post a comment to the question

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
