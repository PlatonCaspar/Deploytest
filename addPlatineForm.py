from flask_wtf import Form
from flask_wtf.file import FileField
# from werkzeug.utils import secure_filename
from flask_wysiwyg.wysiwyg import WysiwygField

from wtforms import validators, StringField, HiddenField, SubmitField, TextField, TextAreaField


class CKTextAreaWidget(TextField):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()


class BoardForm(Form):
    code = StringField('Code', [validators.data_required])
    name = StringField('Project Name', [validators.DataRequired])
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
