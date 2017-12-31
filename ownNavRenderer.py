from dominate import tags
from flask_nav.elements import NavigationItem, RawTag
from flask_bootstrap.nav import BootstrapRenderer, sha1


class BetterRawTag(RawTag, NavigationItem):

    @property
    def visit_BetterRawTag(self): return False

    def visit(self): return False

    @property
    def active(self):
        return False

    def __getattr__(self, item):
        print('I want to get the attr')
        return self.visit_BetterRawTag()

# setattr(BetterRawTag, 'visit_BetterRawTag', 'return False')


class ExtendedNavbar(NavigationItem):
    def __init__(self, title, root_class='navbar navbar-default', items=[], right_items=[]):
        self.title = title
        self.root_class = root_class
        self.items = items
        self.right_items = right_items


class own_nav_renderer(BootstrapRenderer):
    def visit_ExtendedNavbar(self, node):
        # create a navbar id that is somewhat fixed, but do not leak any
        # information about memory contents to the outside
        node_id = self.id or sha1(str(id(node)).encode()).hexdigest()

        root = tags.nav() if self.html5 else tags.div(role='navigation')
        root['class'] = node.root_class
        root['style'] = 'border-bottom-color: #009999'
        cont = root.add(tags.div(_class='container-fluid'))

        # collapse button
        header = cont.add(tags.div(_class='navbar-header'))
        btn = header.add(tags.button())
        btn['type'] = 'button'
        btn['class'] = 'navbar-toggle collapsed'
        btn['data-toggle'] = 'collapse'
        btn['data-target'] = '#' + node_id
        btn['aria-expanded'] = 'false'
        btn['aria-controls'] = 'navbar'

        btn.add(tags.span('Toggle navigation', _class='sr-only'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))

        # title may also have a 'get_url()' method, in which case we render
        # a brand-link
        if node.title is not None:
            if hasattr(node.title, 'get_url'):
                header.add(tags.a(node.title.text, _class='navbar-brand',
                                  href=node.title.get_url()))
            else:
                header.add(tags.span(node.title, _class='navbar-brand'))

        bar = cont.add(tags.div(
            _class='navbar-collapse collapse',
            id=node_id,
        ))
        bar_list = bar.add(tags.ul(_class='nav navbar-nav'))
        for item in node.items:

            if item.__class__.__name__ is not 'RawTag':
                bar_list.add(self.visit(item))
            elif item.__class__.__name__ is 'RawTag':
                bar_list.add(item.content)

        if node.right_items:
            right_bar_list = bar.add(tags.ul(_class='nav navbar-nav navbar-right'))
            for item in node.right_items:
                if item.__class__.__name__ is not 'RawTag':
                    right_bar_list.add(self.visit(item))
                elif item.__class__.__name__ is 'RawTag':
                    right_bar_list.add(item.content)

        return root
