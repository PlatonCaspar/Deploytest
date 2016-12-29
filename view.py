from flask_nav.elements import View, Link
import nav
from dominate import tags
import ownNavRenderer
import flask
import flask_wtf
import searchForm
import flask_login

@nav.nav.navigation()
def nav_bar():
    if True:  # flask_login.current_user.is_authenticated:
        return ownNavRenderer.ExtendedNavbar(
            title=View(tags.img(src='/static/Pictures/logo.png', width=200), 'start'),
            items=(View('Data', 'spitOut'),
                   View('Add Board', 'add__board'),
                   View('Delete Board', 'del_board')),
            right_items=(
                View('Test', 'start'),
                View('show registered Users', 'show_registered_users'),
                View('Register User', 'register_user'),
                View('Delete User', 'delete_user'),
                # View('Login', 'login'),
                View('Logout', 'logout'))
        )
    else:
        return ownNavRenderer.ExtendedNavbar(
            title=View(tags.img(src='/static/Pictures/logo.png', width=200), 'start'),
            items=(View('Data', 'spitOut'),
                   View('Add Board', 'add__board'),
                   View('Delete Board', 'del_board')),
            right_items=(
                # View(flask_login.current_user, 'start'),
                View('show registered Users', 'show_registered_users'),
                View('Register User', 'register_user'),
                View('Delete User', 'delete_user'),
                View('Login', 'login'),
                # View('Logout', 'logout'))
            )
        )


nav.nav.register_element("frontend_top", nav_bar())
