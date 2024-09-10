"""
original author: Dominik Cedro
created: 2024-08-29
license: ###
description: Data schemas for writing / reading data
"""
from sqlalchemy.orm import Session
from . import models, schemas

# Snake CRUD operations
def get_snake(db: Session, snake_id: int):
    return db.query(models.Snake).filter(models.Snake.id == snake_id).first()

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

def create_message(db: Session, message: schemas.MessageCreate):
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