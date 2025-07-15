from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from datetime import datetime
from config import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(Enum('male', 'female', name='gender_status'), nullable=False)
    county = db.Column(db.String(50))
    town = db.Column(db.String(50))
    registration_level = db.Column(
        Enum('basic', 'details', 'completed', name='registration_stage'),
        default='basic'
    )
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    details = db.relationship('UserDetail', back_populates='user', uselist=False)
    match_requests = db.relationship('MatchRequest', backref='user', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='receiver', lazy=True)

    def __repr__(self):
        return f'<User {self.name} - {self.phone_number}>'


class UserDetail(db.Model):
    __tablename__ = 'user_details'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    education_level = db.Column(db.String(50))
    profession = db.Column(db.String(50))
    marital_status = db.Column(Enum('single', 'married', 'divorced', name='marital_status_enum'))
    ethnicity = db.Column(db.String(50))
    religion = db.Column(db.String(50))
    self_description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user = db.relationship('User', back_populates='details')

    def __repr__(self):
        return f'<UserDetail for User {self.user_id}>'


class MatchRequest(db.Model):
    __tablename__ = 'match_requests'

    match_request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    age_range_start = db.Column(db.Integer)
    age_range_end = db.Column(db.Integer)
    town = db.Column(db.String(50))
    total_matches = db.Column(db.Integer, default=0)
    current_offset = db.Column(db.Integer, default=0)
    matches_per_page = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    matches = db.relationship('ProfileMatch', backref='match_request', lazy=True)

    def has_more_matches(self):
        return self.current_offset < self.total_matches

    def advance_pagination(self):
        self.current_offset += self.matches_per_page
        db.session.commit()

    def __repr__(self):
        return f'<MatchRequest {self.match_request_id} by User {self.user_id}>'


class ProfileMatch(db.Model):
    __tablename__ = 'profile_match'

    id = db.Column(db.Integer, primary_key=True)
    match_request_id = db.Column(db.Integer, db.ForeignKey('match_requests.match_request_id'), nullable=False)
    matched_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sent = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    matched_user = db.relationship('User', foreign_keys=[matched_user_id])

    def __repr__(self):
        return f'<ProfileMatch {self.id} - User {self.matched_user_id}>'


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    phone_number = db.Column(db.String(15))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Message {self.id} from {self.sender_id} to {self.recipient_id}>'
