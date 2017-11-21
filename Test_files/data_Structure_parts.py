from data_Structure import db, User
from os import urandom
from flask_login import current_user
import datetime

packaging_types = [("Cut Tape", "Cut Tape"), ("Reel", "Reel"), ("Tray", "Tray"), ("Tube", "Tube"), ("Bulk", "Bulk")]
component_types = []
booking_types = [("Purchase", "Purchase"), ("Removal", "Removal"), ("Inventory", "Inventory")]


class Exb(db.Model):

    exb_number = db.Column(db.Text, primary_key=True)
    associated_components = db.relationship('Component', backref='associated_components_exb', lazy='dynamic',
                                            uselist=True)

    def __init__(self, exb_number):
        self.exb_number = exb_number


class A5E(db.Model):

    a5e_number = db.Column(db.Text, primary_key=True)
    associated_components_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    associated_components = db.relationship('Component', backref='associated_components_a5e', lazy='dynamic',
                                            uselist=True)

    def __init(self, a5e_number):
        self.a5e_number = a5e_number


class Component(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text)
    value = db.Column(db.Integer)
    unit = db.Column(db.String(10))
    manufacturer = db.Column(db.String)
    packaging_type = db.Column(db.String)
    a5e_numer = db.Column(db.Text, db.ForeignKey('a5e.a5e_number'))
    exb_number = db.Column(db.Text, db.ForeignKey('exb.exb_number'))
    # storage_place = db.Column()


class Documents(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.Text)
    description = db.Column(db.Text)

    def __init__(self, file_path: str, description='None'):
        self.id = id(file_path + str(urandom(5)))
        self.description = description
        self.file_path = file_path


class Booking(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    component = db.relationship('Component', backref='booked_component', uselist=False)
    quantity = db.Column(db.Integer)
    deprecated = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer)
    booking_type = db.Column(db.String)

    def __init__(self, qty: int, booking_type: str):
        self.id = id(str(urandom(15)) + str(qty))
        if booking_type is "Removal":
            self.quantity = (-1) * qty
        else:
            self.quantity = qty

        self.booking_type = booking_type
        self.user_id = int(current_user.uid)
        self.date_time = datetime.datetime.now()

    def date(self):
        if self.date_time:
            return self.date_time.strftime("%d.%m.%Y")
        else:
            return None

    def user(self):
        return db.session.query(User).get(self.user_id)


class Reservation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'))
    component = db.relationship('Component', backref='booked_component', uselist=False)
    quantity = db.Column(db.Integer)
    project_name = db.Column(db.Text, db.ForeignKey('project.project_name'))
    project = db.relationship('Project', backref='reserved_for_project', uselist=False)

    def __init__(self, qty: int):
        self.id = id(str(urandom(15)) + str(qty))
        self.date_time = datetime.datetime.now()
        self.user_id = current_user.uid

    def date(self):

        if self.date_time:
            return self.date_time.strftime("%d.%m.%Y")
        else:
            return None

    def user(self):
        return db.session.query(User).get(self.user_id)

