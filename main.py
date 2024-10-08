"""
original author: Dominik Cedro
created: 2024-07-01
license: GSB 3.0
description: Main script for security setup, endpoint operation and app config
"""
from dotenv import load_dotenv
import os

load_dotenv()

import logging
import jwt
from sqlalchemy import text
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, Request
from fastapi.responses import RedirectResponse
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
from starlette.middleware.cors import CORSMiddleware
from fastapi import Form
from cloudinary.uploader import upload
from icecream import ic

# Security setup
SECRET_KEY = os.getenv("SECRET_HASH_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS setup for traffic with frontend page
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def redirect_to_https(request: Request, call_next):
    if request.url.scheme == "http":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url)
    response = await call_next(request)
    return response

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dependency for db
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Security setup
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

# USER endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

# SNAKE endpoints

async def upload_image(file: UploadFile):
    ic("Reading file content")
    result = await file.read()
    ic("File read success")
    upload_result = upload(result)
    ic("File uploaded to ", upload_result)

    return upload_result['url']

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
        ic("Starting file upload process...")

        file_content = await file.read()  # Ensure the file content is read correctly
        ic("File content read:", file_content[:100])  # Log first 100 bytes of file content

        url = upload(file_content)['url']  # Upload the file content and get the URL
        ic("File uploaded to Cloudinary, URL:", url)

        snake = schemas.SnakeCreate(
            snake_species=snake_species,
            snake_description=snake_description,
            snake_sex=snake_sex,
            snake_image=url
        )
        ic("Creating snake in the database...")

        return crud.create_snake(db=db, snake=snake)
    except Exception as e:
        ic("Error creating snake:", str(e))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating snake: {str(e)}"
        )

@app.get("/snakes/", response_model=List[schemas.Snake])
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

# MESSAGE endpoints
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

# HEALTH CHECK
@app.get("/")
def healthcheck(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "online"}
    except SQLAlchemyError as e:
        logging.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
