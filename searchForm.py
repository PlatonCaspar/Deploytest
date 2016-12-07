from wtforms import *


class SearchForm(Form):
    search_value = StringField('Search everywhere!! Wuhuuuu', [validators.data_required])
    submit = SubmitField('Go!')
    hidden_tag = HiddenField('Blubb')
    action = None


