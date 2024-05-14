#!/usr/bin/python3
""" Contains class Mission that stores
task objects;
"""
from .base import BaseModel, Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Mission(BaseModel, Base):
    """
    Represents a Mission in the MyTaskMate system.

    Attributes:
        total_tasks (int): The total number of tasks.
        completed_tasks (int): The total number of completed tasks.
        user_id (str): the id of the user who created this mission
    """

    __tablename__ = 'missions'

    active = Column(Boolean, default=True)
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    user_id = Column(String(60), ForeignKey('users.id'), nullable=False)

    tasks = relationship('Task', backref='mission', cascade="delete")
