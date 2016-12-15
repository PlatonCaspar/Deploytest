from flask_nav.elements import View, Link
import nav
from dominate import tags
import ownNavRenderer
import flask_wtf
import searchForm

nav.nav.register_element("frontend_top",
                         ownNavRenderer.ExtendedNavbar(
                             title=View(tags.img(src='/static/Pictures/logo.png', width=200), 'start'),
                             items=(View('Data', 'spitOut'),
                                    View('Add Board', 'add__board'),
                                    View('Delete Board', 'del_board')),
                             right_items=(View('ShowAll', 'spitOut'),
                                          View('Add Board', 'add__board'))
                         )
                         )
# flask_nav.elements.View(searchForm.SearchForm(), 'search')))




# Code below worked . Trying out new things because it would get boring.

# flask_nav.elements.View(
#     tags.img(
#         src='/static/Pictures/logo.png',
#         width=200),
#     'start'),
# flask_nav.elements.View(
#     'Data', 'spitOut'),
# flask_nav.elements.View(
#     'Add Board',
#     'add__board'),
# flask_nav.elements.View(
#     'Delete Board',
#     'del_board'))
