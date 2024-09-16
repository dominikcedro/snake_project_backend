from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from a .env file

import logging

import jwt
from sqlalchemy import text
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Annotated, List
import models
import crud
import schemas
from cloudinary.uploader import upload_image, destroy
from database import SessionLocal, engine
from models import User
from fastapi import File


# Secret key to encode JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS settings
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = crud.get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user(db, username=form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)


from fastapi import Form

@app.post("/snakes/", response_model=schemas.Snake)
async def create_snake(
    snake_species: str = Form(...),
    snake_description: str = Form(...),
    snake_sex: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Upload the image and get the URL
        url = await upload_image(file)
        # Create the snake object with the image URL
        snake = schemas.SnakeCreate(
            snake_species=snake_species,
            snake_description=snake_description,
            snake_sex=snake_sex,
            snake_image=url
        )
        # Create the snake in the database
        return crud.create_snake(db=db, snake=snake)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating snake: {str(e)}"
        )

@app.get("/snakes/", response_model=List[schemas.Snake]) # implemented pagination for "view more" button
def get_snakes(skip: int = 0, limit: int = 6, db: Session = Depends(get_db)):
    snakes = crud.get_all_snakes(db, skip=skip, limit=limit)
    return snakes

@app.get("/snakes/{snake_id}", response_model=schemas.Snake)
def get_snake_by_id(snake_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_snake = crud.get_snake(db, snake_id=snake_id)
    if db_snake is None:
        raise HTTPException(status_code=404, detail="Snake not found")
    return db_snake




@app.delete("/snakes/{snake_id}", response_model=schemas.Snake)
def delete_snake(snake_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_snake = crud.get_snake(db, snake_id=snake_id)
    if db_snake is None:
        raise HTTPException(status_code=404, detail="Snake not found")

    # Delete the image from Cloudinary
    try:
        destroy(db_snake.snake_image)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting image from Cloudinary: {str(e)}"
        )

    # Delete the snake from the database
    db_snake = crud.delete_snake(db, snake_id=snake_id)
    return db_snake

@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_message(db=db, message=message)

@app.get("/messages/", response_model=list[schemas.Message])
def read_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    messages = crud.get_all_messages(db)
    return messages

@app.get("/messages/{message_id}", response_model=schemas.Message)
def read_message(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_message = crud.get_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

@app.delete("/messages/{message_id}", response_model=schemas.Message)
def delete_message(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_message = crud.delete_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message
@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@app.get("/healthcheckkkk")
def healthcheck(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except SQLAlchemyError as e:
        logging.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")


@app.post("/upload")
async def handle_upload(file: UploadFile, db: Session = Depends(get_db)):
    try:
        url = await upload_image(file)
        return {
            "data": {
                "url": url
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading images: {str(e)}"
        )