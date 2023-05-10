# Description: This file contains the models for the database.
# from .dbcon import db
# from datetime import datetime


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     username = db.Column(db.String(200), unique=True, nullable=False)
#     fullname = db.Column(db.String(200), nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     refresh_token = db.Column(db.String(1000))
#     date_joined = db.Column(db.DateTime, nullable=False,
#                             default=datetime.utcnow)


# class Pins(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     body = db.Column(db.Text, nullable=False)
#     image = db.Column(db.String(255), nullable=True)
#     date_posted = db.Column(db.DateTime, nullable=False,
#                             default=datetime.utcnow)
#     updated_date = db.Column(db.DateTime, nullable=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     author = db.relationship('User', backref='pins', lazy=True)


from .dbcon import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    username = Column(String(200), unique=True, nullable=False)
    fullname = Column(String(200), nullable=False)
    password = Column(String(200), nullable=False)
    refresh_token = Column(String(1000))
    date_joined = Column(DateTime, nullable=False,
                         default=datetime.utcnow)


class Pins(Base):
    __tablename__ = 'pins'

    pin_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    body = Column(Text, nullable=False)
    image = Column(String(255), nullable=True)
    date_posted = Column(DateTime, nullable=False,
                         default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    author = relationship('User', backref='pins', lazy=True)
