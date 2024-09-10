from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import logging
from sqlalchemy import text
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Snake endpoints
@app.post("/snakes/", response_model=schemas.Snake)
def create_snake(snake: schemas.SnakeCreate, db: Session = Depends(get_db)):
    return crud.create_snake(db=db, snake=snake)

@app.get("/snakes/", response_model=list[schemas.Snake])
def read_snakes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    snakes = crud.get_snakes(db, skip=skip, limit=limit)
    return snakes

@app.get("/snakes/{snake_id}", response_model=schemas.Snake)
def read_snake(snake_id: int, db: Session = Depends(get_db)):
    db_snake = crud.get_snake(db, snake_id=snake_id)
    if db_snake is None:
        raise HTTPException(status_code=404, detail="Snake not found")
    return db_snake

@app.delete("/snakes/{snake_id}", response_model=schemas.Snake)
def delete_snake(snake_id: int, db: Session = Depends(get_db)):
    db_snake = crud.delete_snake(db, snake_id=snake_id)
    if db_snake is None:
        raise HTTPException(status_code=404, detail="Snake not found")
    return db_snake

# Message endpoints
@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_message(db=db, message=message)

@app.get("/messages/", response_model=list[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = crud.get_messages(db, skip=skip, limit=limit)
    return messages

@app.get("/messages/{message_id}", response_model=schemas.Message)
def read_message(message_id: int, db: Session = Depends(get_db)):
    db_message = crud.get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

@app.delete("/messages/{message_id}", response_model=schemas.Message)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    db_message = crud.delete_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

@app.get("/healthcheck")
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except SQLAlchemyError as e:
        logging.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")