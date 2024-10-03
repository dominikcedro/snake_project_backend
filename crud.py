"""
original author: Dominik Cedro
created: 2024-08-29
license: BSD 3.0
description: functions for handling CRUD operations on mySQL DB
"""
from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Snake CRUD operations
def get_snake(db: Session, snake_id: int):
    return db.query(models.Snake).filter(models.Snake.id == snake_id).first()

def get_all_snakes(db: Session, skip: int = 0, limit: int = 6):
    return db.query(models.Snake).offset(skip).limit(limit).all()

def create_snake(db: Session, snake: schemas.SnakeCreate):
    db_snake = models.Snake(
        snake_species=snake.snake_species,
        snake_description=snake.snake_description,
        snake_sex=snake.snake_sex,
        snake_image=snake.snake_image
    )

    db.add(db_snake)
    db.commit()
    db.refresh(db_snake)
    return db_snake

def delete_snake(db: Session, snake_id: int):
    db_snake = db.query(models.Snake).filter(models.Snake.id == snake_id).first()
    if db_snake:
        db.delete(db_snake)
        db.commit()
    return db_snake

# Message CRUD operations
def get_message(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.id == message_id).first()

def get_all_messages(db: Session):
    return db.query(models.Message).all()

def create_message(db: Session, message: schemas.MessageCreate):
    if message.datetime is None:
        message.datetime = datetime.utcnow()
    db_message = models.Message(
        sender=message.sender,
        body=message.body,
        title=message.title,
        datetime=message.datetime
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def delete_message(db: Session, message_id: int):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        disabled=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

