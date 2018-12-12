import flask_sqlalchemy
from flask import Flask, url_for
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
import collections
import requests

import helper
import board_labels

RELATIVE_PICTURE_PATH = 'static/Pictures'
UPLOAD_FOLDER = path.join(path.dirname(path.abspath(__file__)),
                          RELATIVE_PICTURE_PATH)
RESERVATION = 0
BOOKING = 1
ORDER = 2


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
            return collections.OrderedDict(sorted(json.loads(self.arguments).items()))
        else:
            return {}

    def link(self):
        return url_for('show_board_history', g_code=self.code)

    def patch_numbers(self):
        out = ""
        for patch in self.patches:
            out += ("""{}""".format(patch.patch_number)+",")
        return out.strip(",")

    def print_label(self, _flash=True):
        label_file_cont = board_labels.generate_label(code_number=self.code, code_url=url_for('show_board_history', g_code=self.code, _external=True))
        board_labels.print_label("labelprinter01.internal.sdi.tools", label_file_cont, _flash=_flash)
        

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
    division = db.Column(db.Text)

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
        return list(filter(lambda msg: msg.read is False, self.messages))
    
    def get_messages_count(self):
            msg = self.get_messages()
            if msg:
                return len(self.get_messages())
            else:
                return 0

    def project_related_processes(self):
        return sorted(list(filter(lambda p: p.project is not None, self.processes)),key=lambda p: p.id, reverse=True)


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
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))

    def __init__(self, history: str, board_code=None, parent_id=None, part=None):
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
        if part:
            part.comments.append(self)
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
        elif self.part:
            return self.part.link()+'#comment_id'+str(self.id)        
        else:
            if not self.parent():
                return None
            return self.parent().link()+'#comment_id'+str(self.id)

    def reduce(self):
        return self.history.replace(" ", ";")+";"+str(self.added_by.username)+";"+self.edited_by.username

    def parent(self):
        if self.parent_id:
            return History.query.get(self.parent_id)
        else:
            return None

    def short_result(self, search_word, max_length=30):
        start_ind = 0
        try:
            start_ind = self.history.lower().index(search_word.lower())
        except ValueError:
            pass
        except Exception as e:
            flash('some error occured in \"short_result\"\n{}'.format(e), "danger")
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

    def delete(self):
        for obj in self.data_objects:
            image_to_delete = obj
            remove(path.join(UPLOAD_FOLDER, image_to_delete.file_path))
            db.session.delete(image_to_delete)
            db.session.commit()
        for answer in self.answers:
            answer.delete()
        db.session.delete(self)
        db.session.commit()


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
    
    def link(self):
        return url_for("show_project", project_name=self.project_name)

    def get_board_abbr(self):
        try:
            abbr = helper.parse_board_abbr(self.project_boards[0].code)
        except Exception as e:
            raise Exception("An Error occured in //Project.get_board_abbr()// while trying to parse the project abbr.\n{}".format(e))
        return abbr

    def create_boards(self, number, version=0):
        try:
            abbr = self.get_board_abbr()
        except Exception as e:
            raise Exception("An Error occured in //Project.get_board_abbr()_0_//\n{}".format(e))
        try:
            nrs = []
            for b in self.project_boards:
                nrs.append(int(b.code[len(abbr):]))
        except Exception as e:
            raise Exception("Failed to get existing board numbers //Project.create_boards()//\n{}".format(e))
        last = helper.array_max_val(nrs)
        if number is 1:
            nr = last+1
            board = Board(
                "{abbr}{nr}".format(abbr=abbr, nr=nr),
                self.project_name,
                str(version))
            board.print_label(_flash=False)
            db.session.add(board)
        else:    
            text = None
            for n in range(1, number+1):
                nr = last+n
                board = Board(
                    "{abbr}{nr}".format(abbr=abbr, nr=nr),
                    self.project_name,
                    str(version))
                text = board_labels.generate_label(code_number=board.code, code_url=url_for('show_board_history', g_code=board.code, _external=True), text=text)        
                db.session.add(board)
            board_labels.print_label("labelprinter01.internal.sdi.tools", text, _flash=False)   
        db.session.commit()
        flash("{} Boards were successfully added.".format(number), "success")


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
        # print(path.join(UPLOAD_FOLDER, self.name()))
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
    device_documents = db.relationship('DeviceDocument',
                                       backref='device_device_documents_backref',
                                       lazy=True, uselist=True)

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

    def print_label(self):
        if app.config["TESTING"]:
            return
        code_url = url_for('show_device', device_id=self.device_id, _external=True)
        data = dict(
            QR=code_url,
            HEAD="Device {}".format(self.device_id),
            SUBHEAD="{mf}::{}".format(self.device_brand, self.device_name)
        )
        r = requests.post("http://10.11.20.5/print/label/38mm/", data=json.dumps(data))
        if "OK" in r.text:
            flash("Check labelprinter for your label!", "success")
        if "OK" in r.text:
            flash("Check labelprinter for your label!", "success")
        if "FAIL" in r.text:
            flash("Something may be wrong, check labelprinter for label. You may try again!\n{}".format(r.text), "warning")


# Components from now on
class PartType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    json_attributes = db.Column(db.Text)
    parts = db.relationship('Part', backref="part_type", lazy='dynamic',
                            uselist=True)

    def __init__(self, name, description=None):
        self.name = name
        self.json_attributes = json.dumps([])
        self.description = ""

    def args(self, attr=None, delete=False):
        attributes = json.loads(self.json_attributes)
        if not attr:
            return attributes
        elif attr and not delete:
            if attr in attributes:
                flash("key is already present. Nothing was changed", "warning")
                return attributes
            attributes.append(attr)
            if attr in attributes:
                flash("key {} was added".format(attr), "success")
        elif attr and delete:
            if attr in attributes:
                attributes.pop(attributes.index(attr))
                flash("key was removed", "success")
        self.json_attributes = json.dumps(attributes)
        db.session.commit()
        return attributes


class Part(db.Model):
    ids = db.Column(db.Integer, primary_key=True)
    part_type_id = db.Column(db.Integer, db.ForeignKey('part_type.id'))
    exb_number = db.Column(db.Integer)
    json_attributes = db.Column(db.Text)
    out = db.Column(db.Boolean)
    recommended = db.Column(db.Integer)
    orders = db.relationship('Order',
                             backref='part',
                             lazy='dynamic',
                             uselist=True)
    reservations = db.relationship('Reservation',
                                   backref='part',
                                   lazy='dynamic',
                                   uselist=True)
    comments = db.relationship('History', backref='part', lazy='dynamic',
                               uselist=True)
    containers = db.relationship('Container', backref='part', uselist=True)

    def __init__(self, part_type_id: int):
        self.json_attributes = json.dumps({})
        PartType.query.get(part_type_id).parts.append(self)
        self.recommended = 0
        self.exb_number = 0
    
    def exb(self, exb_nr=None, number_only=False, new=False):
        if exb_nr:
            if "EXB" in exb_nr:
                exb_nr = exb_nr.strip("EXB")
            try:
                if len(exb_nr) != 6:
                    raise Exception("The EXB Number was not of the correct format. It must consist of 6 digits!")
                self.exb_number = int(exb_nr)
                db.session.commit()
            except Exception as e:
                flash("an error occured in //part.exb()//\n{}".format(e), "danger")
                return
        if number_only:
            return self.exb_number

        if new:
            exb_numbers = [part.exb(number_only=True) for part in Part.query.all()]
            self.exb_number = helper.array_max_val(exb_numbers, current_user.division)+1
            db.session.commit()
        return "EXB%06d" % self.exb_number

    def same_exb(self):
        if self.exb_number:
            ret = Part.query.filter_by(exb_number=self.exb_number).all()
            return ret
        else:
            return []
    def link(self):  # required for use with "History" Table
        return url_for('show_part', ids=self.ids)

    def description(self, human=False):
        if human:
            ret = "{0}::IDS:{1} ".format(self.part_type.name, self.ids)
            for key in self.part_type.args():
                try:
                    ret+="{0}:{1}; ".format(key, self.args()[key])
                except KeyError as e:
                    self.args(attr=key, val="")
                finally:
                    pass
                    # ret+="{0}:{1}; ".format(key, self.args()[key])
            return ret
                    
        else:
            if self.exb_number:
                return """PartType:{part_type};{json_attributes};EXB:{exb_number};
                      EXB:{exb_nr_no};
                      out:{out};recommended:{recommended};IDS:{ids}""".format(
                          part_type=self.part_type.name,
                          json_attributes=self.ref_json(),
                          exb_number=self.exb(),
                          out=self.out or False,
                          recommended=self.recommended,
                          ids=self.ids,
                          exb_nr_no=self.exb(number_only=True)
                      )
            else:
                return """PartType:{part_type};{json_attributes};EXB:{exb_number};
                          EXB:{exb_nr_no};
                          out:{out};recommended:{recommended};IDS:{ids}""".format(
                              part_type=self.part_type.name,
                            json_attributes=self.ref_json(),
                            exb_number=self.exb(),
                            out=self.out or False,
                            recommended=self.recommended,
                            ids=self.ids,
                            exb_nr_no=self.exb(number_only=True)
                        )

    def reduce(self):
        return self.description()

    def ref_json(self):
        data = json.loads(self.json_attributes)
        ret = ""
        for k in self.part_type.args():
            if k in data.keys():
                ret += """{key}:{value};""".format(key=k, value=data[k])
        return ret

    def args(self, attr=None, val=None, delete=False):
        attributes = json.loads(self.json_attributes)
        if attr and attr in self.part_type.args():
            if delete and attr:
                val = attributes[attr]
                attributes.pop(attr)
                flash("value \"{}\" was deleted".format(val), "success")
            else:
                try:
                    if not val[0] == "0":
                        val = float(val)
                except:
                    pass
                attributes[attr] = val
                flash("value was set", "success")
            self.json_attributes = json.dumps(attributes)
            db.session.commit()
        elif attr and attr not in self.part_type.args():
            flash("The Key is not available", "warning")
            return
        return attributes

    def messages(self):
        if (self.available() - self.recommended) < 0:
            flash("The available parts are lower than the recommended value.",
                  "warning")
        # if out:
        #     flash("The part is in Use, therefore unavailable for now.",
        #           "danger")

    def available(self):
        p = 0
        for res in filter(lambda k: k.deprecated is False, self.reservations):
            p += res.number
        return self.in_stock()-p

    def in_stock(self):
        r = 0
        for container in self.containers:
            r += container.in_stock()
        return r

    def ordered(self):
        o = 0
        for order in filter(lambda k: k.deprecated is False, self.orders):
            o += order.number
        return o

    def order(self, number, process=None):
        if not process:
            process = Process()
        order = Order()
        order.number = number
        db.session.add(process)
        db.session.add(order)
        process.orders.append(order)
        self.orders.append(order)
        db.session.commit()

    def reserve(self, duedate, number, process=None):
        if not process:
            process = Process()
        reservation = Reservation(duedate)
        reservation.number = number
        db.session.add(process)
        db.session.add(reservation)
        process.reservations.append(reservation)
        self.reservations.append(reservation)
        db.session.commit()

    def take(self, count):
        # if self.out:
        #     flash("""Part is out right now. It is impossible to take it. 
        #     The action will be cancelled.""", "danger")
        #     return False
        if count > self.available():
            flash("""<h4>You cannot take what isn't there.
                  </h4>\nNothing was done.""", "warning")
            return False
        taking_process = Process()
        db.session.add(taking_process)
        containers = helper.recommend_containers(self, count)
        for c, a in containers:
            b = Booking()
            b.number = -a
            db.session.add(b)
            taking_process.bookings.append(b)
            c._bookings.append(b)
        db.session.commit()
        return containers

    def stocktaking(self, container_id, count):
        container = Container.query.get(container_id)
        for booking in container._bookings:
            if booking.floating:
                booking.deprecated = True
        stocktaking_process = Process()
        b = Booking()
        b.number = count
        db.session.add(stocktaking_process)
        db.session.add(b)
        stocktaking_process.bookings.append(b)
        container._bookings.append(b)
        db.session.commit()

    def last_active_reservations(self):
        return sorted(list(filter(lambda k: k.deprecated is False, self.reservations)), key=lambda e: e.duedate)

    def print_label(self):
        if app.config["TESTING"]:
            return
        data = dict(
            QR="IDS{}".format(self.ids),
            HEAD="IDS{}".format(self.ids),
            SUBHEAD="{}".format(self.exb() or self.a5e() or None),
            ARGS=self.args()
        )
        r = requests.post("http://printer_ip_address/print/label/38mm/", data=json.dumps(data))
        if "OK" in r.text:
            flash("Check labelprinter for your label!", "success")
        if "FAIL" in r.text:
            flash("Something may be wrong, check labelprinter for label. You may try again!\n{}".format(r.text), "warning")


class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids')) 
    __place = db.relationship('Place', uselist=False)
    _bookings = db.relationship('Booking', backref='container', uselist=True)
    out = db.Column(db.Boolean)
    fk_place = db.Column(db.Integer, db.ForeignKey("place.id"))

    def __init__(self, out=True):
        self.out = out

    def place(self, place=None, remove=False):
        self.is_empty()
        if place:
            try:
                self.fk_place = place.id
            except Exception as e:
                flash("an error occured in //Container.place()//\n{}".format(e), "danger")
            if self.out:
                self.out = False
            db.session.commit()
        if remove:
            self.fk_place = None
            db.session.commit()
        return self.__place

    def print_label(self):
        self.is_empty()
        if app.config["TESTING"]:
            return
        data = dict(
            QR="IDS{}".format(self.part_ids),
            HEAD="IDS{} @ Container {}".format(self.part_ids,self.id),
            SUBHEAD="{}".format(self.part.exb()),
            ARGS=self.part.args()
        )
        r = requests.post("http://printer_ip_address/print/label/38mm/", data=json.dumps(data))
        if "OK" in r.text:
            flash("Check labelprinter for your label!", "success")
        if "FAIL" in r.text:
            flash("Something may be wrong, check labelprinter for label. You may try again!\n{}".format(r.text), "warning")

        

    def add_pieces(self, number):
        adding_process = Process()
        b = Booking()
        b.number = number
        db.session.add(adding_process)
        db.session.add(b)
        adding_process.bookings.append(b)
        self._bookings.append(b)
        db.session.commit()

    def in_stock(self):
        # self.is_empty()
        r = 0
        for booking in filter(lambda b:  b.deprecated is False, self._bookings):
            r += booking.number
        return r
    
    def stocktaking(self, number):
        self.is_empty()
        for b in self._bookings:
            b.deprecated = True
        stocktaking_process = Process()
        b = Booking()
        b.number = number
        db.session.add(stocktaking_process)
        db.session.add(b)
        stocktaking_process.bookings.append(b)
        self._bookings.append(b)
        db.session.commit()
    
    def is_empty(self):
        if self.in_stock() is 0:
            # self._place = None
            return True
        else:
            return False
        

class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    container = db.relationship("Container", backref="_place", lazy="dynamic", uselist=True)
    
    def print_label(self):
        if app.config["TESTING"]:
            return
        data = dict(
            QR="PLACE{}".format(self.id),
            HEAD="Place {}".format(self.id),
            SUBHEAD="Location: {} @ {}".format(self.room.title, self.room.address),
            ARGS=dict()
        )
        r = requests.post("http://printer_ip_address/print/label/38mm/", data=json.dumps(data))
        if "OK" in r.text:
            flash("Check labelprinter for your label!", "success")
        if "FAIL" in r.text:
            flash("Something may be wrong, check labelprinter for label. You may try again!\n{}".format(r.text), "warning")
    
    def clear(self):
        for container in self.container:
            container.fk_place = None
        db.session.commit()
    
    def link(self):
        return self.room.link()


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    address = db.Column(db.Text)
    places = db.relationship('Place', backref='room', lazy='dynamic',
                             uselist=True)

    def __init__(self, title, address):
        self.title = title
        self.address = address

    def link(self):
        return url_for("show_room", room_id=self.id)

    def reduce(self):
        return "Room;title:{title};address:{address};".format(title=self.title, address=self.address)


class Process(db.Model):
    id = db.Column(db.Integer, primary_key=True)
# start relationships
    reservations = db.relationship(
                                   'Reservation',
                                   backref='process',
                                   lazy='dynamic',
                                   uselist=True
                                   )
    orders = db.relationship(
                             'Order',
                             backref='process',
                             lazy='dynamic',
                             uselist=True
                             )
    bookings = db.relationship(
                             'Booking',
                             backref='process',
                             lazy='dynamic',
                             uselist=True
                             )
    user = db.relationship('User', backref='processes',
                           uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    project = db.relationship(
        "Project",
        backref='process',
        uselist=False
    )
    project_id = db.Column(db.Text, db.ForeignKey("project.project_name"))
# end relationships
    datetime = db.Column(db.DateTime)
    path = db.Column(db.Text)

    def __init__(self, project=None):
        self.user = current_user
        self.datetime = datetime.datetime.now()
        self.path = ""
        if project:
            self.project = project

    def children(self):
        if self.reservations.all():
            return self.reservations
        elif self.orders.all():
            return self.orders
        elif self.bookings.all():
            return self.bookings
        else:
            return list()
    
    def ProcessType(self):
        if self.reservations.all():
            return "Reservation"
        elif self.orders.all():
            return "Order"
        elif self.bookings.all():
            return "Booking"
        else:
            return None

    def GetAmount(self):
        """Returns the amount of reserved Projects. So if there are 12 reserved parts for a Project and 3 are needed for one complete assembly, 4 is returned"""
        val = None
        if not self.project:
            return None
        for child in self.children():
            bom = list(filter(lambda b: b.part_ids is child.part_ids and b.project_id == self.project_id, self.project.bom))
            if len(bom) is 1:
                if not val:
                    val = child.number/bom[0].amount
            elif len(bom) > 1:
                raise Exception("Process.GetAmount(self):: multiple processes open for same project. That should not happen!")
        return val
    
    def GetChildDate(self):
        val = None
        if not self.project or self.ProcessType().lower() != "reservation":
            return None
        for child in self.children():
            bom = list(filter(lambda b: b.part_ids is child.part_ids and b.project_id == self.project_id, self.project.bom))
            if len(bom) is 1:
                if not val:
                    val = child.duedate
                elif val is not child.duedate:
                    raise Exception("Process.GetChildDate(self):: multiple processes open for same project. That should not happen!")
                else:
                    val = child.duedate
                return val
            elif len(bom) > 1:
                raise Exception("Process.GetChildDate(self):: multiple processes open for same project. That should not happen!")
        return val
    
    def EditNumber(self, number):
        if not self.project or self.ProcessType().lower() != "reservation":
            return None
        date = self.GetChildDate()
        for res in self.reservations:
            db.session.delete(res)
        db.session.commit()
        old = self.GetAmount()    
        for bom in self.project.bom:
            bom.reserve(duedate=date, process=self, number=number)

    def delete(self):
        for child in self.children():
            db.session.delete(child)
        db.session.delete(self)
        db.session.commit()
    
    def all_available(self):
        return True
        # TODO: May be useful in the future


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))
    number = db.Column(db.Integer)
    deprecated = db.Column(db.Boolean)

    estimated_arrival = db.Column(db.DateTime)
    floating = db.Column(db.Boolean)  # means no one took care of that

    def __init__(self):
        self.deprecated = False
        self.floating = True

    def user(self):
        return self.process.user

    def book(self, number=None):
        if not number or number is self.number or number == self.number:
            self.deprecated = True
        else:
            self.number = self.number-number  # so a few 
            # were delivered but not all
        db.session.commit()
    
    def ordered(self, number=None):
        self.floating = False
        if number:
            self.number = number
        db.session.commit()

    def delete(self, only=True):
        db.session.delete(self)
        db.session.commit()
        if only:
            flash('Order was removed from the table', "success")


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))
    number = db.Column(db.Integer)
    deprecated = db.Column(db.Boolean)
    project = db.relationship('Project', backref="reservations", uselist=False)
    project_id = db.Column(db.Text, db.ForeignKey('project.project_name'))
    duedate = db.Column(db.DateTime)

    def __init__(self, duedate):
        self.deprecated = False
        self.duedate = duedate

    def user(self):
        return self.process.user

    def book(self, single=False):
        if self.part.available()+self.number < self.number:
            flash("Not enough parts available. Please wait until delivery arrived.", "danger")
            return
        containers = helper.recommend_containers(self.part, self.number)
        for c, a in containers:
            b = Booking()
            b.number = a * (-1)  # negative because of removal
            db.session.add(b)
            c._bookings.append(b)
            # add booking to connected process bookings list
            self.process.bookings.append(b)
        self.process.reservations.remove(self)
        self.deprecated = True
        db.session.commit()
        return containers

    def delete(self):
        process = self.process
        db.session.delete(self)
        db.session.commit()
        if not process.children():
            db.session.delete(process)
            db.session.commit()
            flash('Reservation was removed from the table', "success")
            return True
        return True

    def set_date(self, date):
        self.duedate = date


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'))
    number = db.Column(db.Integer)
    deprecated = db.Column(db.Boolean)
    floating = db.Column(db.Boolean)

    def __init__(self):
        self.deprecated = False
        self.floating = True

    def user(self):
        return self.process.user

    def book(self):  # no more boking possible if already booked
        self.floating = True
        db.session.commit()

    def delete(self, only=True):
        db.session.delete(self)
        db.session.commit()
        if only:
            flash('Booking was removed from the table', "success")


class BOM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    project_id = db.Column(db.Text, db.ForeignKey('project.project_name'))
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))
    project = db.relationship(
                              'Project',
                              backref='bom',
                              uselist=False
                              )
    part = db.relationship(
                           'Part',
                            backref='bom',
                            uselist=False
                           )
                        
    def __init__(self, project, part, amount):
        self.project = project
        self.part = part
        self.amount = amount
       
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        flash("part was removed from bom", "success")

    def reserve(self, number, duedate, process):
        self.part.reserve(duedate, self.amount*number, process)


class PartDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))
    path = db.Column(db.Text)
    description = db.Column(db.Text)
    part = db.relationship("Part", backref="documents", uselist=False)

    def __init__(self, path, part, description=""):
        self.description = description
        self.path = path
        self.part = part

    def name(self):
        only_name = self.path.replace('/','\\').split('\\')
        if len(only_name) > 1:
            return only_name[len(only_name)-1]+" "+str(self.description)
        else:
            return only_name[0]+" "+str(self.description)

    def delete(self):
        db.session.delete(self)
        remove(path.join(UPLOAD_FOLDER, self.name()))
        db.session.commit()
        flash("document was deleted.", "success")


def create_database(test=False):
    if not test:
        eng = db.create_all()
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///static/Database/test_data.sql'
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI