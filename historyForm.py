from wtforms import  validators, HiddenField, SubmitField, Form, TextAreaField


class HistoryForm(Form):
    history = TextAreaField(validators=[validators.data_required])
    send = SubmitField('Add History')
    hidden_tag = HiddenField('Blubb')
    history_id = HiddenField()

class EditHistoryForm(Form):
    history = TextAreaField(validators=[validators.data_required])
    send = SubmitField('Add History')
    hidden_tag = HiddenField('Blubb')
    history_id = HiddenField()