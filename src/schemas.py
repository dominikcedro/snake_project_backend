"""
original author: Dominik Cedro
created: 2024-08-29
license: ###
description: Data schemas for writing / reading data
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SnakeBase(BaseModel):
    snake_species: str
    snake_description: str
    snake_sex: str
    snake_image: Optional[str] = None

class SnakeCreate(SnakeBase):
    pass

class Snake(SnakeBase):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    sender: str
    body: str
    title: str
    datetime: Optional[datetime] = None

from pydantic import Field

class MessageCreate(MessageBase):
    datetime: Optional[datetime] = None

class Message(MessageBase):
    id: int
    datetime: datetime  # Ensure datetime is of type datetime

    class Config:
        orm_mode = True