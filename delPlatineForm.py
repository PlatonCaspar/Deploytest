from wtforms import *


class delBoardForm(Form):
    code = StringField('ID', [validators.data_required])
    hidden_tag = HiddenField('Blubb')
    submit = SubmitField('Delete!')


