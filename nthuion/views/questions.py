from .base import View


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
