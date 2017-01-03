from wtforms import StringField, validators, HiddenField, SubmitField, PasswordField, Form


class DeleteUser(Form):
    username = StringField('Please enter a Username', [validators.data_required])

    password = PasswordField('Pleas enter your Password', [validators.required])

    hidden_tag = HiddenField('Blubb')
    submit = SubmitField('Delete!')
