from wtforms import *


class delBoardForm(Form):
    code = StringField('Code', [validators.data_required])
    hidden_tag = HiddenField('Blubb')
    submit = SubmitField('Delete!')


