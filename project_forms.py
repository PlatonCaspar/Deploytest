from wtforms import Form, StringField, SubmitField, StringField, FileField, validators, HiddenField


class AddProjectForm(Form):
    project_name = StringField(validators=[validators.required()])
    project_description = StringField(validators=[validators.required()])
    project_image = FileField('Put a representing Image here!', validators=[validators.optional()])
    GOOOOOOOOOOOOOOOOOOOOOOOOOOO = SubmitField('Create!')
    hidden_tag = HiddenField('Blubb!')
