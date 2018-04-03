import flask_sqlalchemy
from flask import Flask
from werkzeug.utils import secure_filename
from os import urandom, path, remove
from flask import url_for, flash
from passlib.hash import pbkdf2_sha256
from flask_login import current_user, AnonymousUserMixin
from sqlalchemy import MetaData
import json
import datetime
import time
import markdown
import re


RELATIVE_PICTURE_PATH = 'static/Pictures'
UPLOAD_FOLDER = path.join(path.dirname(path.abspath(__file__)),
                             RELATIVE_PICTURE_PATH)


app = Flask(__name__)
naming_convention = {
    "fk": "fk_%(table_name)s_(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s" 
}
metadata = MetaData(naming_convention=naming_convention)
SQLALCHEMY_DATABASE_URI = 'sqlite:///static/Database/data.sql'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
db = flask_sqlalchemy.SQLAlchemy(app, metadata=metadata)


# needed for many to many relationship bewteen patch and board
patch_board = db.Table('patch_board',
                       db.Column('board_code', db.String(500), db.ForeignKey('board.code', primary_key=True)),
                       db.Column('patch_id', db.Integer, db.ForeignKey('patch.patch_id'))
                       )


class Board(db.Model):
    code = db.Column(db.String(500), primary_key=True)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project = db.relationship('Project', backref=db.backref('project_boards_backref', lazy='dynamic'))
    #link = db.Column(db.String(500))
    version = db.Column(db.String(20))
    id = db.Column(db.Integer, primary_key=False)
    dateAdded = db.Column(db.String(10))
    history = db.relationship('History', backref='History', lazy='dynamic')
    addedBy_id = db.Column(db.String, db.ForeignKey('user.uid'))
    addedBy = db.relationship('User', backref='user_board', uselist=False)
    stat = db.Column(db.Text)
    patch = db.Column(db.Text)
    arguments = db.Column(db.Text)
    patches = db.relationship('Patch', secondary=patch_board)

    def __init__(self, code: str, project_name: str, ver: str, stat="init", patch="None"):  # , history):

        self.project_name = project_name
        self.code = code
        self.id = id(code)
        self.version = ver
        # self.link = str(url_for('show_board_history', g_code=self.code))
        self.dateAdded = time.strftime("%d.%m.%Y %H:%M:%S")
        self.addedBy = current_user
        self.stat = stat
        self.patch = patch

    def __repr__(self):
        return '<Board %r>' % self.code

    def reduce(self):
        arguments = ""
        for arg in self.args():
            arguments = arguments+arg+":"+self.args()[arg]+";"
        return str(self.code)+";"+str(self.project_name)+";version:"+str(self.version)+";patch:"+str(self.patch_numbers())+";state:"+str(self.stat)+arguments

    def args(self, to_add=None, delete=False):
        if delete:
            arguments = json.loads(self.arguments)
            deleted = arguments.pop(to_add, None)
            self.arguments = json.dumps(arguments)
            return deleted

        if to_add:
            if not self.arguments:
                self.arguments = json.dumps({to_add[0]: to_add[1]})
            else:
                val = json.loads(self.arguments)
                val[to_add[0]] = to_add[1]

                self.arguments = json.dumps(val)

        elif self.arguments:
            return json.loads(self.arguments)
        else:
            return {}

    def link(self):
        return url_for('show_board_history', g_code=self.code)

    def patch_numbers(self):
        out = ""
        for patch in self.patches:
            out += ("""{}""".format(patch.patch_number)+",")

        return out.strip(",")


class User(db.Model):
    username = db.Column(db.String(), primary_key=False)
    password_hashed_and_salted = db.Column(db.String())
    uid = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String())
    user_group = db.Column(db.Integer, db.ForeignKey('user_group.id'))
    boards_Added = db.relationship('Board', lazy='dynamic')
    is_active = db.Column(db.Boolean)
    is_authenticated = db.Column(db.Boolean)
    avatar_path = db.Column(db.Text)
    messages = db.relationship("Message", uselist=True)

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

    def avatar(self, file=None):
        if file:
            # save file Here
            datatype = secure_filename(file.filename).split(".")[1]
            # TODO check if image
            new_name = """avatar_{0}.{1}""".format(self.username, datatype)
            file.save(path.join(UPLOAD_FOLDER, new_name))
            self.avatar_path = path.join(RELATIVE_PICTURE_PATH, new_name)
            db.session.commit()
        else:

            if self.avatar_path:

                return "/"+self.avatar_path

            else:

                return "/static/staticPictures/general_user.png"

    def registered_users(self):
        names = list()
        for uname in db.session.query(User.username).all():
            names.append(uname[0])
        return names

    def message(self, message, link):
        try:
            msg = Message(self, message, link, current_user)
        except:
            print("could not create the message")
        db.session.add(msg)
        self.messages.append(msg)
        db.session.commit()

    def get_messages(self, all=False):
        #print(list(filter(lambda msg: msg.read is False, self.messages)))
        return list(filter(lambda msg: msg.read is False, self.messages))
    
    def get_messages_count(self):
            msg = self.get_messages()
            if msg:
                return len(self.get_messages())
            else:
                return 0


class History(db.Model):
    board_code = db.Column(db.String(500), db.ForeignKey('board.code'))
    id = db.Column(db.Integer, primary_key=True)
    history = db.Column(db.Text)
    edited_by_id = db.Column(db.Text, db.ForeignKey('user.uid'))
    added_by = db.relationship('User', backref=db.backref('added_by_backref', 
                                                          lazy='dynamic'))

    edited_by = db.relationship('User', backref=db.backref('edited_by_backref',
                                                           lazy='dynamic'))
    time_and_date = db.Column(db.String(10))
    last_edited = db.Column(db.String(10))
    data_objects = db.relationship('Files',
                                   backref=db.backref('belongs_to_history_backref', 
                                                      lazy='dynamic', uselist=True))
    parent_id = db.Column(db.Integer, db.ForeignKey('history.id'))
    answers = db.relationship('History', uselist=True)

    def __init__(self, history: str, board_code=None, parent_id=None):
        self.board_code = board_code
        self.history = history
        if parent_id:
            self.parent_id = parent_id
        if current_user is not None:
            self.added_by = current_user
        elif current_user is None:
            flash("Please log in to make a comment", 'info')
            return redirect(url_for('login', next=request.referrer))
        self.time_and_date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.last_edited = self.time_and_date
        self.check_mentions()

    def add_answer(self, text: str):
        answer = History(text, parent_id=self.id)
        db.session.add(answer)
        self.answers.append(answer)
        db.session.commit()


    def time_date_datetime(self):
        return datetime.datetime.strptime(self.time_and_date, 
                                          "%d.%m.%Y %H:%M:%S")

    def link(self):
        if self.board_code:
            return url_for('show_board_history', g_code=self.board_code)+'#comment_id'+str(self.id)
        else:
            return url_for('show_board_history', g_code=self.parent().board_code)+'#comment_id'+str(self.id)

    def reduce(self):
        return self.history.replace(" ", ";")+";"+str(self.added_by.username)+";"+self.edited_by.username

    def parent(self):
        if self.parent_id:
            return History.query.get(self.parent_id)
        else:
            return None

    def short_result(self, search_word, max_length=30):
        # print(self.history+ " "+search_word)
        start_ind = 0
        try:
            start_ind = self.history.lower().index(search_word.lower())
        except:
            flash('some error occured in \"short_result\"', "danger")
            #print(search_word.lower()+" "+self.history.lower())
        if start_ind > 6:
            start_ind = start_ind-6

        if len(self.history)-start_ind < max_length:
            end_ind = len(self.history)
            return self.history[start_ind:end_ind].replace("<br>", " ")
        else:
            end_ind = start_ind+max_length-1
            return self.history[start_ind:end_ind].replace("<br>", " ")+"..."

    def md_history(self):
        return markdown.markdown(self.history.replace('<br>', '\n'))

    def check_mentions(self):
        mentions = re.findall("(?<=@)\w+", self.history)
        users = []
        mentions = set(mentions)
        for name in mentions:
            user = User.query.filter_by(username=name).first()
            if user:
                user.message("""{} mentioned you""".format(current_user.username),
                             self.link())
            else:
                flash("You mentioned a User that does not exist! ({})".format(name), "info")


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', uselist=False)
    user_name = db.Column(db.String(), db.ForeignKey('user.username'))
    read = db.Column(db.Boolean)
    message = db.Column(db.Text)
    link = db.Column(db.Text)
    created_by = db.Column(db.Text)

    def __init__(self, user, message, link, created_by):
        self.user = user
        self.message = message
        self.read = False
        self.link = link

    def set_read(self, val=True):
        self.read = val

    def c_user(self):
        return User.query.filter_by(username=self.created_by) or self.created_by

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
    project_patches = db.relationship("Patch", lazy='dynamic', uselist=True)

    def __init__(self, project_name: str,
                 project_description: str, project_default_image_path):
        self.project_name = project_name
        self.project_description = project_description
        self.project_default_image_path = project_default_image_path

    def reduce(self):
        return str(self.project_name)+";"+str(self.project_description.replace(" ", ";"))


class Patch(db.Model):
    patch_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    patch_number = db.Column(db.Integer)
    project = db.relationship('Project', uselist=False)
    project_id = db.Column(db.Text, db.ForeignKey('project.project_name'))
    boards = db.relationship("Board", secondary=patch_board, uselist=True)
    files = db.relationship("PatchDocument", backref='patch', uselist=True)

    def __init__(self, project):
        self.project = project
        self.patch_number = len(Patch.query.filter_by(project_id=project.project_name).all()) + 1
        
    def md_description(self):
        return markdown.markdown(self.description)

    def addFile(self, doc):
        self.files.append(doc)


class PatchDocument(db.Model):
    patch_document_id = db.Column(db.Integer, primary_key=True)
    patch_document_path = db.Column(db.Text)
    patch_document_description = db.Column(db.Text)
    patch_document_patch_id = db.Column(db.Integer, db.ForeignKey('patch.patch_id'))

    def __init__(self, path, descr=""):
        self.patch_document_path = path
        self.patch_document_description = descr

    def name(self):
        only_name = self.patch_document_path.replace('/','\\').split('\\')
        if len(only_name) > 1:
            return only_name[len(only_name)-1]+" "+str(self.patch_document_description)
        else:
            return only_name[0]+" "+str(self.patch_document_description)

    def delete(self):
        db.session.delete(self)
        print(path.join(UPLOAD_FOLDER, self.name()))
        remove(path.join(UPLOAD_FOLDER, self.name()))
        db.session.commit()


class DeviceDocument(db.Model):
    device_document_id = db.Column(db.Integer, primary_key=True)
    device_document_path = db.Column(db.Text)
    device_document_description = db.Column(db.Text)
    device_document_device = db.relationship('Device', backref='device_document_device_backref', uselist=False)
    device_document_device_id = db.Column(db.Integer, db.ForeignKey('device.device_id'))

    def __init__(self, device_document_path, device_document_device, device_document_description=""):
        self.device_document_path = device_document_path
        self.device_document_device = device_document_device
        self.device_document_description = device_document_description

    def name(self):
        only_name = self.device_document_path.replace('/','\\').split('\\')
        if len(only_name) > 1:
            return only_name[len(only_name)-1]+" "+str(self.device_document_description)
        else:
            return only_name[0]+" "+str(self.device_document_description)


class Device(db.Model):
    device_name = db.Column(db.Text)
    device_brand = db.Column(db.Text)
    device_id = db.Column(db.Integer, primary_key=True)
    device_description = db.Column(db.Text)
    device_arguments = db.Column(db.Text)
    device_documents = db.relationship('DeviceDocument', backref='device_device_documents_backref', lazy=True, uselist=True)
    #device_documents_id = db.Column(db.Integer, db.ForeignKey('deviceDocument.device_document_id'))

    def __init__(self, device_name, device_brand, device_description=None):
        self.device_name = device_name
        self.device_brand = device_brand
        if device_description:
            self.device_description = device_description
    
    def link(self):
    
        return url_for('show_device', device_id=self.device_id)

    def reduce(self):
        arg = ""
        for a in self.args():
            arg = arg+a+":"+self.args()[a]+";"
        return "Device;"+arg+";"+self.device_name+";"+self.device_brand+";"

    def args(self, to_add=None, delete=False):
        if delete:
            arguments = json.loads(self.device_arguments)
            deleted = arguments.pop(to_add, None)
            self.device_arguments = json.dumps(arguments)
            return deleted

        if to_add:
            if not self.device_arguments:
                self.device_arguments = json.dumps({to_add[0]: to_add[1]})
            else:
                val = json.loads(self.device_arguments)
                val[to_add[0]] = to_add[1]
                
                self.device_arguments = json.dumps(val)

        elif self.device_arguments:
            return json.loads(self.device_arguments)
        else:
            return {}


# EXB-List from now on


def create_database(test=False):
    if not test:
        eng = db.create_all()
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///static/Database/test_data.sql'
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    


# session = db.sessionmaker(bind=eng)
