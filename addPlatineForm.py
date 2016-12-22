from flask_wtf import Form
from flask_wysiwyg.wysiwyg import WysiwygField

from wtforms import validators, StringField, HiddenField, SubmitField


class BoardForm(Form):
    code = StringField('Code', [validators.data_required])
    name = StringField('Project Name', [validators.DataRequired])
    ver = StringField('Version', [validators.data_required])
    history = StringField('History', validators=[validators.required],
                          body=WysiwygField('editor', validators=[validators.required]))
    submit = SubmitField('Create')
    hidden_tag = HiddenField('Blubb')
