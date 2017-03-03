from wtforms import Form, StringField, validators, SubmitField, HiddenField


class SearchForm(Form):
    search_value = StringField('Search Content:')
    submit = SubmitField('Go!')
    hidden_tag = HiddenField('Blubb')
