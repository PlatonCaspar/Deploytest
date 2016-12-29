from wtforms import StringField, validators, HiddenField, SubmitField, PasswordField, Form, FormField


class RegisterUser(Form):
    username = StringField('Please enter a Username', [validators.data_required])
    email_adress = StringField('Please enter your E-Mail', [validators.data_required, validators.email])
    password = PasswordField('Pleas enter your Password', [validators.required])
    password_again = PasswordField('Please repeat your Password', [validators.required])
    hidden_tag = HiddenField('Blubb')
    submit = SubmitField('Register!')