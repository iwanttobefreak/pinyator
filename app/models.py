from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(200), nullable=True)
    photo = db.Column(db.String(500), nullable=True)
    height = db.Column(db.Integer, nullable=True)
    arm_height = db.Column(db.Integer, nullable=True)
    role = db.Column(db.String(20), nullable=False, default='casteller')
    position = db.Column(db.String(30), nullable=True)

    attendances = db.relationship('Attendance', backref='user', lazy=True)
    assignments = db.relationship('EventCastellAssignment', backref='user', lazy=True)

    def is_admin(self):
        return self.role == 'admin'

    def is_cap(self):
        return self.role in ('admin', 'cap')

    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)

    attendances = db.relationship('Attendance', backref='event', lazy=True)
    castells = db.relationship('EventCastell', backref='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.title}>'


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id'),)

    def __repr__(self):
        return f'<Attendance {self.user_id} {self.event_id} {self.status}>'


class CastellTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)

    positions = db.relationship('CastellPosition', backref='template',
                                lazy=True, order_by='CastellPosition.y',
                                cascade='all, delete-orphan')

    def __repr__(self):
        return f'<CastellTemplate {self.name}>'


class CastellPosition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('castell_template.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    x = db.Column(db.Integer, nullable=False, default=0)
    y = db.Column(db.Integer, nullable=False, default=0)
    w = db.Column(db.Integer, nullable=False, default=80)
    h = db.Column(db.Integer, nullable=False, default=30)
    angle = db.Column(db.Integer, nullable=False, default=0)
    shape = db.Column(db.Integer, nullable=False, default=0)
    color = db.Column(db.String(7), nullable=True)
    text_color = db.Column(db.String(7), nullable=True)

    assignments = db.relationship('EventCastellAssignment', backref='position', lazy=True)

    def __repr__(self):
        return f'<CastellPosition {self.name}>'


class EventCastell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('castell_template.id'), nullable=False)
    name = db.Column(db.String(100), nullable=True)

    template = db.relationship('CastellTemplate')
    assignments = db.relationship('EventCastellAssignment', backref='event_castell',
                                  lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<EventCastell {self.id}>'


class RoleDefaults(db.Model):
    __tablename__ = 'role_defaults'
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(30), unique=True, nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), nullable=False, default='#cfe2f3')
    text_color = db.Column(db.String(7), nullable=True)

    def __repr__(self):
        return f'<RoleDefaults {self.role}>'


class EventCastellAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_castell_id = db.Column(db.Integer, db.ForeignKey('event_castell.id'), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('castell_position.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    __table_args__ = (db.UniqueConstraint('event_castell_id', 'position_id'),)

    def __repr__(self):
        return f'<EventCastellAssignment {self.id}>'
