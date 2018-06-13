from flask_wtf import FlaskForm as Form 
from flask_wtf.file import FileField
from data_Structure import Project
from wtforms import validators, StringField, HiddenField, SubmitField, StringField, TextAreaField, SelectField


class CKTextAreaWidget(StringField):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


def load_choices():
    choices = []
    for choice in Project.query.all():
        choices.append([choice.project_name, choice.project_name])
    return choices


class BoardForm(Form):
    code = StringField('Code', [validators.data_required])
    name = SelectField('Select Project')
    ver = StringField('Version', [validators.data_required])
    submit = SubmitField('Create')
    hidden_tag = HiddenField('Blubb')


class ChangeBoard(Form):
    image = FileField('put an Image of the Board here!')
    history = StringField('Edit History')
    submit = SubmitField('Edit!')
    hidden_tag = HiddenField('Blubb')


class SelectChangeBoard(Form):
    edit = SubmitField('Edit!')
    add = SubmitField('Add a beautiful Story!')
    hidden_tag = HiddenField('Blubb')
