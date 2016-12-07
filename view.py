import flask_nav.elements
from flask_bootstrap import url_for
import nav
from dominate import tags
import flask_wtf
import searchForm

nav.nav.register_element("frontend_top", flask_nav.elements.Navbar(
    flask_nav.elements.View(tags.img(src='/static/Pictures/logo.png', width=200), 'start'),
    flask_nav.elements.View('data', 'spitOut'),
    flask_nav.elements.View('Add Board', 'add__board'),
    flask_nav.elements.View('Delete Board', 'del_board')))
# flask_nav.elements.View(searchForm.SearchForm(), 'search')))
