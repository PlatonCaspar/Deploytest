from flask_nav.elements import View, Link, Text, Subgroup
import nav
from dominate import tags
import ownNavRenderer
from flask import request

logged_user = None


class UserGreeting(Text):
    def __init__(self):
        pass

    @property
    def text(self):
        if logged_user is not None:
            return 'Hello, {}'.format(logged_user)
        else:
            return 'Hello, Guest'


def get_logged_user():
    return logged_user


@nav.nav.navigation()
def nav_bar():
    if logged_user is None:
        return ownNavRenderer.ExtendedNavbar(
            title=View(tags.img(src='/static/Pictures/logo.png', width=200), 'start'),
            items=(View('Start', 'start'),
                   Subgroup('Board Actions',
                            View('Add Board', 'add__board'),
                            View('Delete Board', 'del_board'),
                            ),
                   Subgroup('Project Actions',
                            Text('Nothing til now'))),

            right_items=(
                Text(tags.span(Class="glyphicon glyphicon-user")),
                Subgroup('Hello Guest',
                         View('Login', 'login', last_page=request.endpoint))
            )

        )
    else:
        return ownNavRenderer.ExtendedNavbar(
            title=View(tags.img(src='/static/Pictures/logo.png', width=200), 'start'),
            items=(View('Start', 'start'),
                   Subgroup('Board Actions',
                            View('Add Board', 'add__board'),
                            View('Delete Board', 'del_board')
                            ),
                   Subgroup('Project Actions',
                            View('Add a Project', 'add_project')),

                   ),
            right_items=(

                Text(tags.span(Class="glyphicon glyphicon-user", text='Hello, ' + get_logged_user())),
                Subgroup('Hello ' + get_logged_user(),
                         View('show registered Users', 'show_registered_users'),
                         View('Register User', 'register_user'),
                         View('Delete User', 'delete_user'),
                         View('Logout', 'logout'))
            )

        )
