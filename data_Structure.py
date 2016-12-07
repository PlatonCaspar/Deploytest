from flask_sqlalchemy import *
from Platinen import app
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from flask import url_for
from wtforms import validators

# from contextlib import closing
# import sqlite3


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/Database/data.sql'

db = SQLAlchemy(app)

metadata = MetaData(db)
db.echo = True


# counter = 0;


class Board(db.Model):
    code = db.Column(db.String(500), primary_key=True)
    project_name = db.Column(db.String(80))
    link = db.column(db.String(500))
    id = db.Column(db.Integer, primary_key= False)
    history = db.column(db.Text)


    # = db.Column(db.Text(120))

    def __init__(self, code: str, project_name: str):
        self.project_name = project_name
        self.code = code
        self.id = id(code)





    def __repr__(self):
        return '<User %r>' % self.project_name

    def __hash__(self):
        return hash(self.name)


eng = db.create_all()
Session = sessionmaker(bind=eng)
session = Session()
