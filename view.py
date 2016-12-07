import flask_nav.elements
import nav

nav.nav.register_element("frontend_top", flask_nav.elements.Navbar(
    flask_nav.elements.View('Start', 'start'),
    flask_nav.elements.View('data', 'spitOut'),
    flask_nav.elements.View('Add Board', 'add__board'),
    flask_nav.elements.View('Delete Board', 'del_board')))



