#!/usr/bin/python3
""" Contains class User """
from sqlalchemy import Column, String, Boolean
from models.base import BaseModel, Base
from sqlalchemy.orm import relationship
from flask_login import UserMixin


class User(BaseModel, Base, UserMixin):
    """
    Represents a User in the MyTaskMate system.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
    """

    __tablename__ = 'users'

    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(30), nullable=False)

    missions = relationship('Mission', backref='user', cascade="delete")
