from wtforms import validators, HiddenField, SubmitField, Form, TextAreaField, IntegerField
from flask_wtf import form


class HistoryForm(Form):
    history = TextAreaField(validators=[validators.data_required])
    send = SubmitField('Add History')
    hidden_tag = HiddenField('Blubb')
    history_id = HiddenField()


class EditHistoryForm(Form):
    history = TextAreaField(validators=[validators.data_required])
    send_edit = SubmitField('Add History')
    hidden_tag = HiddenField('Blubb')
    history_id = HiddenField('hidden')
