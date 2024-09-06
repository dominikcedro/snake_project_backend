"""
original author: Dominik Cedro
created: 2024-08-29
license: ###
description: Data models for snake info. It will contain all crucial information.
"""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class Snake(Base):
    __tablename__ = "snakes"

    id = Column(Integer, primary_key=True)
    snake_species = Column(String)
    snake_description = Column(String)
    snake_sex = Column(String) # maybe ENUM?
    snake_image = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    username = Column(String)
    hashed_password = Column(String)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    sender = Column(String)
    body = Column(String)
    title = Column(String)
    datetime = Column(String)





