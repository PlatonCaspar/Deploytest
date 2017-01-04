from flask_wtf import Form
from flask_wtf.file import FileField
from data_Structure import Project
from wtforms import validators, StringField, HiddenField, SubmitField, TextField, TextAreaField, SelectField


class CKTextAreaWidget(TextField):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


def choices():  #//TODO Select wont load the current elements... thois function is not exexutet when form is loaded...
    choices_var = []
    for choice in Project.query.all():
        choices_var.append([choice.project_name, choice.project_name])
        print('now we execute the coices funcion and get: '+str(choices_var))
    return choices_var


class BoardForm(Form):
    code = StringField('Code', [validators.data_required])
    name = SelectField('Select Project', choices=choices())
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
