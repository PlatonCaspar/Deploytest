from flask_nav.elements import View, Link, Text, Subgroup, Separator, RawTag
import nav
from dominate import tags
import ownNavRenderer
from flask import request, url_for
from flask_login import current_user
import data_Structure

logged_user = data_Structure.db.session.query(data_Structure.User).get('Guest')


def get_logged_user():
    return current_user


def write_code_for_search_bar():
    bar = tags.div(tags.form(tags.div(
        tags.select(tags.option('All', value='All', Class="container-fluid panel-body"),

                    tags.option("Boards", value='Boards', Class="container-fluid panel-body"),
                    tags.option("Projects", value='Projects', Class="container-fluid panel-body"),
                    tags.option("Devices", value='Devices', Class="container-fluid panel-body"),
                    Class="form-control selectpicker",
                    style="margin: auto data-width: auto", name="Selector"),

        tags.input(Type="text", Class="form-control ", placeholder="Search", name="search_field"),

        # tags.div(
        tags.button(tags.i(Class="glyphicon glyphicon-search", style="color:#009999"),
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
    if current_user.username is 'Guest':
        return ownNavRenderer.ExtendedNavbar(
            title=View(tags.a(tags.img(src='/static/staticPictures/logo.png', width=200), Class="navbar-left", href=url_for('start')), 'start'),
            items=(View('Start', 'start'),
                    Subgroup('Label',
                            View('Print Label', 'show_new_label')),
                    Subgroup('Board',
                            View('New Board', 'add__board')),
                    Subgroup('Project',
                            View('All Projects', 'show_project_all')),
                   search_bar
                   ),

            right_items=(
                Text(tags.a('gitlab', href='http://git.sdi.site/sdi/platos',  target="_blank")),
                Text(tags.span(Class="glyphicon glyphicon-user", style="margin-right: -20px; color:#009999")),
                Subgroup('Hello Guest!',
                         View(
                             tags.div(tags.span(Class="glyphicon glyphicon-log-in", style="margin-right: 5%"), "Login"),
                             'login',
                             next=request.path))
            )

        )
    else:
        return ownNavRenderer.ExtendedNavbar(
            title=View(tags.a(tags.img(src='/static/staticPictures/logo.png', width=200), Class="navbar-left"), 'start'),
            items=(View('Start', 'start'),
                    Subgroup('Label',
                            View('Print Label', 'show_new_label')),
                    Subgroup('Board',
                            View('New Board', 'add__board')),
                    Subgroup('Project',
                            View('All Projects', 'show_project_all'),
                            View('New Project', 'add_project')),
                    Subgroup('Device', 
                            View('New Device', 'add_device')),
                    search_bar

                   ),
            right_items=(
                Text(tags.a('gitlab', href='http://git.sdi.site/sdi/platos',  target="_blank")),
                Text(tags.span(Class="glyphicon glyphicon-user", style="margin-right: -20px; color:#009999")),
                Subgroup('Hello ' + current_user.username+'!',
                         View(tags.div(tags.span(Class="glyphicon glyphicon-trash", style="margin-right: 5%"),
                                       "Delete User"), 'delete_user'),
                         Separator,
                         View(tags.div(tags.span(Class="glyphicon glyphicon-user", style="margin-right: 5%; color:#009999"),
                                       current_user.username+"`s Profile"), 'my_profile'),
                         View(tags.div(tags.span(Class="glyphicon glyphicon-log-out text-danger", style="margin-right: 5%"),
                                       "Logout"), 'logout'))
            )

        )
