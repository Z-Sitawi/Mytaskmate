#!/usr/bin/python3
""" Contains class Task """
from .base import BaseModel, Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy import event


class Task(BaseModel, Base):
    """
        Represents a Task in the MyTaskMate system.

        Attributes:
            title (str): The title of the task.
            mission_id (int): The ID of the mission the task belongs to.
    """

    __tablename__ = 'tasks'

    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)
    mission_id = Column(String(60), ForeignKey('missions.id'), nullable=False)
