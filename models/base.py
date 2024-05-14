#!/usr/bin/python3
""" Contains class Base """
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime
from uuid import uuid4

Base = declarative_base()


class BaseModel(Base):
    """
        Represents the Base Model that all classes inherit from.

        Attributes:
            id (str): The unique identifier for an obj.
            created_at (str): The datetime of creation.
            updated_at (str): The datetime of last update.
    """
    __abstract__ = True

    id = Column(String(60), primary_key=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    def __init__(self, *args, **kwargs):
        datetime_now = datetime.utcnow()
        if not kwargs.get('id'):
            kwargs['id'] = str(uuid4())
        if not kwargs.get('created_at'):
            kwargs['created_at'] = str(datetime_now)
        if not kwargs.get('updated_at'):
            kwargs['updated_at'] = str(datetime_now)
        super().__init__(*args, **kwargs)

    def to_dict(self):
        obj = dict(self.__dict__).copy()
        for k, v in obj.items():
            if k == '_sa_instance_state':
                obj.pop(k)
                break
        for k in obj.keys():
            if k == 'created_at' or k == 'updated_at':
                obj[k] = str(obj[k])
        return obj

    def delete(self):
        from models import storage
        storage.delete(self)

    def __str__(self):
        key = f"{self.__class__.__name__}.{self.id} "
        obj_dict = self.to_dict()
        return key + f"{obj_dict}"
