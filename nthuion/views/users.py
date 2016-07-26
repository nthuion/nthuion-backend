from nthuion.models import User
from nthuion.utils import noresultfound_is_404
from .base import View


class UserView(View):
    """The user with the id"""

    @staticmethod
    def factory(request):
        id = request.matchdict['id']
        with noresultfound_is_404():
            return request.db.query(User).filter(User.id == id).one()

    def get(self):
        """returns the information about the user incl. id, name"""
        return self.context.as_dict()


class MeView(UserView):

    @staticmethod
    def factory(request):
        return request.authenticated_userid

    def get(self):
        """
        returns the currently logged in user object, with an additional
        attribute ``authenticated``

        if the user is not logged in, all attributes will be null
        """
        user = self.context
        if user is None:
            return {
                'id': None,
                'name': None,
                'avatar_url': None,
                'authenticated': False,
            }
        else:
            return {
                **user.as_dict(),
                'authenticated': True,
            }
