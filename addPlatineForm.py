from wtforms import *


class BoardForm(Form):
    code = StringField('Code', [validators.data_required])
    name = StringField('Project Name', [validators.DataRequired])
    ver = StringField('Version', [validators.data_required])
    history = TextAreaField('Story')
    submit = SubmitField('Create')
    hidden_tag = HiddenField('Blubb')
