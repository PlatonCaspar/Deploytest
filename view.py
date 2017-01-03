from flask_nav.elements import View, Link, Text, Subgroup
import nav
from dominate import tags
import ownNavRenderer

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
            items=(View('Add Board', 'add__board'),
                   View('Delete Board', 'del_board'),
                   ),

            right_items=(
                Text(tags.span(Class="glyphicon glyphicon-user")),
                Subgroup('Hello Guest',
                         View('Login', 'login'))
            )

        )
    else:
        return ownNavRenderer.ExtendedNavbar(
            title=View(tags.img(src='/static/Pictures/logo.png', width=200), 'start'),
            items=(View('Add Board', 'add__board'),
                   View('Delete Board', 'del_board')),
            right_items=(

                Text(tags.span(Class="glyphicon glyphicon-user", text='Hello, ' + get_logged_user())),
                Subgroup('Hello, ' + get_logged_user(),
                         View('show registered Users', 'show_registered_users'),
                         View('Register User', 'register_user'),
                         View('Delete User', 'delete_user'),
                         View('Logout', 'logout'))
            )
            # )
        )

        nav.nav.register_element("frontend_top", nav_bar())
