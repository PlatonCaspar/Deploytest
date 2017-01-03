from wtforms import StringField, validators, HiddenField, SubmitField, PasswordField, Form, TextAreaField

class HistoryForm(Form):
    history = TextAreaField()
    send = SubmitField('Add History')
    hidden_tag = HiddenField('Blubb')
    history_id=HiddenField()