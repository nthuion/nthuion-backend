import transaction
from voluptuous import Schema, Required

from .base import View
from nthuion.utils import keyerror_is_bad_request
from nthuion.models import Question, Tag, ArticleTag


class QuestionList(View):
    def get(self):
        return {
            'data': [
                {
                    'id': 1,
                    'title': 'Lorem ipsum',
                    'tags': ['lorem', 'ipsum'],
                    'votes': 15,
                    'comments': 4
                },
                {
                    'id': 2,
                    'title': 'Neque porro quisquam est qui',
                    'tags': ['spam'],
                    'votes': -3,
                    'comments': 2
                }
            ]
        }

    def post(self):
        body = self.request.json_body
        with transaction.manager:
            with keyerror_is_bad_request():
                title = body['title']
                tags = [
                    Tag.get_or_create(self.db, name=name)
                    for name in body['tags']
                ]
                content = body['content']
            question = Question(
                title=title,
                content=content,
                user=self.user,
                tags=tags
            )
            self.db.add(question)
            for tag in tags:
                self.db.add(ArticleTag(article=question.id, tag=tag))


class QuestionView(View):
    @staticmethod
    def factory(request):
        return request.db.query(Question)\
            .filter(Question.id == request.matchdict['id']).one()

    def get(self):
        return self.context.as_dict()

    put_schema = Schema({
        'title': str,
        'content': str,
        'tags': [str]
    })

    def put(self):
        obj = self.context
        body = self.request.json_body
        self.put_schema(body)
        obj.title = body['title']
        obj.content = body['content']
        with transaction.manager:
            obj.tags = Tag.from_names(self.db, obj.tags)
            return obj.as_dict()
