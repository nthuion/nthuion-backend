from pyramid.httpexceptions import HTTPError
from nthuion.views import (
    echo, auth, error_handler, issues, users, solutions, comments
)


def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_view(error_handler.error_view, context=HTTPError)

    def add(path, view, name):
        config.add_route(
            name,
            path,
            factory=getattr(view, 'factory', None),
        )
        config.add_view(
            view,
            route_name=name,
        )

    add('/api/echo', echo.EchoView, 'echo')
    add('/api/login/facebook', auth.FacebookLogin, 'facebook-login')
    add('/api/logout', auth.Logout, 'logout')
    add('/api/issues', issues.IssueList, 'issue-list')
    add('/api/issues/{id}', issues.IssueView, 'issue-object')
    add(
        '/api/issues/{id}/vote',
        issues.IssueVoteView,
        'issue-vote'
    )
    add(
        '/api/issues/{id}/comments',
        issues.IssueCommentView,
        'issue-comment'
    )

    add(
        '/api/solutions',
        solutions.SolutionListView,
        'solution-list'
    )
    add('/api/solutions/{id}', solutions.SolutionView, 'solution-object')
    add(
        '/api/solutions/{id}/vote',
        solutions.SolutionVoteView,
        'solution-vote'
    )
    add(
        '/api/solutions/{id}/comments',
        solutions.SolutionCommentView,
        'solution-comment'
    )

    add('/api/comments/{id}', comments.CommentView, 'comment-object')
    add('/api/comments/{id}/vote', comments.CommentVoteView, 'comment-vote')
    add('/api/comments/{id}/comments',
        comments.CommentCommentView,
        'comment-comment')

    add('/api/users/me', users.MeView, 'me')
    add('/api/users/{id}', users.UserView, 'user')
    add(
        '/api/users/me/emails',
        users.EmailView,
        'user-emails'
    )
    add(
        '/api/email/verify/{token}',
        users.EmailVerificationView,
        'email-verification'
    )

    # old /api/questions interface
    add('/api/questions', issues.IssueList, 'question-list')
    add('/api/questions/{id}', issues.IssueView, 'question-object')
    add(
        '/api/questions/{id}/vote',
        issues.IssueVoteView,
        'question-vote'
    )
    add(
        '/api/questions/{id}/comments',
        issues.IssueCommentView,
        'question-comment'
    )
