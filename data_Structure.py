import flask_sqlalchemy
from flask import Flask
from os import urandom, path
from flask import url_for
from passlib.hash import pbkdf2_sha256
from flask_login import current_user, AnonymousUserMixin
from sqlalchemy import MetaData

import json
import datetime
import time



DATA_FOLDER = path.dirname(__file__)
# print(DATA_FOLDER)
# import flask
app = Flask(__name__)
naming_convention = {
    "fk": "fk_%(table_name)s_(column_0_name)s_%(referred_table_name)s"  
}
metadata = MetaData(naming_convention)
SQLALCHEMY_DATABASE_URI = 'sqlite:///static/Database/data.sql'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = flask_sqlalchemy.SQLAlchemy(app)

class Board(db.Model):
    code = db.Column(db.String(500), primary_key=True)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project = db.relationship('Project', backref=db.backref(
        'project_boards_backref', lazy='dynamic'))
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
    

    # , history):
    def __init__(self, code: str, project_name: str, ver: str, stat="init", patch="None"):

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

        # First user logged in must be active!
        if db.session.query(User).all() is None:
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

    def processes(self):
        return Process.query.filter_by(user_id=self.uid).all()


class History(db.Model):
    board_code = db.Column(db.String(500), db.ForeignKey('board.code'))
    id = db.Column(db.Integer, primary_key=True)
    history = db.Column(db.Text)
    edited_by_id = db.Column(db.Text, db.ForeignKey('user.uid'))
    added_by = db.relationship('User', backref=db.backref(
        'added_by_backref', lazy='dynamic'))

    edited_by = db.relationship('User', backref=db.backref(
        'edited_by_backref', lazy='dynamic'))
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


class Project(db.Model):  # //TODO Implement the Project Class and add relationship to Board
    project_name = db.Column(db.Text, primary_key=True)
    project_description = db.Column(db.Text)
    project_default_image_path = db.Column(db.Text, default=None)
    project_boards = db.relationship('Board', backref=db.backref(
        'project_backref', lazy='dynamic', uselist=True))
    sub_projects = db.relationship('Project', lazy='dynamic', uselist=True)
    sub_projects_id = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project_history = db.relationship('History',
                                      backref=db.backref('project_history_backref', lazy='dynamic', uselist=True))
    project_history_id = db.Column(db.Integer, db.ForeignKey('history.id'))
    project_component_id = db.Column(db.Integer, db.ForeignKey('component.id'), name='project_component_id')
    project_components = db.relationship('Component', backref='project_component_bacckref', lazy='dynamic',
                                         uselist=True)
    reservations = db.relationship('Reservation',
                                   backref=db.backref('project_reservations_backref', lazy='dynamic', uselist=True))

    def __init__(self, project_name: str, project_description: str, project_default_image_path: str):
        self.project_name = project_name
        self.project_description = project_description
        self.project_default_image_path = project_default_image_path

    def reduce(self):
        return str(self.project_name)+";"+str(self.project_description.replace("",";"))

# EXB-List from now on


packaging_types = dict([("0", "Cut Tape"), ("1", "Reel"),
                        ("2", "Tray"), ("3", "Tube"), ("4", "Bulk")])

booking_types = dict([("purchase", "Purchase"),
                      ("removal", "Removal"), ("stocktaking", "Stocktaking")])

# be sure to change the categories in the html file as well!
categories = dict(
    [(1, "Diode"), (2, "Transistor"), (3, "Integrated circuit"), (4, "Optoelectronic device"), (5, "Display"),
     (6, "Vacuum Tube"), (7, "Discharge device"), (8,
                                                   "Power source"), (9, "Resistor"), (10, "Capacitor"),
     (11, "Inductor"),
     (12, "Saturable inductor"), (13,
                                  "Transformer"), (14, "Magnetic amplifier (toroid)"),
     (15, "Ferrite impedance, bedas"),
     (16, "Motor / Generator"), (17, "Solenoid"), (18,
                                                   "Loudspeaker / Microphone"), (19, "Memristor"),
     (20, "RC / LC Network"),
     (21, "Transducer, seonsor, detector"), (22,
                                             "Antenna"), (23, "Filter"), (24, "Prototyping aid"),
     (25, "Piezoelectric device, crystal, resonator"),
     (26, "Terminals and Connectors"), (27,
                                        "Cable assembly"), (28, "Switch"), (29, "Protection device"),
     (30, "Mechanical accesories (Heat sink, Fan, etc...)")])
# be sure to change the housings in the html as well!
housings = dict([(0, "NA"), (1, "TO"), (2, "PFM"), (3, "SIP"), (4, "ZIP"), (5, "DIL"), (6, "DIP"),
                 (7, "DPAK/TO"), (8, "SOD"), (9, "DFP"), (10, "TFP"), (11, "QFP"),
                 (12, "QFN (MLF/MFP)"), (13, "SOP"), (14,
                                                      "SOIC"), (15, "SOJ"), (16, "LGA"),
                 (17, "PGA"), (18, "BGA"), (19, "TCP"), (20, "PLCC")])

# String of Chip forms:
chip_forms = "010050201040205040603080509071008120612101411151516081812182520102220231325122515271628241917292031113931401840404320433543494424452745404723482555505727614565617565"

# Units
unit = dict([(0, ""), (1, "Ohm"), (2, "Farad"), (3, "Henry"), (4, "dB")])
# unit scale
scale = dict([(0, ""), (1, "G"), (2, "M"), (3, "k"),
              (4, "m"), (5, "µ"), (6, "n"), (7, "p")])


class Exb(db.Model):
    exb_number = db.Column(db.Text, primary_key=True)
    associated_components_id = db.Column(
        db.Integer, db.ForeignKey('component.id'))
    associated_components = db.relationship('Component', backref='associated_components_exb',
                                            uselist=False)

    def __init__(self, exb_number=None, division=None):

        if exb_number is not None:
            self.exb_number = exb_number

        elif division is not None and exb_number is None:
            if division == 'SDI':
                all_exb_sdi = db.session.query(Exb).filter(
                    Exb.exb_number.contains("EXB01")).all()
                biggest = 0
                for exb in all_exb_sdi:
                    if biggest < int(exb.exb_number.split("EXB01")[1]):
                        biggest = int(exb.exb_number.split("EXB01")[1])
                new_exb_numer_counter = biggest + 1
                self.exb_number = "EXB01" + str(new_exb_numer_counter).zfill(4)
                print(self.exb_number)
            elif division == 'IPE':
                all_exb_ipe = db.session.query(Exb).filter(
                    Exb.exb_number.contains("EXB00")).all()
                biggest = 0
                for exb in all_exb_ipe:
                    if biggest < int(exb.exb_number.split("EXB00")[1]):
                        biggest = int(exb.exb_number.split("EXB00")[1])
                new_exb_numer_counter = biggest + 1
                self.exb_number = "EXB00" + str(new_exb_numer_counter).zfill(4)


class A5E(db.Model):
    # __table_name__ = 'a5e'
    a5e_number = db.Column(db.Text, primary_key=True)
    associated_components_id = db.Column(
        db.Integer, db.ForeignKey('component.id'))
    associated_components = db.relationship('Component', backref='associated_components_a5e',
                                            uselist=False)

    def __init(self, a5e_number):
        self.a5e_number = a5e_number


class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    smd = db.Column(db.Boolean)
    housing_id = db.Column(db.Integer)
    category_id = db.Column(db.Integer)
    manufacturer_id = db.Column(db.Text)
    chip_form_id = db.Column(db.Text)
    value = db.Column(db.Text)
    # unit = db.Column(db.String(10))
    manufacturer = db.Column(db.String)
    packaging_id = db.Column(db.Integer)
    a5e_number = db.relationship(
        'A5E', backref='associated_a5e_number', uselist=False)
    exb_number = db.relationship(
        'Exb', backref='associated_exb_number', uselist=False)
    documents_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    documents = db.relationship(
        'Documents', backref='associated_documents', uselist=True)
    taken_out = db.Column(db.Boolean, default=False)
    # footprint_id = db.Column(db.Integer,db.ForeignKey('documents.id'))
    footprint = db.relationship(
        'Documents', backref='associated_footprint', uselist=False)
    # storage_place = db.Column()

    def __init__(self):
        #self.id = id(str(urandom(10)) + datetime.datetime.now().strftime('%m.%d.%y %H:%M:%S'))
        pass

    def reduced_description(self):
        if self.smd:
            smd = "smd"
        else: 
            smd = ""
        return self.description+";"+self.manufacturer+";"+self.manufacturer_id+";"+self.value+";"+smd+";"+self.housing()+";"+self.category()+";"+self.package()+";"+str(self.chip_form_id)

    def reduce(self):
        return self.reduced_description().replace(" ",";")

    def datasheet(self):
        for d in self.documents:
            if d.document_type == "Datasheet":
                return d
            else:
                return None

    def housing(self):
        return housings[self.housing_id]

    def category(self):
        return categories[self.category_id]

    def package(self):
        return packaging_types[str(self.packaging_id)]

    def stock(self):
        qty_stock = 0
        bookings = Booking.query.filter_by(
            deprecated=False, component_id=self.id, lab=False).all()
        print(str(bookings))
        for booking in bookings:
            if booking.quantity:
                print("booking.quantity is true")
                qty_stock += booking.quantity
                print("qty_stock: " + str(qty_stock))
        return qty_stock

    def reserved(self):
        qty_stock = 0
        bookings = Reservation.query.filter_by(component_id=self.id).all()
        for booking in bookings:
            if booking.quantity:
                qty_stock += booking.quantity
        return qty_stock

    def stock_lab(self):
        qty_lab = 0
        bookings = Booking.query.filter_by(
            deprecated=False, lab=True, component_id=self.id)
        for b in bookings:
            if b.quantity:
                qty_lab += b.quantity
        return qty_lab

    def reservations(self):
        return Reservation.query.filter_by(component_id=self.id).all()

    def orders(self):
        return Order.query.filter_by(component_id=self.id, delivered=False).all()


class Documents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.Text)
    description = db.Column(db.Text)
    document_type = db.Column(db.Text)

    def __init__(self, document_type: str, file_name: str, description='None'):
        #self.id = id(file_name + str(urandom(5)))
        self.description = description
        self.file_name = file_name
        self.document_type = document_type


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    component = db.relationship(
        'Component', backref='booked_component', uselist=False)
    quantity = db.Column(db.Integer)
    deprecated = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)
    user_mail = db.Column(db.Text)
    booking_type = db.Column(db.String)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project = db.relationship(
        'Project', backref='booked_for_project', uselist=False)
    lab = db.Column(db.Boolean, default=False)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


    def __init__(self, qty: int, booking_type: str, component=None):
       # self.id = id(str(urandom(15)) + str(qty))
        if booking_type is "Removal" or booking_type is "removal":
            self.quantity = (-1) * qty
        else:
            self.quantity = qty

        self.booking_type = booking_type
        self.user_id = int(current_user.uid)
        self.date_time = datetime.datetime.now()
        self.user_mail = current_user.email
        self.component = component

    def date(self):
        if self.date_time:
            return self.date_time.strftime("%d.%m.%Y")
        else:
            return None

    def user(self):
        if db.session.query(User).get(self.user_id) is not None:
            return db.session.query(User).get(self.user_id)
        else:
            return User(username=str(self.user_id), email=self.user_mail)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)
    user_mail = db.Column(db.Text)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    component = db.relationship(
        'Component', backref='reserved_component', uselist=False)
    quantity = db.Column(db.Integer)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project = db.relationship(
        'Project', backref='reserved_for_project', uselist=False)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))

    def __init__(self, qty: int):
        #self.id = id(str(urandom(15)) + str(qty))
        self.date_time = datetime.datetime.now()
        self.user_id = current_user.uid
        self.user_mail = current_user.email
        self.quantity = qty

    def date(self):

        if self.date_time:
            return self.date_time.strftime("%d.%m.%Y")
        else:
            return None

    def user(self):
        if db.session.query(User).get(self.user_id) is not None:
            return db.session.query(User).get(self.user_id)
        else:
            return User(username=str(self.user_id), email=self.user_mail)
            # moved to db_migrate
            # eng = db.create_all()
            # create_databases()

    def book(self):
        booking = Booking(component=self.component,
                          qty=self.quantity, booking_type='removal')
        self.component.taken_out = True
        db.session.add(booking)
        db.session.commit()
        return booking


class Process(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    bookings = db.relationship(
        'Booking', backref='process_bookings', lazy='dynamic', uselist=True)
    #reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'))
    reservations = db.relationship(
        'Reservation', backref='process_reservations', lazy='dynamic', uselist=True)
    #order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    orders = db.relationship(
        'Order', backref='processs_order', lazy='dynamic', uselist=True)
    date_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)
    user_mail = db.Column(db.Text)
    description = db.Column(db.Text)

    def __init__(self, description=None):
        self.date_time = datetime.datetime.now()
        self.user_id = current_user.uid
        self.user_mail = current_user.email
        if description:
            self.description = description
        else:
            self.description = current_user.username + \
                ": Process " + self.date_time.strftime("%d.%m.%y")

    def book(self):
        for r in self.data(booking=True):
            self.bookings.append(r.book())
            if self.reservations.all():
                db.session.delete(r)
                db.session.commit()
            elif self.orders.all():
                r.delivered = True
                db.session.commit()

    def data(self, booking=False, hide_delivered=False):
        if self.reservations.all():
            print("Reservations: " + str(self.reservations.all()))
            return self.reservations.all()
        elif self.bookings.all():
            if booking:
                return None
            return self.bookings.all()
        elif self.orders.all():
            if hide_delivered:
                return self.orders.filter_by(delivered=False).all()
            else:
                return self.orders.all()
        else:
            return None

    def user(self):
        user = User.query.get(self.user_id)
        if user:
            return user 
        else:
            return User(username=self.user_mail, email=self.user_mail)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    component = db.relationship(
        'Component', backref='ordered_component', uselist=False)
    booking_type = db.Column(db.Text)
    delivered = db.Column(db.Boolean, default=False)
    date_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.uid'))
    user = db.relationship('User', backref='ordering_user', uselist=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))


    def __init__(self, component, qty: int, description=None):
        self.date_time = datetime.datetime.now()
        self.booking_type = "Order"
        if description:
            self.description = description
        else:
            self.description = current_user.username + \
                ": Order " + self.date_time.strftime("%d.%m.%y")
        self.user = current_user
        self.component = component
        self.quantity = qty

    def date(self):

        if self.date_time:
            return self.date_time.strftime("%d.%m.%Y")
        else:
            return None

    def confirm(self, quantity=None):
        if not quantity:
            quantity = self.quantity

        description = "Delivery Confirmed qty: " + str(quantity)
        p = Process(description=description)
        b = Booking(qty=int(quantity), booking_type='purchase',
                    component=self.component)
        p.component = b
        db.session.add(p)
        db.session.add(b)
        db.session.commit()

    def book(self, quantity=None):
        if not quantity:
            quantity=self.quantity
            self.delivered = True
        elif quantity is self.quantity:
            self.delivered = True
        else:
            self.quantity -= quantity
        booking = Booking(component=self.component,
                          qty=quantity, booking_type='Purchase')
        db.session.add(booking)
        db.session.commit()
        return booking

db.create_all()
# if not path.exists(SQLALCHEMY_MIGRATE_REPO):
#    api.create(SQLALCHEMY_MIGRATE_REPO, 'database_repository')
#    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# else:
#    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))
# api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# print('Current database version: ' + str(v))

# session = flask_sqlalchemy.SQLAlchemy.(bind=eng)
