from wtforms import Form, StringField, SubmitField, TextField, FileField, validators, HiddenField


class AddProjectForm(Form):
    project_name = TextField(validators=[validators.required])
    project_description = TextField(validators=[validators.required])
    project_image = FileField('Put a representing Image here!', validators=[validators.optional])
    GOOOOOOOOOOOOOOOOOOOOOOOOOOO = SubmitField('Send!')
    hidden_tag = HiddenField('Blubb!')
