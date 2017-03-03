from wtforms import StringField, validators, HiddenField, SubmitField, PasswordField, Form


class DeleteUser(Form):
    uid = StringField('Please enter the uid of the User', [validators.data_required])

    password = PasswordField('Pleas enter your Password', [validators.required])

    hidden_tag = HiddenField('Blubb')
    submit = SubmitField('Delete!')
