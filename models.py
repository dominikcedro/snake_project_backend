"""
original author: Dominik Cedro
created: 2024-07-01
license: GSB 3.0
description: sqlalchemy models for mySQL database
"""
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Boolean, Column, Integer, String
from database import Base

class Snake(Base):
    __tablename__ = "snakes"

    id = Column(Integer, primary_key=True)
    snake_species = Column(String(255))
    snake_description = Column(String(255))
    snake_sex = Column(String(255)) # maybe ENUM?
    snake_image = Column(String(255))



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    # email = Column(String(255), unique=True, index=True, nullable=True)
    # full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255))
    disabled = Column(Boolean, default=False)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    sender = Column(String(255))
    body = Column(String(255))
    title = Column(String(255))
    datetime = Column(DateTime)