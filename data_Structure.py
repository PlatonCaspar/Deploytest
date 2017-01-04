import flask_sqlalchemy
from flask import Flask
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import url_for
import time
from passlib.hash import pbkdf2_sha256
from flask_login import current_user, AnonymousUserMixin

# import flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/Database/data.sql'

db = flask_sqlalchemy.SQLAlchemy(app)
eng = db.create_all()

metadata = sqlalchemy.MetaData(db)


# db.echo = True


# counter = 0;


class Board(db.Model):
    code = db.Column(db.String(500), primary_key=True)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    link = db.Column(db.String(500))
    version = db.Column(db.String(20))
    id = db.Column(db.Integer, primary_key=False)
    dateAdded = db.Column(db.String(10))
    history = db.relationship('History', backref='History', lazy='dynamic')
    addedBy = db.Column(db.String, db.ForeignKey('user.username'))

    def __init__(self, code: str, project_name: str, ver: str):  # , history):
        self.project_name = project_name
        self.code = code
        self.id = id(code)
        self.version = ver
        self.link = str(url_for('show_board_history', g_code=self.code))
        self.dateAdded = time.strftime("%d.%m.%Y %H:%M:%S")
        self.addedBy = User.get_id(current_user)

    def __repr__(self):
        return '<Board %r>' % self.code

    def __hash__(self):
        return hash(self.code)


class User(db.Model):
    username = db.Column(db.String(), primary_key=True)
    password_hashed_and_salted = db.Column(db.String())
    uid = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String())

    boards_Added = db.relationship('Board', lazy='dynamic')

    def __init__(self, username: str, password: str, email: str):
        self.username = username
        self.uid = id(username)
        self.email = email
        self.password_hashed_and_salted = pbkdf2_sha256.hash(password)

    def validate_user(self, username: str, password: str):
        login_user = self.query.filter_by(username=username)
        if pbkdf2_sha256.verify(password, login_user.password_hashed_and_salted):
            return True
        else:
            return False

    def is_authenticated(self):
        if User.query.filter_by(username=self.username).first().scalar() is None:
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymus(self):
        return False

    def get_id(self):
        return self.username.encode("utf-8").decode("utf-8")

    def get(us_name):
        return User.query.filter_by(username=us_name).first()


class History(db.Model):
    board_code = db.Column(db.String(500), db.ForeignKey('board.code'))
    id = db.Column(db.Integer, primary_key=True)
    history = db.Column(db.Text)
    added_by = db.Column(db.Text)
    edited_by = db.Column(db.Text)
    time_and_date = db.Column(db.String(10))
    last_edited = db.Column(db.String(10))

    def __init__(self, history: str, board_code: str):
        self.board_code = board_code
        self.history = history.replace('\n', "<br>")
        self.added_by = User.get_id(current_user)
        self.time_and_date = time.strftime("%d.%m.%Y %H:%M:%S")
        self.last_edited = self.time_and_date
        self.id = id(time.strftime("%d.%m.%Y %H:%M:%S") + board_code)


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'


class Project(db.Model):  # //TODO Implement the Project Class and add relationship to Board
    project_name = db.Column(db.Text, primary_key=True)
    project_description = db.Column(db.Text)
    project_default_image_path = db.Column(db.Text, default='/static/Pictures/logo.jpg')
    project_boards = db.relationship('Board', lazy='dynamic')

    def __init__(self, project_name: str, project_description: str, project_default_image_path: str):
        self.project_name = project_name
        self.project_description = project_description
        self.project_default_image_path = project_default_image_path


eng = db.create_all()
Session = sessionmaker(bind=eng)
session = Session()
