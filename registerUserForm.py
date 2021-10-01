from wtforms import StringField, validators, HiddenField, SubmitField, PasswordField, Form, FormField


class RegisterUser(Form):
    username = StringField('Username', [validators.data_required()])
    email_adress = StringField('E-Mail', [validators.data_required()])
    password = PasswordField('Password', [validators.required()])
    password_again = PasswordField('Confirm Password', [validators.required()])


class LoginUser(Form):
    username = StringField("Username:", validators=[validators.data_required()])

    password = PasswordField("Password:", validators=[validators.required()])

    hidden_tag = HiddenField('Blubb')
    # submit = SubmitField('Login')
