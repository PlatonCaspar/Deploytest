from wtforms import validators, HiddenField, SubmitField, Form, TextAreaField, FileField


class HistoryForm(Form):
    history = TextAreaField(validators=[validators.data_required])
    send = SubmitField('Add History')
    hidden_tag = HiddenField('Blubb')
    history_id = HiddenField()


class EditHistoryForm(Form):
    history = TextAreaField(validators=[validators.data_required])
    send_edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    hidden_tag = HiddenField('Blubb')
    history_id = HiddenField('hidden')
