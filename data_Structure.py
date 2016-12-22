import flask_sqlalchemy
from Platinen import app
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from flask import url_for
import time
from passlib.hash import pbkdf2_sha256

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/Database/data.sql'

db = flask_sqlalchemy.SQLAlchemy(app)
eng = db.create_all()

metadata = sqlalchemy.MetaData(db)


# db.echo = True


# counter = 0;


class Board(db.Model):
    code = db.Column(db.String(500), primary_key=True)
    project_name = db.Column(db.String(80))
    link = db.Column(db.String(500))
    version = db.Column(db.String(20))
    id = db.Column(db.Integer, primary_key=False)
    history = db.Column(db.Text)
    dateAdded = db.Column(db.String(10))

    def __init__(self, code: str, project_name: str, ver: str, history):
        self.project_name = project_name
        self.code = code
        self.id = id(code)
        self.version = ver
        self.link = str(url_for('show_board_history', g_code=self.code))
        self.history = history
        self.dateAdded = time.strftime("%d.%m.%Y %H:%M:%S")
        print(self.dateAdded)

    def __repr__(self):
        return '<Board %r>' % self.code

    def __hash__(self):
        return hash(self.code)


class User(db.Model):
    username = db.Column(db.String(), primary_key=True)
    password_hashed_and_salted = db.Column(db.String())
    uid = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String())

    def __init__(self, username: str, password: str, email: str):
        self.username = username
        self.uid = id(username)
        self.email = email
        self.password_hashed_and_salted = pbkdf2_sha256.hash(password)

    def validate_user(self, username: str, password: str):
        login_user = self.query.filter_by(username=username)
        if login_user.password_hashed_and_salted == pbkdf2_sha256.hash(password):
            return True
        else:
            return False


eng = db.create_all()
Session = sessionmaker(bind=eng)
session = Session()
