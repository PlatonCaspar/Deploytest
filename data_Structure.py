import flask_sqlalchemy
from flask import Flask
from os import urandom
from flask import url_for
from passlib.hash import pbkdf2_sha256
from flask_login import current_user, AnonymousUserMixin

import json
import datetime
import time



# import flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/Database/data.sql'

db = flask_sqlalchemy.SQLAlchemy(app)


class JSONEncodedDict(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."
    
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Board(db.Model):
    code = db.Column(db.String(500), primary_key=True)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project = db.relationship('Project', backref=db.backref('project_boards_backref', lazy='dynamic'))
    link = db.Column(db.String(500))
    version = db.Column(db.String(20))
    id = db.Column(db.Integer, primary_key=False)
    dateAdded = db.Column(db.String(10))
    history = db.relationship('History', backref='History', lazy='dynamic')
    addedBy_id = db.Column(db.String, db.ForeignKey('user.uid'))
    addedBy = db.relationship('User', backref='user_board', uselist=False)
    stat = db.Column(db.Text)
    patch = db.Column(db.Text)
    arguments = db.Column(db.Text)
    


    def __init__(self, code: str, project_name: str, ver: str, stat="init", patch="None"):  # , history):

        self.project_name = project_name
        self.code = code
        self.id = id(code)
        self.version = ver
        self.link = str(url_for('show_board_history', g_code=self.code))
        self.dateAdded = time.strftime("%d.%m.%Y %H:%M:%S")
        self.addedBy = current_user
        self.stat = stat
        self.patch = patch


    def __repr__(self):
        return '<Board %r>' % self.code

    def __hash__(self):
        return hash(self.code)

    def reduce(self):
        arguments = ""
        for arg in self.args():
            arguments = arguments+arg+":"+self.args()[arg]+";"
        return str(self.code)+";"+str(self.project_name)+";owner:"+";patch:"+str(self.patch)+";state:"+str(self.stat)+arguments

    def args(self, to_add=None, delete=False):
        if delete:
            arguments = json.loads(self.arguments)
            deleted = arguments.pop(to_add, None)
            self.arguments=json.dumps(arguments)
            return deleted
            
        if to_add:
            if not self.arguments:
                self.arguments = json.dumps({to_add[0]:to_add[1]})
            else:
                val = json.loads(self.arguments)
                val[to_add[0]]=to_add[1]
                
                self.arguments=json.dumps(val)

        elif self.arguments:
            return json.loads(self.arguments)
        else:
            return {}

    


class User(db.Model):
    username = db.Column(db.String(), primary_key=False)
    password_hashed_and_salted = db.Column(db.String())
    uid = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String())
    user_group = db.Column(db.Integer, db.ForeignKey('user_group.id'))
    boards_Added = db.relationship('Board', lazy='dynamic')
    is_active = db.Column(db.Boolean)
    is_authenticated = db.Column(db.Boolean)

    def __init__(self, username='Guest', password=None, email=None):
        self.username = username
        if password and email:
            self.email = email
            self.password_hashed_and_salted = pbkdf2_sha256.hash(password)

        if db.session.query(User).all() is None:  # First user logged in must be active!
            self.is_active = True

        else:
            self.is_active = True  # for now every User is active

        if username == 'Guest':
            self.is_authenticated = False
        else:
            self.is_authenticated = True

    def validate_user(self, username: str, password: str):
        login_user = self.query.filter_by(username=username)
        if pbkdf2_sha256.verify(password, login_user.password_hashed_and_salted):
            return True
        else:
            return False

    # def is_authenticated(self):
    #     print('okay, is_authenticated is called')
    #     if User.query.filter_by(username=self.username).first().scalar() is None:
    #         return False
    #     elif self.username != 'Guest':
    #         print(self.username)
    #         return True
    #     else:
    #         return False

    def user_is_active(self):
        if self.is_active is not None:
            return self.is_active
        else:
            return False

    def is_anonymus(self):
        if self.username == 'Guest':
            return True
        else:
            return False

    def get_id(self):
        return str(self.uid).encode("utf-8").decode("utf-8")

    # //TODO Here was everything returning the username as primary key
    def get(uid):
        return User.query.filter_by(uid=uid).first()


class History(db.Model):
    board_code = db.Column(db.String(500), db.ForeignKey('board.code'))
    id = db.Column(db.Integer, primary_key=True)
    history = db.Column(db.Text)
    edited_by_id = db.Column(db.Text, db.ForeignKey('user.uid'))
    added_by = db.relationship('User', backref=db.backref('added_by_backref', lazy='dynamic'))

    edited_by = db.relationship('User', backref=db.backref('edited_by_backref', lazy='dynamic'))
    time_and_date = db.Column(db.String(10))
    last_edited = db.Column(db.String(10))
    data_objects = db.relationship('Files',
                                   backref=db.backref('belongs_to_history_backref', lazy='dynamic', uselist=True))



    def __init__(self, history: str, board_code: str):
        self.board_code = board_code
        self.history = history.replace('\n', "<br>")
        if current_user is not None:
            self.added_by = db.session.query(User).get(
                current_user.uid)
        elif current_user is None:
            self.added_by = db.session.query(User).get('Guest')

        self.time_and_date = time.strftime("%d.%m.%Y %H:%M:%S")
        self.last_edited = self.time_and_date
        

    def time_date_datetime(self):
        return time.strptime(self.time_and_date, "%d.%m.%Y %H:%M:%S")

    def link(self):
        return url_for('show_board_history', g_code=self.board_code)+'#comment_id'+str(self.id)

    def reduce(self):
        return self.history.replace(" ", ";")+";"+str(self.added_by.username)+";"+self.edited_by.username

    def short_result(self, search_word, max_length = 30):
        
        start_ind = self.history.index(search_word)
        
        if start_ind > 6:
            start_ind = start_ind-6

        if len(self.history)-start_ind < max_length:
            end_ind = len(self.history)
            return self.history[start_ind:end_ind]
        else:
            end_ind = start_ind+max_length-1
            return self.history[start_ind:end_ind]+"..."
        



class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.Text)
    description = db.Column(db.Text)
    belongs_to_history_id = db.Column(db.Integer, db.ForeignKey('history.id'))
    belongs_to_history = db.relationship('History',
                                         backref=db.backref('data_objects_backref', lazy='dynamic', uselist=True))

    def __init__(self, history, file_path: str, description='None'):
        self.belongs_to_history = history
        self.description = description
        self.file_path = file_path


class UserGroup(db.Model):
    user_type = db.Column(db.String)
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', lazy='dynamic')


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'


class Project(db.Model):
    project_name = db.Column(db.Text, primary_key=True)
    project_description = db.Column(db.Text)
    project_default_image_path = db.Column(db.Text, default=None)
    project_boards = db.relationship('Board', backref=db.backref('project_backref', lazy='dynamic', uselist=True))
    sub_projects = db.relationship('Project', lazy='dynamic', uselist=True)
    sub_projects_id = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project_history = db.relationship('History',
                                      backref=db.backref('project_history_backref', lazy='dynamic', uselist=True))
    project_history_id = db.Column(db.Integer, db.ForeignKey('history.id'))


    def __init__(self, project_name: str, project_description: str, project_default_image_path: str):
        self.project_name = project_name
        self.project_description = project_description
        self.project_default_image_path = project_default_image_path

    def reduce(self):
        return str(self.project_name)+";"+str(self.project_description.replace(" ",";"))


##EXB-List from now on

eng = db.create_all()


# session = flask_sqlalchemy.SQLAlchemy.(bind=eng)
