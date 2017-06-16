import flask_sqlalchemy
from flask import Flask
from os import urandom, path
from flask import url_for
import time
from passlib.hash import pbkdf2_sha256
from flask_login import current_user, AnonymousUserMixin
from migrate.versioning import api

import datetime

DATA_FOLDER = path.dirname(__file__)
# print(DATA_FOLDER)
# import flask
app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///static/Database/data.sql'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
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
        #self.id = id(time.strftime("%d.%m.%Y %H:%M:%S") + board_code + str(current_user.uid) + str(urandom(5)))


class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.Text)
    description = db.Column(db.Text)
    belongs_to_history_id = db.Column(db.Integer, db.ForeignKey('history.id'))
    belongs_to_history = db.relationship('History',
                                         backref=db.backref('data_objects_backref', lazy='dynamic', uselist=True))

    def __init__(self, history, file_path: str, description='None'):
        self.belongs_to_history = history
        #self.id = id(file_path)
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
    project_component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    project_components = db.relationship('Component', backref='project_component_bacckref', lazy='dynamic',
                                         uselist=True)
    reservations = db.relationship('Reservation',
                                   backref=db.backref('project_reservations_backref', lazy='dynamic', uselist=True))

    def __init__(self, project_name: str, project_description: str, project_default_image_path: str):
        self.project_name = project_name
        self.project_description = project_description
        self.project_default_image_path = project_default_image_path


##EXB-List from now on


packaging_types = dict([("0", "Cut Tape"), ("1", "Reel"), ("2", "Tray"), ("3", "Tube"), ("4", "Bulk")])

booking_types = dict([("purchase", "Purchase"), ("removal", "Removal"), ("stocktaking", "Stocktaking")])

# be sure to change the categories in the html file as well!
categories = dict(
    [(1, "Diode"), (2, "Transistor"), (3, "Integrated circuit"), (4, "Optoelectronic device"), (5, "Display"),
     (6, "Vacuum Tube"), (7, "Discharge device"), (8, "Power source"), (9, "Resistor"), (10, "Capacitor"),
     (11, "Inductor"),
     (12, "Saturable inductor"), (13, "Transformer"), (14, "Magnetic amplifier (toroid)"),
     (15, "Ferrite impedance, bedas"),
     (16, "Motor / Generator"), (17, "Solenoid"), (18, "Loudspeaker / Microphone"), (19, "Memristor"),
     (20, "RC / LC Network"),
     (21, "Transducer, seonsor, detector"), (22, "Antenna"), (23, "Filter"), (24, "Prototyping aid"),
     (25, "Piezoelectric device, crystal, resonator"),
     (26, "Terminals and Connectors"), (27, "Cable assembly"), (28, "Switch"), (29, "Protection device"),
     (30, "Mechanical accesories (Heat sink, Fan, etc...)")])
# be sure to change the housings in the html as well!
housings = dict([(0, "NA"), (1, "TO"), (2, "PFM"), (3, "SIP"), (4, "ZIP"), (5, "DIL"), (6, "DIP"),
                 (7, "DPAK/TO"), (8, "SOD"), (9, "DFP"), (10, "TFP"), (11, "QFP"),
                 (12, "QFN (MLF/MFP)"), (13, "SOP"), (14, "SOIC"), (15, "SOJ"), (16, "LGA"),
                 (17, "PGA"), (18, "BGA"), (19, "TCP"), (20, "PLCC")])

# String of Chip forms:
chip_forms = "010050201040205040603080509071008120612101411151516081812182520102220231325122515271628241917292031113931401840404320433543494424452745404723482555505727614565617565"

# Units
unit = dict([(0, ""), (1, "Ohm"), (2, "Farad"), (3, "Henry"), (4, "dB")])
# unit scale
scale = dict([(0, ""), (1, "G"), (2, "M"), (3, "k"), (4, "m"), (5, "µ"), (6, "n"), (7, "p")])


class Exb(db.Model):
    exb_number = db.Column(db.Text, primary_key=True)
    associated_components_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    associated_components = db.relationship('Component', backref='associated_components_exb',
                                            uselist=False)

    def __init__(self, exb_number=None, division=None):

        if exb_number is not None:
            self.exb_number = exb_number

        elif division is not None and exb_number is None:
            if division == 'SDI':
                all_exb_sdi = db.session.query(Exb).filter(Exb.exb_number.contains("EXB01")).all()
                biggest = 0
                for exb in all_exb_sdi:
                    if biggest < int(exb.exb_number.split("EXB01")[1]):
                        biggest = int(exb.exb_number.split("EXB01")[1])
                new_exb_numer_counter = biggest + 1
                self.exb_number = "EXB01" + str(new_exb_numer_counter).zfill(4)
                print(self.exb_number)
            elif division == 'IPE':
                all_exb_ipe = db.session.query(Exb).filter(Exb.exb_number.contains("EXB00")).all()
                biggest = 0
                for exb in all_exb_ipe:
                    if biggest < int(exb.exb_number.split("EXB00")[1]):
                        biggest = int(exb.exb_number.split("EXB00")[1])
                new_exb_numer_counter = biggest + 1
                self.exb_number = "EXB00" + str(new_exb_numer_counter).zfill(4)


class A5E(db.Model):
    # __table_name__ = 'a5e'
    a5e_number = db.Column(db.Text, primary_key=True)
    associated_components_id = db.Column(db.Integer, db.ForeignKey('component.id'))
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
    a5e_number = db.relationship('A5E', backref='associated_a5e_number', uselist=False)
    exb_number = db.relationship('Exb', backref='associated_exb_number', uselist=False)
    documents_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    documents = db.relationship('Documents', backref='associated_documents', uselist=True)
    taken_out = db.Column(db.Boolean, default=False)
    # footprint_id = db.Column(db.Integer,db.ForeignKey('documents.id'))
    footprint = db.relationship('Documents', backref='associated_footprint', uselist=False)
    # storage_place = db.Column()

    def __init__(self):
        #self.id = id(str(urandom(10)) + datetime.datetime.now().strftime('%m.%d.%y %H:%M:%S'))
        pass

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
            deprecated=False, component_id=self.id).filter_by(lab=False).all()
        for booking in bookings:
            qty_stock += booking.quantity
        return qty_stock

    def reserved(self):
        qty_stock = 0
        bookings = db.session.query(Reservation).join(Component, Component.id == Reservation.component_id).all()
        for booking in bookings:
            qty_stock += booking.quantity
        return qty_stock

    def stock_lab(self):
        qty_lab = 0
        bookings = Booking.query.filter_by(deprecated=False, lab=True, component_id=self.id)
        for b in bookings:
            qty_lab += b.quantity
        return qty_lab


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
    component = db.relationship('Component', backref='booked_component', uselist=False)
    quantity = db.Column(db.Integer)
    deprecated = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)
    user_mail = db.Column(db.Text)
    booking_type = db.Column(db.String)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project = db.relationship('Project', backref='booked_for_project', uselist=False)
    lab = db.Column(db.Boolean, default=False)

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
    component = db.relationship('Component', backref='reserved_component', uselist=False)
    quantity = db.Column(db.Integer)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project = db.relationship('Project', backref='reserved_for_project', uselist=False)

    def __init__(self, qty: int):
        #self.id = id(str(urandom(15)) + str(qty))
        self.date_time = datetime.datetime.now()
        self.user_id = current_user.uid
        self.user_mail = current_user.email

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

        def book (self):
            booking = Booking(self.component, self.quantity, 'removal')
            db.session.add(booking)
            db.session.commit()
            return booking



class Process(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
     bookings = db.relationship('Booking', backref='process_bookings', lazy='dynamic', uselist=True)
     reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'))
     reservations = db.relationship('Reservation', backref='process_reservations', lazy='dynamic', uselist=True)
     date_time = db.Column(db.DateTime)
     user_id = db.Column(db.Integer)
     user_mail = db.Column(db.Text)
    
     def __init__(self):
        self.date_time = datetime.datetime.now()
        self.user_id = current_user.uid
        self.user_mail = current_user.email

     def book(self):
        for r in self.reservations:
            self.bookings+=r.book()
            db.session.delete(r)
            db.session.commit()


    



SQLALCHEMY_MIGRATE_REPO = path.join(DATA_FOLDER, "static/Database")


# v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
# tmp_module = imp.new_module('old_model')
# old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# exec(old_model, tmp_module.__dict__)
# script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
# open(migration, "wt").write(script)
# api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
# print('New migration saved as ' + migration)
# print('Current database version: ' + str(v))


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
