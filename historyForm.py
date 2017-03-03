from wtforms import validators, HiddenField, SubmitField, Form, TextAreaField, FileField


class HistoryForm(Form):
    history = TextAreaField('Comment', validators=[validators.data_required])
    send = SubmitField('Add Comment')
    hidden_tag = HiddenField('Blubb')
    history_id = HiddenField()


class EditHistoryForm(Form):
    history = TextAreaField('Comment', validators=[validators.data_required])
    send_edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    hidden_tag = HiddenField('Blubb')
    history_id = HiddenField('hidden')
