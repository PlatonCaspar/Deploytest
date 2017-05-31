import flask_sqlalchemy
from flask import Flask
from os import urandom
from flask import url_for
import time
from passlib.hash import pbkdf2_sha256
from flask_login import current_user, AnonymousUserMixin
import datetime

# import flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/Database/data.sql'

db = flask_sqlalchemy.SQLAlchemy(app)


# metadata = sqlalchemy.MetaData(db)


# db.echo = True


# counter = 0;


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

    def __init__(self, code: str, project_name: str, ver: str):  # , history):
        self.project_name = project_name
        self.code = code
        self.id = id(code)
        self.version = ver
        self.link = str(url_for('show_board_history', g_code=self.code))
        self.dateAdded = time.strftime("%d.%m.%Y %H:%M:%S")
        self.addedBy = current_user

    def __repr__(self):
        return '<Board %r>' % self.code

    def __hash__(self):
        return hash(self.code)


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
            self.uid = id(username)
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
        self.id = id(time.strftime("%d.%m.%Y %H:%M:%S") + board_code + str(current_user.uid) + str(urandom(5)))


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.Text)
    description = db.Column(db.Text)
    belongs_to_history_id = db.Column(db.Integer, db.ForeignKey('history.id'))
    belongs_to_history = db.relationship('History',
                                         backref=db.backref('data_objects_backref', lazy='dynamic', uselist=True))

    def __init__(self, history, file_path: str, description='None'):
        self.belongs_to_history = history
        self.id = id(file_path)
        self.description = description
        self.file_path = file_path


class UserGroup(db.Model):
    user_type = db.Column(db.String)
    id = db.Column(db.Integer, primary_key=True)
    users = db.relationship('User', lazy='dynamic')


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'


class Project(db.Model):  # //TODO Implement the Project Class and add relationship to Board
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



##EXB-List from now on





eng = db.create_all()


# session = flask_sqlalchemy.SQLAlchemy.(bind=eng)
