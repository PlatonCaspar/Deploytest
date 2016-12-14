#from flask_sqlalchemy import *
import flask_sqlalchemy
from Platinen import app
import sqlalchemy
#from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask import url_for

# from contextlib import closing
# import sqlite3


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/Database/data.sql'

db = flask_sqlalchemy.SQLAlchemy(app)


metadata = sqlalchemy.MetaData(db)
#db.echo = True


# counter = 0;


class Board(db.Model):
    code = db.Column(db.String(500), primary_key=True)
    project_name = db.Column(db.String(80))
    link = db.Column(db.String(500))
    version = db.Column(db.String(20))
    id = db.Column(db.Integer, primary_key=False)
    history = db.Column(db.Text)

    # = db.Column(db.Text(120))

    def __init__(self, code: str, project_name: str, ver: str, history):
        self.project_name = project_name
        self.code = code
        self.id = id(code)
        self.version = ver
        self.link = str(url_for('show_board_history', g_code=self.code))
        self.history = history

    def __repr__(self):
        return '<Board %r>' % self.code

    def __hash__(self):
        return hash(self.code)


eng = db.create_all()
Session = sessionmaker(bind=eng)
session = Session()
