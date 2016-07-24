from .base import View
from nthuion.models import Solution


class SolutionListView(View):

    def get(self):
        return {
            'data': [sol.as_dict() for sol in self.db.query(Solution)]
        }
