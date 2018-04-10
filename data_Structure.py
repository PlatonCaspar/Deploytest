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
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))

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
            return self.parent().link()+'#comment_id'+str(self.id)

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


# Components from now on
class PartType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    json_attributes = db.Column(db.Text)
    parts = db.relationship('Part', backref="part_type", lazy='dynamic',
                            uselist=True)

    def __init__(name, description=None):
        self.name = name
        self.json_attributes = json.dumps([])
        self.description = ""

    def args(self, attr=None, delete=False):
        attributes = json.loads(self.json_attributes)
        if not attr:
            return attributes
        else if attr and not delete:
            if attr in attributes:
                flash("key is already present. Nothing was changed", "warning")
                return attributes
            attributes.append(attr)
            if attr in attributes:
                flash("key {} was added".format(attr), "success")
        else if attr and delete:
            if attr in attributes:
                attributes.pop(attributes.index(attr))
                flash("key was removed", "success")
        self.json_attributes = json.dumps(attributes)
        db.session.commit()
        return attributes


class Part(db.Model):
    ids = db.Column(db.Integer, primary_key=True)
    part_type_id = db.Column(db.Integer, db.ForeignKey('parttype.id'))
    exb_number = db.Column(db.Integer)
    json_attributes = db.Column(db.Text)
    out = db.Column(db.Boolean)
    recommended = db.Column(db.Integer)

    bookings = db.relationship('Booking',
                               backref='part',
                               lazy='dynamic',
                               uselist=True)
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
    # documents = db.relationship()
    place_rel = db.relationship('Place', backref='part', lazy='dynamic')
    # project

    def __init__(self, part_type_id: int):
        self.json_attributes = json.dumps({})
        PartType.query.get(part_type_id).parts.append(self)
        self.recommended = 0
        self.exb_number = 0

    def link(self):  # required for use with "History" Table
        return url_for('show_part', ids=self.ids)

    def args(self, attr=None, val=None, delete=False):
        attributes = json.loads(self.json_attributes)
        if attr in self.part_type.attributes():
            if delete and attr:
                val = attributes[attr]
                attributes.pop(attr)
                flash("value \"{}\" was deleted".format(val), "success")
            else:
                attributes[attr] = val
                flash("value was set", "success")
            self.json_attributes = json.dumps(attributes)
            db.session.commit()
        else:
            flash("The Key is not available", "warning")
            return
        return attributes

    def messages(self):
        if (self.available() - self.recommended) < 0:
            flash("The available parts are lower than the recommended value.",
                  "warning")
        if out:
            flash("The part is in Use, therefore unavailable for now.",
                  "danger")

    def available(self):
        p = 0
        for res in filter(lambda k: k.deprecated is False, self.reservations):
            p -= res.number
        return self.in_stock()-p

    def in_stock(self):
        r = 0
        for booking in filter(lambda k: k.deprecated is False, self.bookings):
            r += booking.number
        return r

    def order(self, number):
        process = Process()
        order = Order()
        order.number = number
        db.session.add(process)
        db.session.add(order)
        process.orders.append(order)
        self.orders.append(order)
        db.session.commit()

    def reserve(self):
        process = Process()
        reservation = Reservation()
        reservation.number = number
        db.session.add(process)
        db.session.add(reservation)
        process.orders.append(reservation)
        self.orders.append(reservation)
        db.session.commit()

    def take(self):
        if self.out:
            flash("""Part is out right now. It is impossible to take it. 
            The action will be cancelled.""", "danger")
            return False
        stocktaking_process = Process()
        b = Booking()
        b.number = count
        db.session.add(stocktaking_process)
        db.session.add(b)
        stocktaking_process.bookings.append(b)
        self.bookings.append(b)
        db.session.commit()
        return True

    def stocktaking(self, count):
        if self.out:
            flash("""Part is out right now. It is impossible to take it.
            The action will be cancelled.
            Please use the place function to define a new storage Place
            and if neccesary enter the new number of parts in stock.""",
                  "danger")
            return False
        for booking in self.bookings:
            booking.deprecated = True
            booking.floating = False
        stocktaking_process = Process()
        b = Booking()
        b.number = count
        db.session.add(stocktaking_process)
        db.session.add(b)
        stocktaking_process.bookings.append(b)
        self.bookings.append(b)
        db.session.commit()

    def place(self, place_id=None, count=None):
        """Returns the place of the component. If a place id is given,
        the place is changed to the new Place and then returned.
        if Place was out due to booking, out will be set to False.
        """
        if place_id:
            try:
                self.place_rel = Place.query.get(int(place_id))
                if self.out:
                    self.out = False
                    floating = filter(self.bookings, lambda k: k.floating is True)
                    if len(floating) > 1:
                        flash("""There were more open Bookings regarding this Part.
                        Since this should be impossible all open bookings are closed.
                        Please Count the remainig pieces!""", "danger")
                    for f in floating:
                        f.floating = False
                    db.session.commit()
                db.session.commit()
                # if e.g. a new part is stored, the initial amount can be set
                if count:
                    self.stocktaking(count)
            except:
                flash("""An Error occured in part.place
                    \nplace_id: {}""".format(place_id), "danger")
        return self.place_rel


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    address = db.Column(db.Text)
    places = db.relationship('Place', backref='room', lazy='dynamic',
                             uselist=True)

    def __init__(self, title, address):
        self.title = title
        self.address = address


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
    user = db.relationship('User', backref='processes', lazy='dynamic',
                           uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
# end relationships
    datetime = db.Column(db.DateTime)

    def __init__(self):
        self.user = current_user
        self.datetime = datetime.datetime.now()

    def children(self):
        if self.reservations:
            return self.reservations
        elif self.orders:
            return self.orders
        elif self.booking:
            return self.booking
        else:
            flash("""
                    That should not have happened. \n//process.children()//\n
                    Please inform Stefan about this incident
                  """,
                  "warning"
                  )
            return None


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))
    number = db.Column(db.Integer)
    deprecated = db.Column(db.Boolean)

    floating = db.Column(db.Boolean)

    def __init(self)__:
        self.deprecated = False
        self.floating = True

    def user(self):
        return self.process.user

    def book(self):
        b = Booking()
        b.number = self.number
        db.session.add(b)
        # add booking to connected part bookings list
        self.part.bookings.append(b)
        # add booking to connected process bookings list
        self.process.bookings.append(b)
        self.deprecated = True
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

    duedate = db.Column(db.DateTime)

    def __init(self)__:
        self.deprecated = False

    def user(self):
        return self.process.user

    def book(self):
        b = Booking()
        b.number = self.number * (-1)  # negative because of removal
        db.session.add(b)
        # add booking to connected part bookings list
        self.part.bookings.append(b)
        # add booking to connected process bookings list
        self.process.bookings.append(b)
        self.deprecated = True
        self.part.out = True
        db.session.commit()

    def delete(self, only=True):
        db.session.delete(self)
        db.session.commit()
        if only:
            flash('Reservation was removed from the table', "success")


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    part_ids = db.Column(db.Integer, db.ForeignKey('part.ids'))
    number = db.Column(db.Integer)
    deprecated = db.Column(db.Boolean)

    floating = db.Column(db.Boolean)

    def __init(self)__:
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


def create_database(test=False):
    if not test:
        eng = db.create_all()
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///static/Database/test_data.sql'
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

# session = db.sessionmaker(bind=eng)
