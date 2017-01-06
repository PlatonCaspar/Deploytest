from flask_nav.elements import View, Link, Text, Subgroup, Separator, RawTag
import nav
from dominate import tags
import ownNavRenderer
from flask import request, url_for

logged_user = None


def get_logged_user():
    return logged_user


def write_code_for_search_bar():
    bar = tags.div(tags.form(tags.div(
        tags.select(tags.option('Everywhere', value='Everywhere', Class="container-fluid panel-body"),
                    tags.option("User", value='User', Class="container-fluid panel-body"),
                    tags.option("Boards", value='Boards', Class="container-fluid panel-body"),
                    tags.option("Projects", value='Projects', Class="container-fluid panel-body"),
                    Class="form-control selectpicker",
                    style="margin: auto data-width: auto", name="Selector"),

        tags.input(Type="text", Class="form-control ", placeholder="Search", name="search_field"),

        # tags.div(
        tags.button(tags.i(Class="glyphicon glyphicon-search"),
                    Class="btn btn-default",
                    Type="submit"),
        # Class="input-group-btn"),
        Class="form-inline", style="width: 150%;"),
        Class="form-inline", style="padding-top: 3%;", action='/',
        method="post", name="nav_search_form"), Class="container-fluid")  # tags.html(),

    return bar


search_bar = RawTag(tags.li(write_code_for_search_bar()))


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
                            Text('Nothing til now')),
                   search_bar
                   ),

            right_items=(
                Text(tags.span(Class="glyphicon glyphicon-user", style="margin-right: -20px")),
                Subgroup('Hello Guest',
                         Separator,
                         View(
                             tags.div(tags.span(Class="glyphicon glyphicon-log-in", style="margin-right: 5%"), "Login"),
                             'login',
                             last_page=request.endpoint))
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
                   search_bar

                   ),
            right_items=(

                Text(tags.span(Class="glyphicon glyphicon-user container-inline", style="margin-right: -20px ")),
                Subgroup('Hello ' + get_logged_user(),
                         View('show registered Users', 'show_registered_users'),
                         View('Register User', 'register_user'),
                         View('Delete User', 'delete_user'),
                         Separator,
                         View(tags.div(tags.span(Class="glyphicon glyphicon-log-out", style="margin-right: 5%"),
                                       "Logout"), 'logout'))
            )

        )
